from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import openpyxl
import uvicorn
import os
import shutil
import json
import jwt
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

app = FastAPI(title="Excel Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_FOLDER = "temp_excel"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# JWT configuration (replace with your Auth0 or Firebase config)
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "database": os.getenv("DB_NAME", "dian_saas"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "admin123"),
    "port": os.getenv("DB_PORT", "5432")
}

# JWT Bearer token
security = HTTPBearer()

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except (jwt.InvalidTokenError, jwt.InvalidSignatureError, jwt.DecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def parse_excel_data(filepath: str):
    """Parse Excel file and extract structured data for DIAN compliance"""
    try:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        sheet = wb.active
        
        # Get all rows with data
        rows = []
        for row in sheet.iter_rows(min_row=1, values_only=True):
            # Filter out completely empty rows
            if any(cell is not None and str(cell).strip() for cell in row):
                rows.append([str(cell) if cell is not None else "" for cell in row])
        
        # Validate DIAN format (basic validation)
        if len(rows) < 2:
            raise ValueError("Excel file must contain at least header and one data row")
        
        # Extract header and data
        header = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []
        
        return {
            "header": header,
            "data": data_rows,
            "total_rows": len(data_rows),
            "columns": len(header) if header else 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing Excel file: {str(e)}"
        )

def save_file_metadata(user_id: str, filename: str, file_size: int, row_count: int):
    """Save file metadata to database"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO file_uploads (id, user_id, filename, file_size, row_count, uploaded_at, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                str(uuid.uuid4()),
                user_id,
                filename,
                file_size,
                row_count,
                datetime.utcnow(),
                'parsed'
            ))
            conn.commit()
            result = cur.fetchone()
            return result['id'] if result else None
    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

@app.post("/parse_excel")
async def parse_excel(
    file: UploadFile = File(...),
    token_payload: dict = Depends(verify_token)
):
    """Parse Excel file and return structured data"""
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are supported"
        )
    
    # Save uploaded file
    filepath = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{file.filename}")
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    
    try:
        # Parse Excel data
        parsed_data = parse_excel_data(filepath)
        
        # Save metadata to database
        user_id = token_payload.get("sub", "unknown")
        file_id = save_file_metadata(
            user_id=user_id,
            filename=file.filename,
            file_size=os.path.getsize(filepath),
            row_count=parsed_data["total_rows"]
        )
        
        # Clean up temporary file
        os.remove(filepath)
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "parsed_data": parsed_data,
            "message": f"Successfully parsed {parsed_data['total_rows']} rows from {parsed_data['columns']} columns"
        }
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        raise e

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "excel-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
