from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import anthropic
import os
import base64
from dotenv import load_dotenv
from forms.lease import fill_lease, fill_lease_pdf

load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError(
        "ANTHROPIC_API_KEY is required. Set it in your .env file."
    )

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


AGENT_SYSTEM_PROMPT = """
You are Smartlease, an AI assistant that helps users fill 
official Ontario real estate documents accurately and quickly.

You currently support:
- Ontario Standard Lease Agreement (Form 2229E) — for 
  landlords renting residential properties
- Agreement of Purchase and Sale (Form 100) — coming soon

BEHAVIOR RULES:
1. When a user describes their need, identify which form 
   they require based on context:
   - Leasing/renting → Form 2229E (Standard Lease)
   - Buying/selling → Form 100 (Purchase and Sale)

2. Collect information conversationally — ask ONE question 
   at a time. Never present a list of questions all at once.

3. Be warm, professional and concise. You are helping with 
   legal documents so accuracy matters.

4. When you have collected ALL required fields for the form, 
   call the appropriate tool to fill it.

5. Before calling the tool, show the user a brief summary 
   of the key details and ask them to confirm.

6. After the tool is called and the document is ready, 
   tell the user their document is ready to download.

REQUIRED FIELDS FOR FORM 2229E (Standard Lease):
Collect these through natural conversation:
- Landlord: full legal name, mailing address, phone, email
- Rental unit: full address including unit number
- Lease start date and type (fixed term or monthly)
- If fixed term: end date
- Monthly rent amount, which day of month it is due,
  payment method (e-transfer, cheque, etc.)
- Who rent is payable to
- Services included in rent: gas, AC, storage, laundry, 
  guest parking
- Utility responsibility for electricity, heat, water
  (landlord or tenant)
- Rent deposit amount (usually first and last month)
- Key deposit amount and description (if any)
- Smoking rules (none, or custom rules)
- Tenant insurance required (yes or no)
- Any additional terms
- Number of tenants and their full names and emails
- NSF charge amount (maximum $20)

EXAMPLE CONVERSATION FLOW:
User: "I need to create a lease for my condo"
You: "I can help you prepare an Ontario Standard Lease. 
      What is the full address of the rental unit?"
User: "45 Bay Street unit 2104, Toronto"
You: "Got it. What is your full legal name as the landlord?"
...continue until all fields collected...
You: "Here's a summary of what I have:
      - Property: 45 Bay Street Unit 2104, Toronto
      - Landlord: [name]
      - Tenant(s): [names]
      - Rent: $[amount]/month starting [date]
      Does everything look correct?"
User: "Yes"
You: [calls fill_lease_agreement tool]
You: "Your lease is ready! You can review and download it 
      using the button in the document panel."

IMPORTANT: 
- Never make up or assume field values
- Always ask if you are unsure about something
- If the user gives you multiple pieces of information 
  at once, acknowledge them all and ask for the next 
  missing field
- Dates should always be formatted as yyyy/mm/dd
"""

