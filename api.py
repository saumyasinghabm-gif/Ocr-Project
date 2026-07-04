from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
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

        # Check if extracted.json exists
        extracted_path = Path('extracted.json')
        if extracted_path.exists():
            with open(extracted_path, 'r') as f:
                result = json.load(f)
        else:
            # Return sample data if extracted.json doesn't exist
            result = {
                "invoice_number": "SAMPLE-123",
                "invoice_date": "01-Jul-2026",
                "invoice_type": "Original",
                "seller_details": {
                    "name": "Sample Vendor",
                    "address": "123 Business Street",
                    "tin": "12345678901",
                    "pan": "ABCDE1234F"
                },
                "buyer_details": {
                    "name": "Sample Customer",
                    "pan_it_number": None
                },
                "line_items": [
                    {
                        "s_no": 1,
                        "description": "Sample Product 1 - 500 ML",
                        "quantity": 2.0,
                        "unit": "PCS",
                        "rate": 1000.00,
                        "amount": 2000.00
                    }
                ],
                "summary": {
                    "subtotal_amount": 2000.00,
                    "tcs_payable": None,
                    "round_off_amount": 0.00,
                    "total_quantity": 2.0,
                    "total_amount_words": "Indian Rupees Two Thousand Only",
                    "total_amount_numeric": 2000.00
                },
                "declaration": "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.",
                "notes": ["This is a Computer Generated Invoice"]
            }

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