import json
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from forms.lease import fill_lease_pdf
from forms.purchase import fill_purchase_pdf
from forms.mutual_release import fill_mutual_release_pdf
from forms.waiver import fill_waiver_pdf
from forms.notice_fulfillment import fill_notice_fulfillment_pdf
from forms.listing_agreement import fill_listing_agreement_pdf
from forms.buyer_representation import fill_buyer_representation_pdf
from forms.confirmation_cooperation import fill_confirmation_cooperation_pdf

mcp = FastMCP(
    "smartlease",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    )
)


@mcp.tool()
def fill_lease_agreement(
    landlord_name: str,
    unit: str,
    street_number: str,
    street_name: str,
    city: str,
    postal_code: str,
    start_date: str,
    tenancy_type: str,
    base_rent: float,
    total_rent: float,
    rent_payable_to: str,
    payment_method: str,
    tenants_json: str,
    landlord_unit: str = "",
    landlord_street_number: str = "",
    landlord_street_name: str = "",
    landlord_po_box: str = "",
    landlord_city: str = "",
    landlord_province: str = "Ontario",
    landlord_postal_code: str = "",
    landlord_phone: str = "",
    landlord_email: str = "",
    email_notices_agreed: bool = False,
    emergency_contact_provided: bool = False,
    emergency_contact_info: str = "",
    parking_description: str = "",
    is_condo: bool = False,
    end_date: str = "",
    other_tenancy_description: str = "",
    rent_payment_day: str = "first",
    rent_frequency: str = "monthly",
    rent_frequency_other: str = "",
    parking_rent: float = 0.0,
    extra_services_json: str = "[]",
    has_partial_period: bool = False,
    partial_amount: float = 0.0,
    partial_payment_date: str = "",
    partial_from_date: str = "",
    partial_to_date: str = "",
    nsf_charge: float = 20.0,
    gas_included: bool = False,
    ac_included: bool = False,
    storage_included: bool = False,
    laundry: str = "no",
    guest_parking: str = "no",
    other_services_json: str = "[]",
    service_details: str = "",
    electricity_responsibility: str = "tenant",
    heat_responsibility: str = "landlord",
    water_responsibility: str = "tenant",
    utility_details: str = "",
    has_rent_discount: bool = False,
    rent_discount_description: str = "",
    rent_deposit: float = 0.0,
    key_deposit: float = 0.0,
    key_deposit_description: str = "",
    smoking_rules: str = "none",
    insurance_required: bool = False,
    additional_terms_json: str = "[]",
) -> dict:
    """
    Fill an Ontario Standard Residential Lease Agreement
    (Form 2229E) and return a path to the filled PDF.

    Use this tool when a user wants to create a lease
    agreement for a residential property in Ontario, Canada.
    Collect all required information through conversation
    before calling this tool.
    """
    try:
        tenants = json.loads(tenants_json)
        extra_services = json.loads(extra_services_json)
        other_services = json.loads(other_services_json)
        additional_terms = json.loads(additional_terms_json)

        data = {
            "landlord_name": landlord_name,
            "landlord_unit": landlord_unit,
            "landlord_street_number": landlord_street_number,
            "landlord_street_name": landlord_street_name,
            "landlord_po_box": landlord_po_box,
            "landlord_city": landlord_city,
            "landlord_province": landlord_province,
            "landlord_postal_code": landlord_postal_code,
            "landlord_phone": landlord_phone,
            "landlord_email": landlord_email,
            "email_notices_agreed": email_notices_agreed,
            "emergency_contact_provided": emergency_contact_provided,
            "emergency_contact_info": emergency_contact_info,
            "unit": unit,
            "street_number": street_number,
            "street_name": street_name,
            "city": city,
            "postal_code": postal_code,
            "parking_description": parking_description,
            "is_condo": is_condo,
            "start_date": start_date,
            "tenancy_type": tenancy_type,
            "end_date": end_date,
            "other_tenancy_description": other_tenancy_description,
            "rent_payment_day": rent_payment_day,
            "rent_frequency": rent_frequency,
            "rent_frequency_other": rent_frequency_other,
            "base_rent": base_rent,
            "parking_rent": parking_rent,
            "extra_services": extra_services,
            "total_rent": total_rent,
            "rent_payable_to": rent_payable_to,
            "payment_method": payment_method,
            "has_partial_period": has_partial_period,
            "partial_amount": partial_amount,
            "partial_payment_date": partial_payment_date,
            "partial_from_date": partial_from_date,
            "partial_to_date": partial_to_date,
            "nsf_charge": nsf_charge,
            "gas_included": gas_included,
            "ac_included": ac_included,
            "storage_included": storage_included,
            "laundry": laundry,
            "guest_parking": guest_parking,
            "other_services": other_services,
            "service_details": service_details,
            "electricity_responsibility": electricity_responsibility,
            "heat_responsibility": heat_responsibility,
            "water_responsibility": water_responsibility,
            "utility_details": utility_details,
            "has_rent_discount": has_rent_discount,
            "rent_discount_description": rent_discount_description,
            "rent_deposit": rent_deposit,
            "key_deposit": key_deposit,
            "key_deposit_description": key_deposit_description,
            "smoking_rules": smoking_rules,
            "insurance_required": insurance_required,
            "additional_terms": additional_terms,
            "tenants": tenants,
        }

        pdf_bytes = fill_lease_pdf(data)
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pdf", delete=False
        ) as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            pdf_path = tmp_pdf.name

        return {
            "success": True,
            "document_pdf_path": pdf_path,
            "message": "Lease agreement PDF successfully generated.",
            "form": "Ontario Standard Lease - Form 2229E",
            "landlord": landlord_name,
            "property": f"{unit} {street_number} {street_name}, {city}",
            "tenants": [
                t.get("first_name", "") + " " + t.get("last_name", "")
                for t in tenants
            ],
            "monthly_rent": f"${total_rent:,.2f}",
            "start_date": start_date,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate lease agreement.",
        }


