from fastapi import FastAPI, HTTPException, Depends, status, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
import httpx
import jwt
import os
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import tempfile
import shutil

app = FastAPI(title="Excel to DIAN Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://frontend:3000",
        "https://excel-dian-1.onrender.com",
        "https://excel-dian-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
EXCEL_SERVICE_URL = os.getenv("EXCEL_SERVICE_URL", "http://excel_service:8001")
PDF_SERVICE_URL = os.getenv("PDF_SERVICE_URL", "http://pdf_service:8002")

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

# JWT Bearer token
security = HTTPBearer()

# Store generated PDFs temporarily
PDF_STORAGE = {}

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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def log_workflow(user_id: str, workflow_type: str, status: str, metadata: dict = None):
    """Log workflow execution to database"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO workflow_logs (id, user_id, workflow_type, status, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                str(uuid.uuid4()),
                user_id,
                workflow_type,
                status,
                json.dumps(metadata) if metadata else None,
                datetime.utcnow()
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Excel service
        async with httpx.AsyncClient() as client:
            excel_response = await client.get(f"{EXCEL_SERVICE_URL}/health")
            pdf_response = await client.get(f"{PDF_SERVICE_URL}/health")
        
        return {
            "status": "healthy",
            "service": "gateway",
            "excel_service": excel_response.status_code == 200,
            "pdf_service": pdf_response.status_code == 200
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "gateway",
            "error": str(e)
        }

@app.post("/process_excel_to_pdf")
async def process_excel_to_pdf(
    request: Request,
    token_payload: dict = Depends(verify_token)
):
    """Complete workflow: Parse Excel and generate PDF"""
    user_id = token_payload.get("sub", "unknown")
    workflow_id = log_workflow(user_id, "excel_to_pdf", "started")
    
    try:
        # Check content type to determine if it's a file upload or JSON
        content_type = request.headers.get("content-type", "")
        
        if "multipart/form-data" in content_type:
            # Handle file upload
            form_data = await request.form()
            file = form_data.get("file")
            
            if not file:
                log_workflow(user_id, "excel_to_pdf", "failed", {"error": "No file provided"})
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No file provided"
                )
            
            # Forward file to Excel service
            async with httpx.AsyncClient() as client:
                files = {"file": (file.filename, file.file, file.content_type)}
                headers = {"Authorization": f"Bearer {request.headers.get('authorization', '').replace('Bearer ', '')}"}
                
                excel_response = await client.post(
                    f"{EXCEL_SERVICE_URL}/parse_excel",
                    files=files,
                    headers=headers
                )
                
                if excel_response.status_code != 200:
                    log_workflow(user_id, "excel_to_pdf", "failed", {"error": "Excel parsing failed"})
                    raise HTTPException(
                        status_code=excel_response.status_code,
                        detail="Excel parsing failed"
                    )
                
                excel_data = excel_response.json()
                
                # Generate PDF from parsed data
                pdf_request = {
                    "data": excel_data["parsed_data"],
                    "file_id": excel_data["file_id"],
                    "filename": excel_data["filename"]
                }
                
                pdf_response = await client.post(
                    f"{PDF_SERVICE_URL}/generate_pdf",
                    json=pdf_request,
                    headers=headers
                )
                
                if pdf_response.status_code != 200:
                    log_workflow(user_id, "excel_to_pdf", "failed", {"error": "PDF generation failed"})
                    raise HTTPException(
                        status_code=pdf_response.status_code,
                        detail="PDF generation failed"
                    )
                
                pdf_data = pdf_response.json()
                
                # Store PDF content for download
                pdf_filename = pdf_data["pdf_filename"]
                pdf_content = await client.get(f"{PDF_SERVICE_URL}/download_pdf/{pdf_filename}")
                
                if pdf_content.status_code == 200:
                    # Store PDF in memory for download
                    pdf_id = str(uuid.uuid4())
                    PDF_STORAGE[pdf_id] = {
                        "content": pdf_content.content,
                        "filename": pdf_filename,
                        "user_id": user_id,
                        "created_at": datetime.utcnow()
                    }
                    download_url = f"/download_pdf/{pdf_id}"
                else:
                    download_url = pdf_data["pdf_url"]
                
                # Log successful workflow
                log_workflow(user_id, "excel_to_pdf", "completed", {
                    "file_id": excel_data["file_id"],
                    "pdf_id": pdf_data["pdf_id"],
                    "download_url": download_url
                })
                
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "excel_data": excel_data,
                    "pdf_url": download_url,
                    "message": "Complete workflow executed successfully"
                }
        else:
            # Handle JSON data (for PDF generation only)
            body = await request.json()
            
            if "data" not in body:
                log_workflow(user_id, "excel_to_pdf", "failed", {"error": "No data provided"})
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No data provided"
                )
            
            # Generate PDF from provided data
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {request.headers.get('authorization', '').replace('Bearer ', '')}"}
                
                pdf_response = await client.post(
                    f"{PDF_SERVICE_URL}/generate_pdf",
                    json=body,
                    headers=headers
                )
                
                if pdf_response.status_code != 200:
                    log_workflow(user_id, "excel_to_pdf", "failed", {"error": "PDF generation failed"})
                    raise HTTPException(
                        status_code=pdf_response.status_code,
                        detail="PDF generation failed"
                    )
                
                pdf_data = pdf_response.json()
                
                # Store PDF content for download
                pdf_filename = pdf_data["pdf_filename"]
                pdf_content = await client.get(f"{PDF_SERVICE_URL}/download_pdf/{pdf_filename}")
                
                if pdf_content.status_code == 200:
                    # Store PDF in memory for download
                    pdf_id = str(uuid.uuid4())
                    PDF_STORAGE[pdf_id] = {
                        "content": pdf_content.content,
                        "filename": pdf_filename,
                        "user_id": user_id,
                        "created_at": datetime.utcnow()
                    }
                    download_url = f"/download_pdf/{pdf_id}"
                else:
                    download_url = pdf_data["pdf_url"]
                
                # Log successful workflow
                log_workflow(user_id, "excel_to_pdf", "completed", {
                    "pdf_id": pdf_data["pdf_id"],
                    "download_url": download_url
                })
                
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "pdf_url": download_url,
                    "message": "PDF generated successfully"
                }
            
    except Exception as e:
        log_workflow(user_id, "excel_to_pdf", "failed", {"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow failed: {str(e)}"
        )

@app.get("/download_pdf/{pdf_id}")
async def download_pdf(
    pdf_id: str,
    token_payload: dict = Depends(verify_token)
):
    """Download generated PDF file"""
    user_id = token_payload.get("sub", "unknown")
    
    if pdf_id not in PDF_STORAGE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    pdf_data = PDF_STORAGE[pdf_id]
    
    # Check if user has access to this PDF
    if pdf_data["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(pdf_data["content"])
    temp_file.close()
    
    # Return file response
    return FileResponse(
        temp_file.name,
        media_type="application/pdf",
        filename=pdf_data["filename"],
        headers={"Content-Disposition": f"attachment; filename={pdf_data['filename']}"}
    )

@app.get("/workflow-history")
async def get_workflow_history(
    token_payload: dict = Depends(verify_token)
):
    """Get user's workflow history"""
    user_id = token_payload.get("sub", "unknown")
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM workflow_logs 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 50
            """, (user_id,))
            
            workflows = cur.fetchall()
            return {
                "workflows": [dict(w) for w in workflows]
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 