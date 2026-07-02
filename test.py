import json
import time
from pathlib import Path
from llama_cloud import LlamaCloud

client = LlamaCloud(api_key="llx-KBNfV8pYNXm82zb5fxeUBokoJ4qJVuieAQFmOD8v6c9O7l1S")

# Schema from playground
data_schema = {
    "type": "object",
    "properties": {
        "invoice_header": {
            "description": "General information about the invoice.",
            "type": "object",
            "properties": {
                "invoice_number": {
                    "description": "The unique identifier for the invoice.",
                    "type": "string"
                },
                "document_type": {
                    "description": "The type of the document, e.g., Original, Copy.",
                    "anyOf": [{
                        "description": "The type of the document, e.g., Original, Copy.",
                        "type": "string"
                    }, {
                        "type": "null"
                    }]
                },
                "invoice_date": {
                    "description": "The date when the invoice was issued. Expected format 'DDMon-YYYY' (e.g., '15Jun-2026').",
                    "type": "string"
                }
            },
            "required": ["invoice_number", "document_type", "invoice_date"],
            "additionalProperties": False
        },
        "sender_details": {
            "description": "Details of the entity sending the invoice.",
            "type": "object",
            "properties": {
                "name": {
                    "description": "The name of the company or individual sending the invoice.",
                    "type": "string"
                },
                "address": {
                    "description": "The address of the sender.",
                    "anyOf": [{
                        "description": "The address of the sender.",
                        "type": "string"
                    }, {
                        "type": "null"
                    }]
                },
                "tin_number": {
                    "description": "Tax Identification Number (TIN) of the sender.",
                    "anyOf": [{
                        "description": "Tax Identification Number (TIN) of the sender.",
                        "type": "string"
                    }, {
                        "type": "null"
                    }]
                },
                "pan_number": {
                    "description": "Permanent Account Number (PAN) of the sender, typically found under 'Company's PAN'.",
                    "anyOf": [{
                        "description": "Permanent Account Number (PAN) of the sender, typically found under 'Company's PAN'.",
                        "type": "string"
                    }, {
                        "type": "null"
                    }]
                }
            },
            "required": ["name", "address", "tin_number", "pan_number"],
            "additionalProperties": False
        },
        "recipient_details": {
            "description": "Details of the entity receiving the invoice.",
            "type": "object",
            "properties": {
                "name": {
                    "description": "The name of the company or individual receiving the invoice.",
                    "type": "string"
                },
                "pan_it_number": {
                    "description": "Permanent Account Number (PAN) or Income Tax number of the recipient.",
                    "anyOf": [{
                        "description": "Permanent Account Number (PAN) or Income Tax number of the recipient.",
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
            "description": "A list of individual items or services included in the invoice.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item_number": {
                        "description": "The sequential number of the item in the invoice.",
                        "type": "integer"
                    },
                    "description": {
                        "description": "A detailed description of the goods or service.",
                        "type": "string"
                    },
                    "quantity": {
                        "description": "The quantity of the item.",
                        "type": "number"
                    },
                    "quantity_unit": {
                        "description": "The unit of measurement for the quantity (e.g., 'C.S' for Cases).",
                        "anyOf": [{
                            "description": "The unit of measurement for the quantity (e.g., 'C.S' for Cases).",
                            "type": "string"
                        }, {
                            "type": "null"
                        }]
                    },
                    "rate": {
                        "description": "The price per unit of the item.",
                        "type": "number"
                    },
                    "rate_unit": {
                        "description": "The unit of measurement for the rate (e.g., 'C.S' for Cases).",
                        "anyOf": [{
                            "description": "The unit of measurement for the rate (e.g., 'C.S' for Cases).",
                            "type": "string"
                        }, {
                            "type": "null"
                        }]
                    },
                    "amount": {
                        "description": "The total amount for this line item (quantity * rate).",
                        "type": "number"
                    }
                },
                "required": ["item_number", "description", "quantity", "quantity_unit", "rate", "rate_unit", "amount"],
                "additionalProperties": False
            }
        },
        "summary": {
            "description": "Summary of financial totals and other aggregated information.",
            "type": "object",
            "properties": {
                "subtotal_amount": {
                    "description": "The sum of all line item amounts before taxes and adjustments.",
                    "type": "number"
                },
                "tcs_payable_on_sale_percentage": {
                    "description": "The percentage of Tax Collected at Source (TCS) applicable on sale.",
                    "anyOf": [{
                        "description": "The percentage of Tax Collected at Source (TCS) applicable on sale.",
                        "type": "number"
                    }, {
                        "type": "null"
                    }]
                },
                "tcs_payable_on_sale_amount": {
                    "description": "The calculated amount of Tax Collected at Source (TCS).",
                    "anyOf": [{
                        "description": "The calculated amount of Tax Collected at Source (TCS).",
                        "type": "number"
                    }, {
                        "type": "null"
                    }]
                },
                "round_off_amount": {
                    "description": "The amount rounded off for the total.",
                    "anyOf": [{
                        "description": "The amount rounded off for the total.",
                        "type": "number"
                    }, {
                        "type": "null"
                    }]
                },
                "total_quantity_cases": {
                    "description": "The total quantity of items in cases across all line items.",
                    "anyOf": [{
                        "description": "The total quantity of items in cases across all line items.",
                        "type": "number"
                    }, {
                        "type": "null"
                    }]
                },
                "total_amount_chargeable": {
                    "description": "The final total amount chargeable for the invoice.",
                    "type": "number"
                },
                "amount_chargeable_in_words": {
                    "description": "The total amount chargeable written in words.",
                    "anyOf": [{
                        "description": "The total amount chargeable written in words.",
                        "type": "string"
                    }, {
                        "type": "null"
                    }]
                }
            },
            "required": ["subtotal_amount", "tcs_payable_on_sale_percentage", "tcs_payable_on_sale_amount", "round_off_amount", "total_quantity_cases", "total_amount_chargeable", "amount_chargeable_in_words"],
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
        "is_computer_generated": {
            "description": "Indicates if the invoice is stated to be computer generated.",
            "anyOf": [{
                "description": "Indicates if the invoice is stated to be computer generated.",
                "type": "boolean"
            }, {
                "type": "null"
            }]
        }
    },
    "required": ["invoice_header", "sender_details", "recipient_details", "line_items", "summary", "declaration", "is_computer_generated"],
    "additionalProperties": False
}

# Upload
file_obj = client.files.create(file="images/wp.jpeg", purpose="extract")

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