@mcp.tool()
def get_supported_forms() -> dict:
    """
    Get a list of all real estate forms currently
    supported by Smartlease. Use this to inform users
    what documents can be generated.
    """
    return {
        "supported_forms": [
            {
                "id": "lease_2229e",
                "name": "Ontario Standard Lease Agreement",
                "form_number": "Form 2229E (2020/12)",
                "description": "Standard residential tenancy agreement required for most Ontario rentals entered into on or after March 1, 2021",
                "use_case": "Landlord renting a residential unit to tenant(s)",
                "tool": "fill_lease_agreement",
            },
            {
                "id": "purchase_100",
                "name": "Agreement of Purchase and Sale",
                "form_number": "OREA Form 100 (Revised 2024)",
                "description": "Standard offer to purchase residential real property in Ontario",
                "use_case": "Buyer making an offer to purchase a residential property",
                "tool": "fill_purchase_and_sale",
            },
            {
                "id": "mutual_release_122",
                "name": "Mutual Release",
                "form_number": "OREA Form 122",
                "description": "Mutual release between buyer and seller for an agreement of purchase and sale",
                "use_case": "Buyer and seller mutually releasing each other from APS obligations",
                "tool": "fill_mutual_release",
            },
            {
                "id": "waiver_123",
                "name": "Waiver",
                "form_number": "OREA Form 123",
                "description": "Waiver of conditions in an agreement of purchase and sale",
                "use_case": "Buyer and/or seller waiving one or more conditions",
                "tool": "fill_waiver",
            },
            {
                "id": "notice_fulfillment_124",
                "name": "Notice of Fulfillment of Condition(s)",
                "form_number": "OREA Form 124",
                "description": "Notice confirming fulfillment of one or more conditions in an agreement of purchase and sale",
                "use_case": "Buyer and/or seller confirming conditions have been fulfilled",
                "tool": "fill_notice_fulfillment",
            },
            {
                "id": "listing_agreement_200",
                "name": "Listing Agreement",
                "form_number": "OREA Form 200",
                "description": "Listing agreement between seller and listing brokerage for sale of property",
                "use_case": "Seller engaging a brokerage to list and market a property",
                "tool": "fill_listing_agreement",
            },
            {
                "id": "buyer_representation_300",
                "name": "Buyer Representation Agreement",
                "form_number": "OREA Form 300",
                "description": "Agreement appointing a brokerage to represent the buyer in finding and purchasing/leasing property",
                "use_case": "Buyer engaging a brokerage for representation services",
                "tool": "fill_buyer_representation",
            },
            {
                "id": "confirmation_cooperation_320",
                "name": "Confirmation of Co-operation and Representation",
                "form_number": "OREA Form 320",
                "description": "Confirmation of brokerage cooperation and representation relationships in a trade",
                "use_case": "Buyer/seller and cooperating brokerages acknowledging representation and commission arrangements",
                "tool": "fill_confirmation_cooperation",
            },
        ],
        "total_supported": 8,
        "coming_soon": 0,
    }


