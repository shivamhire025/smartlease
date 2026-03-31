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
from forms.purchase import fill_purchase_pdf
from forms.mutual_release import fill_mutual_release_pdf
from forms.waiver import fill_waiver_pdf
from forms.notice_fulfillment import fill_notice_fulfillment_pdf
from forms.listing_agreement import fill_listing_agreement_pdf
from forms.buyer_representation import fill_buyer_representation_pdf
from forms.confirmation_cooperation import fill_confirmation_cooperation_pdf

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
- Agreement of Purchase and Sale (Form 100)
- Mutual Release (Form 122)
- Waiver (Form 123)
- Notice of Fulfillment of Condition(s) (Form 124)
- Listing Agreement (Form 200)
- Buyer Representation Agreement (Form 300)
- Confirmation of Co-operation and Representation (Form 320)

BEHAVIOR RULES:
1. When a user describes their need, identify which form 
   they require based on context:
   - Leasing/renting → Form 2229E (Standard Lease)
   - Buying/selling → Form 100 (Purchase and Sale)
   - Releasing/cancelling APS → Form 122 (Mutual Release)
   - Waiving conditions in APS → Form 123 (Waiver)
   - Confirming conditions are fulfilled in APS → Form 124 (Notice of Fulfillment)
   - Listing a property for sale with brokerage → Form 200 (Listing Agreement)
   - Appointing buyer brokerage representation → Form 300 (Buyer Representation)
   - Confirming cooperation/representation in a trade → Form 320 (Confirmation of Co-operation)

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
    },
    {
        "name": "fill_purchase_and_sale",
        "description": "Fill OREA Form 100 Agreement of Purchase and Sale with collected data and generate a filled PDF.",
        "input_schema": {
            "type": "object",
            "properties": {
                "street_number": {"type": "string"},
                "street_name": {"type": "string"},
                "unit": {"type": "string"},
                "city": {"type": "string"},
                "province": {"type": "string"},
                "postal_code": {"type": "string"},
                "frontage": {"type": "string"},
                "side_of_street": {"type": "string"},
                "municipality": {"type": "string"},
                "depth": {"type": "string"},
                "legal_description": {"type": "string"},
                "buyer_1_name": {"type": "string"},
                "buyer_2_name": {"type": "string"},
                "seller_1_name": {"type": "string"},
                "seller_2_name": {"type": "string"},
                "purchase_price": {"type": "string"},
                "purchase_price_words": {"type": "string"},
                "deposit_words": {"type": "string"},
                "deposit_amount": {"type": "string"},
                "deposit_holder": {"type": "string"},
                "offer_date": {"type": "string"},
                "irrevocability_date": {"type": "string"},
                "irrevocability_time": {"type": "string"},
                "completion_date": {"type": "string"},
                "requisition_date": {"type": "string"},
                "chattels_included": {"type": "string"},
                "fixtures_excluded": {"type": "string"},
                "rental_items": {"type": "string"},
                "schedules": {"type": "string"},
                "schedule_a_content": {"type": "string"},
                "present_use": {"type": "string"},
                "hst_treatment": {"type": "string"},
                "buyer_address": {"type": "string"},
                "buyer_phone": {"type": "string"},
                "seller_address": {"type": "string"},
                "seller_phone": {"type": "string"},
                "listing_brokerage": {"type": "string"},
                "listing_brokerage_phone": {"type": "string"},
                "listing_agent": {"type": "string"},
                "coop_brokerage": {"type": "string"},
                "coop_brokerage_phone": {"type": "string"},
                "coop_agent": {"type": "string"}
            },
            "required": [
                "street_number", "street_name", "unit", "city",
                "postal_code", "frontage", "side_of_street",
                "municipality", "depth", "legal_description",
                "buyer_1_name", "buyer_2_name", "seller_1_name",
                "seller_2_name", "purchase_price", "purchase_price_words",
                "deposit_words", "deposit_amount", "deposit_holder",
                "offer_date", "irrevocability_date", "irrevocability_time",
                "completion_date", "requisition_date", "chattels_included",
                "fixtures_excluded", "rental_items", "schedule_a_content",
                "present_use", "hst_treatment", "buyer_address",
                "buyer_phone", "seller_address", "seller_phone",
                "listing_brokerage", "listing_brokerage_phone",
                "listing_agent", "coop_brokerage",
                "coop_brokerage_phone", "coop_agent"
            ]
        }
    },
    {
        "name": "fill_mutual_release",
        "description": "Fill OREA Form 122 Mutual Release with collected data and generate a filled PDF.",
        "input_schema": {
            "type": "object",
            "properties": {
                "buyer_1_name": {"type": "string"},
                "buyer_2_name": {"type": "string"},
                "seller_1_name": {"type": "string"},
                "seller_2_name": {"type": "string"},
                "listing_brokerage": {"type": "string"},
                "coop_brokerage": {"type": "string"},
                "agreement_date": {"type": "string"},
                "street_number": {"type": "string"},
                "street_name": {"type": "string"},
                "unit": {"type": "string"},
                "city": {"type": "string"},
                "province": {"type": "string"},
                "postal_code": {"type": "string"},
                "deposit_words": {"type": "string"},
                "deposit_amount": {"type": "string"},
                "payable_to": {"type": "string"},
                "payable_to_line2": {"type": "string"},
                "irrevocability_party": {"type": "string"},
                "irrevocability_time": {"type": "string"},
                "irrevocability_date": {"type": "string"},
                "confirmation_date": {"type": "string"},
                "confirmation_time": {"type": "string"}
            },
            "required": [
                "buyer_1_name",
                "seller_1_name",
                "agreement_date",
                "street_number",
                "street_name",
                "city",
                "deposit_amount"
            ]
        }
    },
    {
        "name": "fill_waiver",
        "description": "Fill OREA Form 123 Waiver with collected data and generate a filled PDF.",
        "input_schema": {
            "type": "object",
            "properties": {
                "buyer_1_name": {"type": "string"},
                "buyer_2_name": {"type": "string"},
                "seller_1_name": {"type": "string"},
                "seller_2_name": {"type": "string"},
                "street_number": {"type": "string"},
                "street_name": {"type": "string"},
                "unit": {"type": "string"},
                "city": {"type": "string"},
                "province": {"type": "string"},
                "postal_code": {"type": "string"},
                "agreement_date": {"type": "string"},
                "conditions_waived": {"type": "string"},
                "dated_at_city": {"type": "string"},
                "dated_time": {"type": "string"},
                "dated_date": {"type": "string"},
                "witness_1_name": {"type": "string"},
                "witness_2_name": {"type": "string"},
                "signer_1_name": {"type": "string"},
                "signer_2_name": {"type": "string"},
                "receipt_time": {"type": "string"},
                "receipt_date": {"type": "string"},
                "receipt_acknowledged_by": {"type": "string"}
            },
            "required": [
                "buyer_1_name",
                "seller_1_name",
                "street_number",
                "street_name",
                "city",
                "agreement_date",
                "conditions_waived",
                "dated_at_city",
                "dated_date"
            ]
        }
    },
    {
        "name": "fill_notice_fulfillment",
        "description": "Fill OREA Form 124 Notice of Fulfillment of Condition(s) with collected data and generate a filled PDF.",
        "input_schema": {
            "type": "object",
            "properties": {
                "buyer_1_name": {"type": "string"},
                "buyer_2_name": {"type": "string"},
                "seller_1_name": {"type": "string"},
                "seller_2_name": {"type": "string"},
                "street_number": {"type": "string"},
                "street_name": {"type": "string"},
                "unit": {"type": "string"},
                "city": {"type": "string"},
                "province": {"type": "string"},
                "postal_code": {"type": "string"},
                "agreement_date": {"type": "string"},
                "conditions_fulfilled": {"type": "string"},
                "dated_at_city": {"type": "string"},
                "dated_time": {"type": "string"},
                "dated_date": {"type": "string"},
                "witness_1_name": {"type": "string"},
                "witness_2_name": {"type": "string"},
                "signer_1_name": {"type": "string"},
                "signer_2_name": {"type": "string"},
                "receipt_time": {"type": "string"},
                "receipt_date": {"type": "string"},
                "receipt_acknowledged_by": {"type": "string"}
            },
            "required": [
                "buyer_1_name",
                "seller_1_name",
                "street_number",
                "street_name",
                "city",
                "agreement_date",
                "conditions_fulfilled",
                "dated_at_city",
                "dated_date"
            ]
        }
    },
    {
        "name": "fill_listing_agreement",
        "description": "Fill OREA Form 200 Listing Agreement with collected data and generate a filled PDF.",
        "input_schema": {
            "type": "object",
            "properties": {
                "listing_brokerage": {"type": "string"},
                "listing_brokerage_phone": {"type": "string"},
                "listing_brokerage_address": {"type": "string"},
                "listing_brokerage_city": {"type": "string"},
                "listing_brokerage_province": {"type": "string"},
                "listing_brokerage_postal_code": {"type": "string"},
                "seller_1_name": {"type": "string"},
                "seller_2_name": {"type": "string"},
                "street_number": {"type": "string"},
                "street_name": {"type": "string"},
                "unit": {"type": "string"},
                "city": {"type": "string"},
                "province": {"type": "string"},
                "postal_code": {"type": "string"},
                "commencement_time": {"type": "string"},
                "listing_start_date": {"type": "string"},
                "listing_end_date": {"type": "string"},
                "listing_price": {"type": "string"},
                "listing_price_words": {"type": "string"},
                "schedules": {"type": "string"},
                "listing_commission": {"type": "string"},
                "listing_commission_words": {"type": "string"},
                "coop_commission": {"type": "string"},
                "holdover_days": {"type": "string"},
                "listing_agent_name": {"type": "string"},
                "seller_1_phone": {"type": "string"},
                "seller_2_phone": {"type": "string"},
                "acknowledgement_date": {"type": "string"},
                "schedule_a_content": {"type": "string"}
            },
            "required": [
                "listing_brokerage",
                "seller_1_name",
                "street_number",
                "street_name",
                "city",
                "listing_start_date",
                "listing_end_date",
                "listing_price",
                "listing_commission"
            ]
        }
    },
    {
        "name": "fill_buyer_representation",
        "description": "Fill OREA Form 300 Buyer Representation Agreement with collected data and generate a filled PDF.",
        "input_schema": {
            "type": "object",
            "properties": {
                "brokerage_name": {"type": "string"},
                "brokerage_address": {"type": "string"},
                "brokerage_city": {"type": "string"},
                "brokerage_province": {"type": "string"},
                "brokerage_postal_code": {"type": "string"},
                "brokerage_phone": {"type": "string"},
                "brokerage_fax": {"type": "string"},
                "buyer_1_name": {"type": "string"},
                "buyer_2_name": {"type": "string"},
                "buyer_street_number": {"type": "string"},
                "buyer_street_name": {"type": "string"},
                "buyer_city": {"type": "string"},
                "buyer_postal_code": {"type": "string"},
                "commencement_time": {"type": "string"},
                "start_date": {"type": "string"},
                "expiry_date": {"type": "string"},
                "property_type": {"type": "string"},
                "property_type_2": {"type": "string"},
                "geographic_location": {"type": "string"},
                "geographic_location_2": {"type": "string"},
                "schedules": {"type": "string"},
                "commission_percent": {"type": "string"},
                "commission_words": {"type": "string"},
                "lease_commission": {"type": "string"},
                "holdover_days": {"type": "string"},
                "agent_name": {"type": "string"},
                "buyer_1_phone": {"type": "string"},
                "buyer_2_phone": {"type": "string"},
                "acknowledgement_date": {"type": "string"},
                "schedule_a_content": {"type": "string"}
            },
            "required": [
                "brokerage_name",
                "buyer_1_name",
                "start_date",
                "expiry_date",
                "property_type",
                "geographic_location"
            ]
        }
    },
    {
        "name": "fill_confirmation_cooperation",
        "description": "Fill OREA Form 320 Confirmation of Co-operation and Representation with collected data and generate a filled PDF.",
        "input_schema": {
            "type": "object",
            "properties": {
                "buyer_1_name": {"type": "string"},
                "buyer_2_name": {"type": "string"},
                "seller_1_name": {"type": "string"},
                "seller_2_name": {"type": "string"},
                "street_number": {"type": "string"},
                "street_name": {"type": "string"},
                "unit": {"type": "string"},
                "city": {"type": "string"},
                "province": {"type": "string"},
                "postal_code": {"type": "string"},
                "seller_representation": {"type": "string"},
                "coop_representation": {"type": "string"},
                "coop_commission_type": {"type": "string"},
                "coop_commission_mls_amount": {"type": "string"},
                "coop_commission_other": {"type": "string"},
                "coop_additional_comments": {"type": "string"},
                "seller_additional_comments": {"type": "string"},
                "seller_additional_comments_2": {"type": "string"},
                "seller_brokerage_name": {"type": "string"},
                "seller_brokerage_address": {"type": "string"},
                "seller_brokerage_phone": {"type": "string"},
                "seller_brokerage_fax": {"type": "string"},
                "seller_agent_name": {"type": "string"},
                "coop_brokerage_name": {"type": "string"},
                "coop_brokerage_address": {"type": "string"},
                "coop_brokerage_phone": {"type": "string"},
                "coop_brokerage_fax": {"type": "string"},
                "coop_agent_name": {"type": "string"}
            },
            "required": [
                "buyer_1_name",
                "seller_1_name",
                "street_number",
                "street_name",
                "city",
                "seller_brokerage_name",
                "seller_agent_name"
            ]
        }
    },
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
            elif block.name == "fill_purchase_and_sale":
                tool_input = dict(block.input)
                try:
                    pdf_bytes = fill_purchase_pdf(tool_input)
                    filled_document_pdf = base64.b64encode(pdf_bytes).decode("ascii")
                    tool_result_content = (
                        "OREA Form 100 PDF generated successfully."
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Purchase PDF fill error: {e}")
                    tool_result_content = "Purchase PDF generation failed."

                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result_content,
                    }
                )
            elif block.name == "fill_mutual_release":
                tool_input = dict(block.input)
                try:
                    pdf_bytes = fill_mutual_release_pdf(tool_input)
                    filled_document_pdf = base64.b64encode(pdf_bytes).decode("ascii")
                    tool_result_content = (
                        "OREA Form 122 Mutual Release PDF generated successfully."
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Mutual release PDF fill error: {e}")
                    tool_result_content = "Mutual release PDF generation failed."

                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result_content,
                    }
                )
            elif block.name == "fill_waiver":
                tool_input = dict(block.input)
                try:
                    pdf_bytes = fill_waiver_pdf(tool_input)
                    filled_document_pdf = base64.b64encode(pdf_bytes).decode("ascii")
                    tool_result_content = (
                        "OREA Form 123 Waiver PDF generated successfully."
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Waiver PDF fill error: {e}")
                    tool_result_content = "Waiver PDF generation failed."

                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result_content,
                    }
                )
            elif block.name == "fill_notice_fulfillment":
                tool_input = dict(block.input)
                try:
                    pdf_bytes = fill_notice_fulfillment_pdf(tool_input)
                    filled_document_pdf = base64.b64encode(pdf_bytes).decode("ascii")
                    tool_result_content = (
                        "OREA Form 124 Notice of Fulfillment PDF generated successfully."
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Notice of fulfillment PDF fill error: {e}")
                    tool_result_content = "Notice of fulfillment PDF generation failed."

                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result_content,
                    }
                )
            elif block.name == "fill_listing_agreement":
                tool_input = dict(block.input)
                try:
                    pdf_bytes = fill_listing_agreement_pdf(tool_input)
                    filled_document_pdf = base64.b64encode(pdf_bytes).decode("ascii")
                    tool_result_content = (
                        "OREA Form 200 Listing Agreement PDF generated successfully."
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Listing agreement PDF fill error: {e}")
                    tool_result_content = "Listing agreement PDF generation failed."

                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result_content,
                    }
                )
            elif block.name == "fill_buyer_representation":
                tool_input = dict(block.input)
                try:
                    pdf_bytes = fill_buyer_representation_pdf(tool_input)
                    filled_document_pdf = base64.b64encode(pdf_bytes).decode("ascii")
                    tool_result_content = (
                        "OREA Form 300 Buyer Representation Agreement PDF generated successfully."
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Buyer representation PDF fill error: {e}")
                    tool_result_content = "Buyer representation PDF generation failed."

                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result_content,
                    }
                )
            elif block.name == "fill_confirmation_cooperation":
                tool_input = dict(block.input)
                try:
                    pdf_bytes = fill_confirmation_cooperation_pdf(tool_input)
                    filled_document_pdf = base64.b64encode(pdf_bytes).decode("ascii")
                    tool_result_content = (
                        "OREA Form 320 Confirmation of Co-operation PDF generated successfully."
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Confirmation of co-operation PDF fill error: {e}")
                    tool_result_content = "Confirmation of co-operation PDF generation failed."

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
