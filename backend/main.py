from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Union
import uvicorn

# Create FastAPI instance
app = FastAPI(
    title="Number Calculator API",
    description="A simple API for adding two numbers",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class AdditionRequest(BaseModel):
    number1: Union[int, float] = Field(..., description="First number to add")
    number2: Union[int, float] = Field(..., description="Second number to add")

class AdditionResponse(BaseModel):
    result: Union[int, float] = Field(..., description="Sum of the two numbers")
    operation: str = Field(default="addition", description="Type of operation performed")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Number Calculator API",
        "version": "1.0.0",
        "endpoints": {
            "POST /add": "Add two numbers",
            "GET /health": "Health check"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "number-calculator"}

# Addition endpoint
@app.post("/add", response_model=AdditionResponse)
async def add_numbers(request: AdditionRequest):
    """
    Add two numbers and return the result.
    
    Args:
        request: AdditionRequest containing number1 and number2
        
    Returns:
        AdditionResponse containing the sum of the numbers
    """
    try:
        # Perform the addition
        result = request.number1 + request.number2
        
        return AdditionResponse(
            result=result,
            operation="addition"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing calculation: {str(e)}"
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