@mcp.tool()
def fill_purchase_and_sale(
    street_number: str,
    street_name: str,
    unit: str,
    city: str,
    postal_code: str,
    frontage: str,
    side_of_street: str,
    municipality: str,
    depth: str,
    legal_description: str,
    buyer_1_name: str,
    buyer_2_name: str,
    seller_1_name: str,
    seller_2_name: str,
    purchase_price: str,
    purchase_price_words: str,
    deposit_words: str,
    deposit_amount: str,
    deposit_holder: str,
    offer_date: str,
    irrevocability_date: str,
    irrevocability_time: str,
    completion_date: str,
    requisition_date: str,
    chattels_included: str,
    fixtures_excluded: str,
    rental_items: str,
    schedule_a_content: str,
    present_use: str,
    hst_treatment: str,
    buyer_address: str,
    buyer_phone: str,
    seller_address: str,
    seller_phone: str,
    listing_brokerage: str,
    listing_brokerage_phone: str,
    listing_agent: str,
    coop_brokerage: str,
    coop_brokerage_phone: str,
    coop_agent: str,
    province: str = "Ontario",
    schedules: str = "A",
) -> dict:
    """
    Fill OREA Agreement of Purchase and Sale
    (Form 100) and return a path to the filled PDF.
    """
    try:
        data = {
            "street_number": street_number,
            "street_name": street_name,
            "unit": unit,
            "city": city,
            "province": province,
            "postal_code": postal_code,
            "frontage": frontage,
            "side_of_street": side_of_street,
            "municipality": municipality,
            "depth": depth,
            "legal_description": legal_description,
            "buyer_1_name": buyer_1_name,
            "buyer_2_name": buyer_2_name,
            "seller_1_name": seller_1_name,
            "seller_2_name": seller_2_name,
            "purchase_price": purchase_price,
            "purchase_price_words": purchase_price_words,
            "deposit_words": deposit_words,
            "deposit_amount": deposit_amount,
            "deposit_holder": deposit_holder,
            "offer_date": offer_date,
            "irrevocability_date": irrevocability_date,
            "irrevocability_time": irrevocability_time,
            "completion_date": completion_date,
            "requisition_date": requisition_date,
            "chattels_included": chattels_included,
            "fixtures_excluded": fixtures_excluded,
            "rental_items": rental_items,
            "schedules": schedules,
            "schedule_a_content": schedule_a_content,
            "present_use": present_use,
            "hst_treatment": hst_treatment,
            "buyer_address": buyer_address,
            "buyer_phone": buyer_phone,
            "seller_address": seller_address,
            "seller_phone": seller_phone,
            "listing_brokerage": listing_brokerage,
            "listing_brokerage_phone": listing_brokerage_phone,
            "listing_agent": listing_agent,
            "coop_brokerage": coop_brokerage,
            "coop_brokerage_phone": coop_brokerage_phone,
            "coop_agent": coop_agent,
        }

        pdf_bytes = fill_purchase_pdf(data)
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pdf", delete=False
        ) as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            pdf_path = tmp_pdf.name

        return {
            "success": True,
            "document_pdf_path": pdf_path,
            "message": "Purchase and sale agreement PDF successfully generated.",
            "form": "OREA Form 100",
            "property": f"{unit} {street_number} {street_name}, {city}",
            "buyer_1_name": buyer_1_name,
            "seller_1_name": seller_1_name,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate purchase and sale agreement.",
        }


