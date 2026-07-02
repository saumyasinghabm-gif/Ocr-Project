import easyocr
import json

reader = easyocr.Reader(['th','en'], gpu = False)


text = reader.readtext('images/wp.jpeg', detail = 0)
print(text)

# Save the extracted text to a professional JSON structure
def convert_to_serializable(obj):
    if hasattr(obj, 'flatten'):
        return list(map(int, obj.flatten()))
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    elif hasattr(obj, 'item'):
        return int(obj.item())
    else:
        return obj

# Organize OCR results into a clean API-ready structure (key-value pairs only)
def organize_invoice_data(ocr_results):
    invoice_data = {
        "invoice_number": None,
        "invoice_date": None,
        "vendor_name": None,
        "vendor_tax_ids": [],
        "customer_name": None,
        "customer_address": None,
        "items": [],
        "total_amount": None,
        "total_amount_words": None,
        "currency": "INR",
        "processing_metadata": {
            "timestamp": "2026-06-30T13:30:00",
            "language": "thai-english",
            "total_detections": len(ocr_results)
        }
    }

    # Extract key information from OCR results
    for item in ocr_results:
        text = item[1].strip()
        confidence = float(item[2])

        # Clean up text
        clean_text = ' '.join(text.split())

        # Extract invoice header information
        if "invoice" in clean_text.lower() and "no" in clean_text.lower() and invoice_data["invoice_number"] is None:
            invoice_data["invoice_number"] = clean_text.replace("invoice no.", "").strip()
        elif any(month in clean_text.lower() for month in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]) and invoice_data["invoice_date"] is None:
            invoice_data["invoice_date"] = clean_text

        # Extract vendor information
        elif ("tin" in clean_text.lower() or "pan" in clean_text.lower()) and len(clean_text) > 5:
            if clean_text not in invoice_data["vendor_tax_ids"]:
                invoice_data["vendor_tax_ids"].append(clean_text)

        # Extract customer information
        elif any(keyword in clean_text.lower() for keyword in ["fl2", "depot", "lucknow", "ganj"]) and invoice_data["customer_address"] is None:
            invoice_data["customer_address"] = clean_text

        # Extract items (products)
        elif any(keyword in clean_text.lower() for keyword in ["bacardi", "black & white", "dewar's", "smirnoff", "magic moments", "rockford", "vodka", "whisky", "rum", "scotch", "750 ml", "375 ml", "180 ml"]):
            # Check if this is a product description (not just a brand name)
            if len(clean_text.split()) > 2 and ("ml" in clean_text or "l" in clean_text):
                invoice_data["items"].append({
                    "description": clean_text,
                    "confidence": confidence
                })

        # Extract total amounts
        elif "total" in clean_text.lower() and invoice_data["total_amount"] is None:
            invoice_data["total_amount"] = clean_text.replace("total", "").strip()
        elif "rupees" in clean_text.lower() and invoice_data["total_amount_words"] is None:
            invoice_data["total_amount_words"] = clean_text

    # Clean up extracted data
    if invoice_data["vendor_tax_ids"]:
        invoice_data["vendor_tax_ids"] = [tax_id.strip() for tax_id in invoice_data["vendor_tax_ids"]]

    return invoice_data

with open('output/result.json', 'w', encoding='utf-8') as f:
    organized_data = organize_invoice_data(text)
    json.dump(organized_data, f, indent=2, ensure_ascii=False)

print("\nProfessional OCR results saved to output/result.json")
print(f"Total detections: {len(text)}")
print("Data organized into structured invoice format")


