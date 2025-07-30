from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from fpdf import FPDF
import uvicorn
import os
import boto3
from datetime import datetime
import jwt
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import json

app = FastAPI(title="PDF Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_FOLDER = "pdfs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# JWT configuration
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

# AWS S3 configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET", "dian-pdf-reports")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

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

def save_pdf_metadata(user_id: str, file_id: str, pdf_filename: str, s3_url: str):
    """Save PDF generation metadata to database"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO pdf_generations (id, user_id, file_id, pdf_filename, s3_url, generated_at, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                str(uuid.uuid4()),
                user_id,
                file_id,
                pdf_filename,
                s3_url,
                datetime.utcnow(),
                'completed'
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

def upload_to_s3(file_path: str, filename: str) -> str:
    """Upload PDF to S3 and return public URL"""
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        s3.upload_file(file_path, S3_BUCKET, filename)
        
        # Return public URL
        return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        
    except Exception as e:
        print(f"S3 upload error: {e}")
        # For development, return a mock URL if S3 is not configured
        return f"mock-s3-url/{filename}"

def generate_dian_pdf(data: dict, filename: str) -> str:
    """Generate DIAN-compliant PDF report"""
    pdf = FPDF()
    pdf.add_page()
    
    # Set up fonts and styling
    pdf.set_font("Arial", "B", 16)

    # Header
    pdf.cell(200, 15, txt="LIBRO MAYOR - FORMATO 1007", ln=True, align="C")
    pdf.cell(200, 10, txt="DIAN - Dirección de Impuestos y Aduanas Nacionales", ln=True, align="C")
    pdf.ln(10)

    # Report metadata
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt=f"Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
    pdf.cell(200, 10, txt=f"Archivo Original: {filename}", ln=True)
    pdf.ln(5)
    
    # Data table
    header = data.get("header", [])
    rows = data.get("data", [])
    
    if header:
        # Table header
        pdf.set_font("Arial", "B", 10)
        col_width = 190 / len(header) if len(header) > 0 else 190
        
        for col in header:
            pdf.cell(col_width, 10, txt=str(col)[:20], border=1, align="C")
        pdf.ln()
        
        # Table data
        pdf.set_font("Arial", "", 9)
        for row in rows[:50]:  # Limit to first 50 rows for preview
            for i, cell in enumerate(row):
                cell_text = str(cell)[:18] if cell else ""
                pdf.cell(col_width, 8, txt=cell_text, border=1, align="L")
            pdf.ln()
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 10, txt=f"Total de registros procesados: {len(rows)}", ln=True)
    pdf.cell(200, 10, txt="Documento generado automáticamente por el sistema", ln=True)
    
    # Save PDF
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    pdf.output(output_path)

    return output_path

@app.post("/generate_pdf")
async def generate_pdf(
    request: Request,
    token_payload: dict = Depends(verify_token)
):
    """Generate DIAN-compliant PDF from Excel data"""
    try:
        body = await request.json()
        
        # Validate required fields
        if "data" not in body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'data' field in request body"
            )
        
        file_id = body.get("file_id", str(uuid.uuid4()))
        filename = body.get("filename", "unknown_file")
        
        # Generate PDF
        pdf_filename = f"libro_mayor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = generate_dian_pdf(body["data"], pdf_filename)
        
        # Upload to S3
        s3_url = upload_to_s3(pdf_path, pdf_filename)
        
        # Save metadata to database
        user_id = token_payload.get("sub", "unknown")
        pdf_id = save_pdf_metadata(user_id, file_id, pdf_filename, s3_url)
        
        return {
            "success": True,
            "pdf_id": pdf_id,
            "pdf_filename": pdf_filename,
            "pdf_url": s3_url,
            "message": "PDF generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}"
        )

@app.get("/download_pdf/{filename}")
async def download_pdf(filename: str):
    """Download generated PDF file"""
    pdf_path = os.path.join(OUTPUT_FOLDER, filename)
    
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found"
        )
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pdf-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