@mcp.tool()
def fill_mutual_release(
    buyer_1_name: str,
    seller_1_name: str,
    agreement_date: str,
    street_number: str,
    street_name: str,
    city: str,
    deposit_amount: str,
    buyer_2_name: str = "",
    seller_2_name: str = "",
    listing_brokerage: str = "",
    coop_brokerage: str = "",
    unit: str = "",
    province: str = "Ontario",
    postal_code: str = "",
    deposit_words: str = "",
    payable_to: str = "",
    payable_to_line2: str = "",
    irrevocability_party: str = "",
    irrevocability_time: str = "",
    irrevocability_date: str = "",
    confirmation_date: str = "",
    confirmation_time: str = "",
) -> dict:
    """
    Fill OREA Mutual Release (Form 122)
    and return a path to the filled PDF.
    """
    try:
        data = {
            "buyer_1_name": buyer_1_name,
            "buyer_2_name": buyer_2_name,
            "seller_1_name": seller_1_name,
            "seller_2_name": seller_2_name,
            "listing_brokerage": listing_brokerage,
            "coop_brokerage": coop_brokerage,
            "agreement_date": agreement_date,
            "street_number": street_number,
            "street_name": street_name,
            "unit": unit,
            "city": city,
            "province": province,
            "postal_code": postal_code,
            "deposit_words": deposit_words,
            "deposit_amount": deposit_amount,
            "payable_to": payable_to,
            "payable_to_line2": payable_to_line2,
            "irrevocability_party": irrevocability_party,
            "irrevocability_time": irrevocability_time,
            "irrevocability_date": irrevocability_date,
            "confirmation_date": confirmation_date,
            "confirmation_time": confirmation_time,
        }

        pdf_bytes = fill_mutual_release_pdf(data)
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pdf", delete=False
        ) as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            pdf_path = tmp_pdf.name

        return {
            "success": True,
            "document_pdf_path": pdf_path,
            "message": "Mutual release PDF successfully generated.",
            "form": "OREA Form 122",
            "property": f"{unit} {street_number} {street_name}, {city}",
            "buyer_1_name": buyer_1_name,
            "seller_1_name": seller_1_name,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate mutual release.",
        }


@mcp.tool()
def fill_waiver(
    buyer_1_name: str,
    seller_1_name: str,
    street_number: str,
    street_name: str,
    city: str,
    agreement_date: str,
    conditions_waived: str,
    dated_at_city: str,
    dated_date: str,
    buyer_2_name: str = "",
    seller_2_name: str = "",
    unit: str = "",
    province: str = "Ontario",
    postal_code: str = "",
    dated_time: str = "",
    witness_1_name: str = "",
    witness_2_name: str = "",
    signer_1_name: str = "",
    signer_2_name: str = "",
    receipt_time: str = "",
    receipt_date: str = "",
    receipt_acknowledged_by: str = "",
) -> dict:
    """
    Fill OREA Waiver (Form 123)
    and return a path to the filled PDF.
    """
    try:
        data = {
            "buyer_1_name": buyer_1_name,
            "buyer_2_name": buyer_2_name,
            "seller_1_name": seller_1_name,
            "seller_2_name": seller_2_name,
            "street_number": street_number,
            "street_name": street_name,
            "unit": unit,
            "city": city,
            "province": province,
            "postal_code": postal_code,
            "agreement_date": agreement_date,
            "conditions_waived": conditions_waived,
            "dated_at_city": dated_at_city,
            "dated_time": dated_time,
            "dated_date": dated_date,
            "witness_1_name": witness_1_name,
            "witness_2_name": witness_2_name,
            "signer_1_name": signer_1_name,
            "signer_2_name": signer_2_name,
            "receipt_time": receipt_time,
            "receipt_date": receipt_date,
            "receipt_acknowledged_by": receipt_acknowledged_by,
        }

        pdf_bytes = fill_waiver_pdf(data)
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pdf", delete=False
        ) as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            pdf_path = tmp_pdf.name

        return {
            "success": True,
            "document_pdf_path": pdf_path,
            "message": "Waiver PDF successfully generated.",
            "form": "OREA Form 123",
            "property": f"{unit} {street_number} {street_name}, {city}",
            "buyer_1_name": buyer_1_name,
            "seller_1_name": seller_1_name,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate waiver.",
        }


