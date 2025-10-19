from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Union
import uvicorn
import os
import tempfile
import logging
from resume_parser_v2 import SmartResumeParser
from schemas import ResumeUploadResponse, ResumeData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="Resume Parser API",
    description="An API for parsing resume PDFs and extracting structured data",
    version="1.0.0"
)

# Initialize smart resume parser
resume_parser = SmartResumeParser()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Resume Parser API",
        "version": "1.0.0",
        "endpoints": {
            "POST /parse-resume": "Parse resume PDF and extract structured data",
            "GET /health": "Health check"
        }
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", service="resume-parser")

# Resume parsing endpoint
@app.post("/parse-resume", response_model=ResumeUploadResponse)
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse a resume PDF file and extract structured data.
    
    Args:
        file: PDF file containing the resume
        
    Returns:
        ResumeUploadResponse containing the parsed resume data
    """
    if not file.filename.lower().endswith('.pdf'):
        return ResumeUploadResponse(
            success=False,
            message="Only PDF files are supported",
            error="Invalid file type"
        )
    
    try:
        # Create temporary file to store uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Parse the resume
            logger.info(f"Parsing resume: {file.filename}")
            resume_data = resume_parser.parse_resume(temp_file_path, file.filename)
            
            return ResumeUploadResponse(
                success=True,
                message="Resume parsed successfully",
                resume_data=resume_data
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        return ResumeUploadResponse(
            success=False,
            message="Failed to parse resume",
            error=str(e)
        )

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