tools = [
    {
        "name": "fill_lease_agreement",
        "description": "Fill Ontario Standard Lease Form 2229E with the collected data and generate the complete document. Only call this when ALL required fields have been collected and confirmed by the user.",
        "input_schema": {
            "type": "object",
            "properties": {
                "landlord_name": {"type": "string"},
                "landlord_unit": {"type": "string"},
                "landlord_street_number": {"type": "string"},
                "landlord_street_name": {"type": "string"},
                "landlord_po_box": {"type": "string"},
                "landlord_city": {"type": "string"},
                "landlord_province": {"type": "string"},
                "landlord_postal_code": {"type": "string"},
                "landlord_phone": {"type": "string"},
                "landlord_email": {"type": "string"},
                "email_notices_agreed": {"type": "boolean"},
                "emergency_contact_provided": {"type": "boolean"},
                "emergency_contact_info": {"type": "string"},
                "unit": {"type": "string"},
                "street_number": {"type": "string"},
                "street_name": {"type": "string"},
                "city": {"type": "string"},
                "postal_code": {"type": "string"},
                "parking_description": {"type": "string"},
                "is_condo": {"type": "boolean"},
                "start_date": {"type": "string"},
                "tenancy_type": {
                    "type": "string",
                    "enum": ["fixed", "monthly", "other"]
                },
                "end_date": {"type": "string"},
                "other_tenancy_description": {"type": "string"},
                "rent_payment_day": {"type": "string"},
                "rent_frequency": {
                    "type": "string",
                    "enum": ["monthly", "other"]
                },
                "rent_frequency_other": {"type": "string"},
                "base_rent": {"type": "number"},
                "parking_rent": {"type": "number"},
                "extra_services": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "amount": {"type": "number"}
                        }
                    }
                },
                "total_rent": {"type": "number"},
                "rent_payable_to": {"type": "string"},
                "payment_method": {"type": "string"},
                "has_partial_period": {"type": "boolean"},
                "partial_amount": {"type": "number"},
                "partial_payment_date": {"type": "string"},
                "partial_from_date": {"type": "string"},
                "partial_to_date": {"type": "string"},
                "nsf_charge": {"type": "number"},
                "gas_included": {"type": "boolean"},
                "ac_included": {"type": "boolean"},
                "storage_included": {"type": "boolean"},
                "laundry": {
                    "type": "string",
                    "enum": ["yes","no","no_charge","pay_per_use"]
                },
                "guest_parking": {
                    "type": "string",
                    "enum": ["yes","no","no_charge","pay_per_use"]
                },
                "other_services": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "included": {"type": "boolean"}
                        }
                    }
                },
                "service_details": {"type": "string"},
                "electricity_responsibility": {
                    "type": "string",
                    "enum": ["landlord","tenant"]
                },
                "heat_responsibility": {
                    "type": "string",
                    "enum": ["landlord","tenant"]
                },
                "water_responsibility": {
                    "type": "string",
                    "enum": ["landlord","tenant"]
                },
                "utility_details": {"type": "string"},
                "has_rent_discount": {"type": "boolean"},
                "rent_discount_description": {"type": "string"},
                "rent_deposit": {"type": "number"},
                "key_deposit": {"type": "number"},
                "key_deposit_description": {"type": "string"},
                "smoking_rules": {"type": "string"},
                "insurance_required": {"type": "boolean"},
                "additional_terms": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "tenants": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "first_name": {"type": "string"},
                            "last_name": {"type": "string"},
                            "email": {"type": "string"}
                        }
                    }
                }
            },
            "required": [
                "landlord_name", "unit", "street_number",
                "street_name", "city", "postal_code",
                "start_date", "tenancy_type", "base_rent",
                "total_rent", "rent_payable_to",
                "payment_method", "tenants"
            ]
        }
    }
]


def _messages_to_anthropic(msgs: list[Message]) -> list[dict]:
    return [{"role": m.role, "content": m.content} for m in msgs]


def _content_blocks_to_message_param(content) -> list[dict]:
    blocks: list[dict] = []
    for block in content:
        if block.type == "text":
            blocks.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            blocks.append(
                {
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                }
            )
    return blocks


def _extract_text_from_response(message) -> str:
    parts: list[str] = []
    for block in message.content:
        if block.type == "text":
            parts.append(block.text)
    return "".join(parts)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        anthropic_messages = _messages_to_anthropic(request.messages)

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=AGENT_SYSTEM_PROMPT,
            messages=anthropic_messages,
            tools=tools,
        )

        filled_document: str | None = None
        filled_document_pdf: str | None = None

        if response.stop_reason != "tool_use":
            return {
                "message": _extract_text_from_response(response),
                "filled_document": None,
                "filled_document_pdf": None,
                "role": "assistant",
            }

        assistant_content_param = _content_blocks_to_message_param(
            response.content
        )
        tool_result_blocks: list[dict] = []

        for block in response.content:
            if block.type != "tool_use":
                continue
            if block.name == "fill_lease_agreement":
                tool_input = dict(block.input)
                try:
                    pdf_bytes = fill_lease_pdf(tool_input)
                    print(f"PDF bytes length: {len(pdf_bytes) if pdf_bytes else 'None'}")
                    filled_document_pdf = base64.b64encode(pdf_bytes).decode("ascii")
                    tool_result_content = (
                        "Ontario Standard Lease PDF generated successfully."
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"PDF fill error: {e}")
                    filled_document = fill_lease(tool_input)
                    tool_result_content = "PDF generation failed; HTML lease generated."
                
                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result_content,
                    }
                )
            else:
                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": (
                            f"Unknown tool: {block.name}. "
                            "No handler is available."
                        ),
                    }
                )

        follow_up_messages = anthropic_messages + [
            {"role": "assistant", "content": assistant_content_param},
            {"role": "user", "content": tool_result_blocks},
        ]

        final_response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=AGENT_SYSTEM_PROMPT,
            messages=follow_up_messages,
            tools=tools,
        )

        return {
            "message": _extract_text_from_response(final_response),
            "filled_document": filled_document,
            "filled_document_pdf": filled_document_pdf,
            "role": "assistant",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "An error occurred while processing your request. "
                f"{str(e)}"
            ),
        ) from e


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Smartlease API"}


app.mount(
    "/",
    StaticFiles(directory=os.path.join(BASE_DIR, "public"), html=True),
    name="static",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