@mcp.tool()
def fill_notice_fulfillment(
    buyer_1_name: str,
    seller_1_name: str,
    street_number: str,
    street_name: str,
    city: str,
    agreement_date: str,
    conditions_fulfilled: str,
    dated_at_city: str,
    dated_date: str,
    buyer_2_name: str = "",
    seller_2_name: str = "",
    unit: str = "",
    province: str = "Ontario",
    postal_code: str = "",
    dated_time: str = "",
    witness_1_name: str = "",
    witness_2_name: str = "",
    signer_1_name: str = "",
    signer_2_name: str = "",
    receipt_time: str = "",
    receipt_date: str = "",
    receipt_acknowledged_by: str = "",
) -> dict:
    """
    Fill OREA Notice of Fulfillment of Condition(s) (Form 124)
    and return a path to the filled PDF.
    """
    try:
        data = {
            "buyer_1_name": buyer_1_name,
            "buyer_2_name": buyer_2_name,
            "seller_1_name": seller_1_name,
            "seller_2_name": seller_2_name,
            "street_number": street_number,
            "street_name": street_name,
            "unit": unit,
            "city": city,
            "province": province,
            "postal_code": postal_code,
            "agreement_date": agreement_date,
            "conditions_fulfilled": conditions_fulfilled,
            "dated_at_city": dated_at_city,
            "dated_time": dated_time,
            "dated_date": dated_date,
            "witness_1_name": witness_1_name,
            "witness_2_name": witness_2_name,
            "signer_1_name": signer_1_name,
            "signer_2_name": signer_2_name,
            "receipt_time": receipt_time,
            "receipt_date": receipt_date,
            "receipt_acknowledged_by": receipt_acknowledged_by,
        }

        pdf_bytes = fill_notice_fulfillment_pdf(data)
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pdf", delete=False
        ) as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            pdf_path = tmp_pdf.name

        return {
            "success": True,
            "document_pdf_path": pdf_path,
            "message": "Notice of fulfillment PDF successfully generated.",
            "form": "OREA Form 124",
            "property": f"{unit} {street_number} {street_name}, {city}",
            "buyer_1_name": buyer_1_name,
            "seller_1_name": seller_1_name,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate notice of fulfillment.",
        }


@mcp.tool()
def fill_listing_agreement(
    listing_brokerage: str,
    seller_1_name: str,
    street_number: str,
    street_name: str,
    city: str,
    listing_start_date: str,
    listing_end_date: str,
    listing_price: str,
    listing_commission: str,
    listing_brokerage_phone: str = "",
    listing_brokerage_address: str = "",
    listing_brokerage_city: str = "",
    listing_brokerage_province: str = "",
    listing_brokerage_postal_code: str = "",
    seller_2_name: str = "",
    unit: str = "",
    province: str = "ON",
    postal_code: str = "",
    commencement_time: str = "",
    listing_price_words: str = "",
    schedules: str = "A",
    listing_commission_words: str = "",
    coop_commission: str = "",
    holdover_days: str = "",
    listing_agent_name: str = "",
    seller_1_phone: str = "",
    seller_2_phone: str = "",
    acknowledgement_date: str = "",
    schedule_a_content: str = "",
) -> dict:
    """
    Fill OREA Listing Agreement (Form 200)
    and return a path to the filled PDF.
    """
    try:
        data = {
            "listing_brokerage": listing_brokerage,
            "listing_brokerage_phone": listing_brokerage_phone,
            "listing_brokerage_address": listing_brokerage_address,
            "listing_brokerage_city": listing_brokerage_city,
            "listing_brokerage_province": listing_brokerage_province,
            "listing_brokerage_postal_code": listing_brokerage_postal_code,
            "seller_1_name": seller_1_name,
            "seller_2_name": seller_2_name,
            "street_number": street_number,
            "street_name": street_name,
            "unit": unit,
            "city": city,
            "province": province,
            "postal_code": postal_code,
            "commencement_time": commencement_time,
            "listing_start_date": listing_start_date,
            "listing_end_date": listing_end_date,
            "listing_price": listing_price,
            "listing_price_words": listing_price_words,
            "schedules": schedules,
            "listing_commission": listing_commission,
            "listing_commission_words": listing_commission_words,
            "coop_commission": coop_commission,
            "holdover_days": holdover_days,
            "listing_agent_name": listing_agent_name,
            "seller_1_phone": seller_1_phone,
            "seller_2_phone": seller_2_phone,
            "acknowledgement_date": acknowledgement_date,
            "schedule_a_content": schedule_a_content,
        }

        pdf_bytes = fill_listing_agreement_pdf(data)
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pdf", delete=False
        ) as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            pdf_path = tmp_pdf.name

        return {
            "success": True,
            "document_pdf_path": pdf_path,
            "message": "Listing agreement PDF successfully generated.",
            "form": "OREA Form 200",
            "property": f"{unit} {street_number} {street_name}, {city}",
            "seller_1_name": seller_1_name,
            "listing_brokerage": listing_brokerage,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate listing agreement.",
        }


