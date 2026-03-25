import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

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
    (Form 2229E) with the provided data and return the
    complete filled document as HTML.

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

        html = fill_lease(data)

        return {
            "success": True,
            "document_html": html,
            "message": "Lease agreement successfully generated. The document contains all sections of Ontario Form 2229E filled with the provided information.",
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
                "status": "coming_soon",
            },
        ],
        "total_supported": 1,
        "coming_soon": 1,
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
