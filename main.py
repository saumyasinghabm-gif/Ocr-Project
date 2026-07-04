import json
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from llama_cloud import LlamaCloud

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("LLAMA_CLOUD_API_KEY")
if not api_key:
    raise ValueError("LLAMA_CLOUD_API_KEY environment variable not set")

client = LlamaCloud(api_key=api_key)

# Schema from playground
data_schema = {
    "type": "object",
    "properties": {
        "invoice_number": {
            "description": "The unique identifier for the invoice.",
            "type": "string"
        },
        "invoice_date": {
            "description": "The date when the invoice was issued. Format: DDMon-YYYY (e.g., 15Jun-2026).",
            "type": "string"
        },
        "invoice_type": {
            "description": "The type of invoice, e.g., 'Original'.",
            "anyOf": [{
                "description": "The type of invoice, e.g., 'Original'.",
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "seller_details": {
            "description": "Details of the seller or company issuing the invoice.",
            "type": "object",
            "properties": {
                "name": {
                    "description": "The full name of the seller company.",
                    "type": "string"
                },
                "address": {
                    "description": "The address of the seller company.",
                    "anyOf": [{
                        "description": "The address of the seller company.",
                        "type": "string"
                    }, {
                        "type": "null"
                    }]
                },
                "tin": {
                    "description": "The Taxpayer Identification Number (TIN) of the seller.",
                    "type": "string"
                },
                "pan": {
                    "description": "The Permanent Account Number (PAN) of the seller company.",
                    "type": "string"
                }
            },
            "required": ["name", "address", "tin", "pan"],
            "additionalProperties": False
        },
        "buyer_details": {
            "description": "Details of the buyer or customer receiving the invoice.",
            "type": "object",
            "properties": {
                "name": {
                    "description": "The full name of the buyer or customer.",
                    "type": "string"
                },
                "pan_it_number": {
                    "description": "The PAN or Income Tax number of the buyer, if available.",
                    "anyOf": [{
                        "description": "The PAN or Income Tax number of the buyer, if available.",
                        "type": "string"
                    }, {
                        "type": "null"
                    }]
                }
            },
            "required": ["name", "pan_it_number"],
            "additionalProperties": False
        },
        "line_items": {
            "description": "A list of individual goods or services included in the invoice.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "s_no": {
                        "description": "The serial number of the line item.",
                        "type": "number"
                    },
                    "description": {
                        "description": "A detailed description of the goods or service.",
                        "type": "string"
                    },
                    "quantity": {
                        "description": "The quantity of the item.",
                        "type": "number"
                    },
                    "unit": {
                        "description": "The unit of measurement for the quantity, e.g., 'C.S' (Cases).",
                        "anyOf": [{
                            "description": "The unit of measurement for the quantity, e.g., 'C.S' (Cases).",
                            "type": "string"
                        }, {
                            "type": "null"
                        }]
                    },
                    "rate": {
                        "description": "The unit rate of the item.",
                        "type": "number"
                    },
                    "amount": {
                        "description": "The total amount for this line item (quantity * rate).",
                        "type": "number"
                    }
                },
                "required": ["s_no", "description", "quantity", "unit", "rate", "amount"],
                "additionalProperties": False
            }
        },
        "summary": {
            "description": "Summary of all financial calculations on the invoice.",
            "type": "object",
            "properties": {
                "subtotal_amount": {
                    "description": "The total amount of all line items before taxes and round-off.",
                    "type": "number"
                },
                "tcs_payable": {
                    "description": "Details regarding Tax Collected at Source (TCS) payable.",
                    "anyOf": [{
                        "description": "Details regarding Tax Collected at Source (TCS) payable.",
                        "type": "object",
                        "properties": {
                            "percentage": {
                                "description": "The percentage rate of TCS applied.",
                                "type": "number"
                            },
                            "amount": {
                                "description": "The calculated amount of TCS payable.",
                                "type": "number"
                            }
                        },
                        "required": ["percentage", "amount"],
                        "additionalProperties": False
                    }, {
                        "type": "null"
                    }]
                },
                "round_off_amount": {
                    "description": "The amount rounded off for the final total.",
                    "anyOf": [{
                        "description": "The amount rounded off for the final total.",
                        "type": "number"
                    }, {
                        "type": "null"
                    }]
                },
                "total_quantity": {
                    "description": "The sum of quantities of all items, if available.",
                    "anyOf": [{
                        "description": "The sum of quantities of all items, if available.",
                        "type": "number"
                    }, {
                        "type": "null"
                    }]
                },
                "total_amount_words": {
                    "description": "The total amount chargeable written in words.",
                    "anyOf": [{
                        "description": "The total amount chargeable written in words.",
                        "type": "string"
                    }, {
                        "type": "null"
                    }]
                },
                "total_amount_numeric": {
                    "description": "The final total amount chargeable, including taxes and adjustments.",
                    "type": "number"
                }
            },
            "required": ["subtotal_amount", "tcs_payable", "round_off_amount", "total_quantity", "total_amount_words", "total_amount_numeric"],
            "additionalProperties": False
        },
        "declaration": {
            "description": "Any declaration or legal text provided on the invoice.",
            "anyOf": [{
                "description": "Any declaration or legal text provided on the invoice.",
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "notes": {
            "description": "General notes or statements on the invoice, such as 'This is a Computer Generated Invoice'.",
            "anyOf": [{
                "description": "General notes or statements on the invoice, such as 'This is a Computer Generated Invoice'.",
                "type": "array",
                "items": {
                    "type": "string"
                }
            }, {
                "type": "null"
            }]
        }
    },
    "required": ["invoice_number", "invoice_date", "invoice_type", "seller_details", "buyer_details", "line_items", "summary", "declaration", "notes"],
    "additionalProperties": False
}

# Upload - now accepts file path as parameter
import sys

def process_ocr_from_file(file_path="./document.pdf"):
    try:
        file_obj = client.files.create(file=file_path, purpose="extract")

        # Submit an extract job
        job = client.extract.create(
            file_input=file_obj.id,
            configuration={
                "data_schema": data_schema,
                "tier": "agentic",
                "extraction_target": "per_doc",
                "parse_tier": "agentic",
                "cite_sources": True,
                "confidence_scores": True
            },
        )

        # Poll until the job reaches a terminal state
        while job.status not in ("COMPLETED", "FAILED", "CANCELLED"):
            time.sleep(2)
            job = client.extract.get(job.id)

        if job.status != "COMPLETED":
            raise RuntimeError(f"Extract job {job.id} ended in {job.status}: {job.error_message}")

        # Persist extracted JSON to disk
        Path("extracted.json").write_text(json.dumps(job.extract_result, indent=2))
        print(json.dumps(job.extract_result, indent=2))

        # Per-field citation / confidence metadata
        if job.extract_metadata and job.extract_metadata.field_metadata:
            for field, meta in (job.extract_metadata.field_metadata.document_metadata or {}).items():
                print(f"{field}: {meta}")

        return job.extract_result

    except Exception as e:
        print(f"Error processing OCR: {e}")
        raise

# Main execution
if __name__ == "__main__":
    # Check if a file path was provided as argument
    file_path = sys.argv[1] if len(sys.argv) > 1 else "./document.pdf"
    process_ocr_from_file(file_path)