@mcp.tool()
def fill_buyer_representation(
    brokerage_name: str,
    buyer_1_name: str,
    start_date: str,
    expiry_date: str,
    property_type: str,
    geographic_location: str,
    brokerage_address: str = "",
    brokerage_city: str = "",
    brokerage_province: str = "ON",
    brokerage_postal_code: str = "",
    brokerage_phone: str = "",
    brokerage_fax: str = "",
    buyer_2_name: str = "",
    buyer_street_number: str = "",
    buyer_street_name: str = "",
    buyer_city: str = "",
    buyer_postal_code: str = "",
    commencement_time: str = "",
    property_type_2: str = "",
    geographic_location_2: str = "",
    schedules: str = "A",
    commission_percent: str = "",
    commission_words: str = "",
    lease_commission: str = "",
    holdover_days: str = "",
    agent_name: str = "",
    buyer_1_phone: str = "",
    buyer_2_phone: str = "",
    acknowledgement_date: str = "",
    schedule_a_content: str = "",
) -> dict:
    """
    Fill OREA Buyer Representation Agreement (Form 300)
    and return a path to the filled PDF.
    """
    try:
        data = {
            "brokerage_name": brokerage_name,
            "brokerage_address": brokerage_address,
            "brokerage_city": brokerage_city,
            "brokerage_province": brokerage_province,
            "brokerage_postal_code": brokerage_postal_code,
            "brokerage_phone": brokerage_phone,
            "brokerage_fax": brokerage_fax,
            "buyer_1_name": buyer_1_name,
            "buyer_2_name": buyer_2_name,
            "buyer_street_number": buyer_street_number,
            "buyer_street_name": buyer_street_name,
            "buyer_city": buyer_city,
            "buyer_postal_code": buyer_postal_code,
            "commencement_time": commencement_time,
            "start_date": start_date,
            "expiry_date": expiry_date,
            "property_type": property_type,
            "property_type_2": property_type_2,
            "geographic_location": geographic_location,
            "geographic_location_2": geographic_location_2,
            "schedules": schedules,
            "commission_percent": commission_percent,
            "commission_words": commission_words,
            "lease_commission": lease_commission,
            "holdover_days": holdover_days,
            "agent_name": agent_name,
            "buyer_1_phone": buyer_1_phone,
            "buyer_2_phone": buyer_2_phone,
            "acknowledgement_date": acknowledgement_date,
            "schedule_a_content": schedule_a_content,
        }

        pdf_bytes = fill_buyer_representation_pdf(data)
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pdf", delete=False
        ) as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            pdf_path = tmp_pdf.name

        return {
            "success": True,
            "document_pdf_path": pdf_path,
            "message": "Buyer representation agreement PDF successfully generated.",
            "form": "OREA Form 300",
            "buyer_1_name": buyer_1_name,
            "brokerage_name": brokerage_name,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate buyer representation agreement.",
        }


