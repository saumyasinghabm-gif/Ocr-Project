from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import sys
from pathlib import Path
from typing import Optional
import uvicorn
from pydantic import BaseModel

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class OCRResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

@app.post("/api/process-ocr", response_model=OCRResponse)
async def process_ocr(file: UploadFile = File(...)):
    # Check file extension
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")

    try:
        # Save the uploaded file temporarily
        temp_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # Process the uploaded file using main.py OCR function
        try:
            # Add the current directory to Python path so we can import main
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))

            # Import the OCR function from main.py
            from main import process_ocr_from_file

            # Call the OCR processing function with the uploaded file path
            ocr_result = process_ocr_from_file(temp_path)

            # Check if extracted.json was created by the OCR process
            extracted_path = Path('extracted.json')
            if extracted_path.exists():
                with open(extracted_path, 'r') as f:
                    result = json.load(f)
            else:
                # If no extracted.json, return the direct OCR result
                result = ocr_result

        except Exception as e:
            result = {
                "error": f"Error processing OCR: {str(e)}",
                "filename": file.filename,
                "status": "error",
                "details": str(e)
            }
            print(f"OCR Processing Error: {e}")

        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {"success": True, "data": result}

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "OCR API is running with FastAPI"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)