@mcp.tool()
def fill_confirmation_cooperation(
    buyer_1_name: str,
    seller_1_name: str,
    street_number: str,
    street_name: str,
    city: str,
    seller_brokerage_name: str,
    seller_agent_name: str,
    buyer_2_name: str = "",
    seller_2_name: str = "",
    unit: str = "",
    province: str = "ON",
    postal_code: str = "",
    seller_representation: str = "",
    coop_representation: str = "",
    coop_commission_type: str = "",
    coop_commission_mls_amount: str = "",
    coop_commission_other: str = "",
    coop_additional_comments: str = "",
    seller_additional_comments: str = "",
    seller_additional_comments_2: str = "",
    seller_brokerage_address: str = "",
    seller_brokerage_phone: str = "",
    seller_brokerage_fax: str = "",
    coop_brokerage_name: str = "",
    coop_brokerage_address: str = "",
    coop_brokerage_phone: str = "",
    coop_brokerage_fax: str = "",
    coop_agent_name: str = "",
) -> dict:
    """
    Fill OREA Confirmation of Co-operation and Representation (Form 320)
    and return a path to the filled PDF.
    """
    try:
        data = {
            "buyer_1_name": buyer_1_name,
            "buyer_2_name": buyer_2_name,
            "seller_1_name": seller_1_name,
            "seller_2_name": seller_2_name,
            "street_number": street_number,
            "street_name": street_name,
            "unit": unit,
            "city": city,
            "province": province,
            "postal_code": postal_code,
            "seller_representation": seller_representation,
            "coop_representation": coop_representation,
            "coop_commission_type": coop_commission_type,
            "coop_commission_mls_amount": coop_commission_mls_amount,
            "coop_commission_other": coop_commission_other,
            "coop_additional_comments": coop_additional_comments,
            "seller_additional_comments": seller_additional_comments,
            "seller_additional_comments_2": seller_additional_comments_2,
            "seller_brokerage_name": seller_brokerage_name,
            "seller_brokerage_address": seller_brokerage_address,
            "seller_brokerage_phone": seller_brokerage_phone,
            "seller_brokerage_fax": seller_brokerage_fax,
            "seller_agent_name": seller_agent_name,
            "coop_brokerage_name": coop_brokerage_name,
            "coop_brokerage_address": coop_brokerage_address,
            "coop_brokerage_phone": coop_brokerage_phone,
            "coop_brokerage_fax": coop_brokerage_fax,
            "coop_agent_name": coop_agent_name,
        }

        pdf_bytes = fill_confirmation_cooperation_pdf(data)
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pdf", delete=False
        ) as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            pdf_path = tmp_pdf.name

        return {
            "success": True,
            "document_pdf_path": pdf_path,
            "message": "Confirmation of co-operation PDF successfully generated.",
            "form": "OREA Form 320",
            "buyer_1_name": buyer_1_name,
            "seller_1_name": seller_1_name,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate confirmation of co-operation.",
        }


@mcp.tool()
def get_lease_field_guide() -> dict:
    """
    Get a complete guide of all fields required to fill
    the Ontario Standard Lease (Form 2229E). Use this
    to understand what information to collect from the
    user before calling fill_lease_agreement.
    """
    return {
        "form": "Ontario Standard Lease - Form 2229E",
        "required_fields": [
            {"field": "landlord_name", "description": "Full legal name of landlord or company"},
            {"field": "unit", "description": "Unit number of rental property"},
            {"field": "street_number", "description": "Street number of rental property"},
            {"field": "street_name", "description": "Street name of rental property"},
            {"field": "city", "description": "City of rental property"},
            {"field": "postal_code", "description": "Postal code of rental property"},
            {"field": "start_date", "description": "Tenancy start date in yyyy/mm/dd format"},
            {"field": "tenancy_type", "description": "fixed, monthly, or other"},
            {"field": "base_rent", "description": "Monthly base rent amount in dollars"},
            {"field": "total_rent", "description": "Total monthly rent including all services"},
            {"field": "rent_payable_to", "description": "Name rent cheques are made out to"},
            {"field": "payment_method", "description": "How rent is paid e.g. e-transfer, cheque"},
            {"field": "tenants_json", "description": "JSON array of tenant objects with first_name, last_name, email"},
        ],
        "optional_fields": [
            {"field": "end_date", "description": "Required if tenancy_type is fixed"},
            {"field": "parking_description", "description": "Description of parking if included"},
            {"field": "gas_included", "description": "Whether gas is included in rent"},
            {"field": "ac_included", "description": "Whether AC is included in rent"},
            {"field": "rent_deposit", "description": "Last month rent deposit amount"},
            {"field": "key_deposit", "description": "Refundable key deposit amount"},
            {"field": "smoking_rules", "description": "none or description of smoking rules"},
            {"field": "insurance_required", "description": "Whether tenant insurance is required"},
            {"field": "additional_terms_json", "description": "JSON array of additional term strings"},
        ],
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

    port = int(os.environ.get("MCP_PORT", 8001))
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
    )
