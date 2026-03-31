from io import BytesIO
from pathlib import Path
import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject

# Ontario Standard Form of Lease — Form 2229E (2020/12) HTML generator

PDF_PATH = os.path.join(
    os.path.dirname(__file__), "2229e.pdf"
)



def fill_lease_pdf(data: dict) -> bytes:
    """Fill Ontario Form 2229E PDF and return bytes."""

    def g(key, default=""):
        value = data.get(key, default)
        if value is None:
            return default
        return value

    def s(value) -> str:
        if value is None:
            return ""
        return str(value)

    def boolish(value) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "y", "on"}
        return bool(value)

    def set_checkbox(fields: dict, yes_field: str, no_field: str, state: bool):
        fields[yes_field] = "/1" if state else "/Off"
        fields[no_field] = "/Off" if state else "/2"

    fields: dict[str, str] = {}

    # Section 1
    fields["form1[0].page1[0].body[0].section1[0].landlord[0].instructorInfo[0].instructorName[0].instrName[0]"] = s(g("landlord_name"))

    tenants = g("tenants") or []
    if not isinstance(tenants, list):
        tenants = []
    for idx in range(4):
        tenant = tenants[idx] if idx < len(tenants) and isinstance(tenants[idx], dict) else {}
        fields[f"form1[0].page1[0].body[0].section1[0].tenantsnames[0].tenant[{idx}].instructorInfo[0].instructorName[0].instrName[0]"] = s(tenant.get("last_name", ""))
        fields[f"form1[0].page1[0].body[0].section1[0].tenantsnames[0].tenant[{idx}].instructorInfo[0].instructorName[0].evalName[0]"] = s(tenant.get("first_name", ""))

    # Section 2
    fields["form1[0].page1[0].body[0].section2[0].busUnitNo[0]"] = s(g("unit"))
    fields["form1[0].page1[0].body[0].section2[0].busStreetNo[0]"] = s(g("street_number"))
    fields["form1[0].page1[0].body[0].section2[0].busStreetName[0]"] = s(g("street_name"))
    fields["form1[0].page1[0].body[0].section2[0].busCity[0]"] = s(g("city"))
    fields["form1[0].page1[0].body[0].section2[0].province[0]"] = s(g("province", "Ontario"))
    fields["form1[0].page1[0].body[0].section2[0].busPostalCode[0]"] = s(g("postal_code"))
    fields["form1[0].page1[0].body[0].section2[0].vehicle[0]"] = s(g("parking_description"))
    set_checkbox(
        fields,
        "form1[0].page1[0].body[0].section2[0].#subform[0].yes[0]",
        "form1[0].page1[0].body[0].section2[0].#subform[0].no[0]",
        boolish(g("is_condo", False)),
    )

    # Section 3
    fields["form1[0].page1[0].body[0].section3[0].unitNo[0]"] = s(g("landlord_unit"))
    fields["form1[0].page1[0].body[0].section3[0].streetNo[0]"] = s(g("landlord_street_number"))
    fields["form1[0].page1[0].body[0].section3[0].streetName[0]"] = s(g("landlord_street_name"))
    fields["form1[0].page1[0].body[0].section3[0].unitNo[1]"] = s(g("landlord_po_box"))
    fields["form1[0].page1[0].body[0].section3[0].city[0]"] = s(g("landlord_city"))
    fields["form1[0].page1[0].body[0].section3[0].province[0]"] = s(g("landlord_province", "Ontario"))
    fields["form1[0].page1[0].body[0].section3[0].postalCode[0]"] = s(g("landlord_postal_code"))
    set_checkbox(
        fields,
        "form1[0].page1[0].body[0].section3[0].question1[0].yes[0]",
        "form1[0].page1[0].body[0].section3[0].question1[0].no[0]",
        boolish(g("email_notices_agreed", False)),
    )
    email_values = [s(g("landlord_email"))]
    for tenant in tenants:
        if isinstance(tenant, dict):
            email_values.append(s(tenant.get("email", "")))
    fields["form1[0].page1[0].body[0].section3[0].question1[0].email[0]"] = ", ".join(
        [email for email in email_values if email]
    )
    set_checkbox(
        fields,
        "form1[0].page1[0].body[0].section3[0].question2[0].yes[0]",
        "form1[0].page1[0].body[0].section3[0].question2[0].no[0]",
        boolish(g("emergency_contact_provided", False)),
    )
    emergency_parts = [s(g("landlord_phone")), s(g("emergency_contact_info"))]
    fields["form1[0].page1[0].body[0].section3[0].question2[0].comment[0]"] = " | ".join([p for p in emergency_parts if p])

    # Section 4
    fields["form1[0].page1[0].body[0].section4[0].question1[0].date[0]"] = s(g("start_date"))
    tenancy_type = s(g("tenancy_type")).lower()
    fields["form1[0].page1[0].body[0].section4[0].question2[0].choice1[0]"] = "/1" if tenancy_type == "fixed" else "/Off"
    fields["form1[0].page1[0].body[0].section4[0].question2[0].choice2[0]"] = "/2" if tenancy_type == "monthly" else "/Off"
    fields["form1[0].page1[0].body[0].section4[0].question2[0].choice3[0]"] = "/3" if tenancy_type == "other" else "/Off"
    fields["form1[0].page1[0].body[0].section4[0].question2[0].date[0]"] = s(g("end_date"))
    fields["form1[0].page1[0].body[0].section4[0].question2[0].specify[0]"] = s(g("other_tenancy_description"))

    # Section 5
    fields["form1[0].page1[0].body[0].section5[0].text[0]"] = s(g("rent_payment_day"))
    rent_frequency = s(g("rent_frequency", "monthly")).lower()
    fields["form1[0].page1[0].body[0].section5[0].month[0]"] = "/1" if rent_frequency == "monthly" else "/Off"
    fields["form1[0].page1[0].body[0].section5[0].other[0]"] = "/2" if rent_frequency == "other" else "/Off"
    fields["form1[0].page1[0].body[0].section5[0].specify[0]"] = s(g("rent_frequency_other"))
    fields["form1[0].page1[0].body[0].section5[0].Table1[0].Row1[0].cost[0]"] = s(g("base_rent"))
    fields["form1[0].page1[0].body[0].section5[0].Table1[0].Row2[0].cost[0]"] = s(g("parking_rent"))

    extra_services = g("extra_services") or []
    if not isinstance(extra_services, list):
        extra_services = []
    for idx in range(3):
        extra = extra_services[idx] if idx < len(extra_services) and isinstance(extra_services[idx], dict) else {}
        fields[f"form1[0].page1[0].body[0].section5[0].Table1[0].Row4[{idx}].specify[0]"] = s(extra.get("label", ""))
        fields[f"form1[0].page1[0].body[0].section5[0].Table1[0].Row4[{idx}].cost[0]"] = s(extra.get("amount", ""))

    fields["form1[0].page1[0].body[0].section5[0].Table1[0].Row6[0].totalcost[0]"] = s(g("total_rent"))
    fields["form1[0].page1[0].body[0].section5[0].#subform[2].questionc[0]"] = s(g("rent_payable_to"))
    fields["form1[0].page1[0].body[0].section5[0].#subform[3].questiond[0]"] = s(g("payment_method"))
    fields["form1[0].page1[0].body[0].section5[0].questione[0].day[0]"] = s(g("partial_amount"))
    fields["form1[0].page1[0].body[0].section5[0].questione[0].date[0]"] = s(g("partial_payment_date"))
    fields["form1[0].page1[0].body[0].section5[0].questione[0].RWFrom[0]"] = s(g("partial_from_date"))
    fields["form1[0].page1[0].body[0].section5[0].questione[0].RWTO[0]"] = s(g("partial_to_date"))
    fields["form1[0].page1[0].body[0].section5[0].questionf[0].day[0]"] = s(g("nsf_charge"))

    # Section 6
    set_checkbox(fields, "form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].yes[0]", "form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].no[0]", boolish(g("gas_included", False)))
    set_checkbox(fields, "form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].yes[1]", "form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].no[1]", boolish(g("ac_included", False)))
    set_checkbox(fields, "form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].yes[2]", "form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].no[2]", boolish(g("storage_included", False)))

    laundry = s(g("laundry", "no")).lower()
    fields["form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].yes[3]"] = "/1" if laundry in {"yes", "no_charge", "pay_per_use"} else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].no[3]"] = "/2" if laundry == "no" else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].charge1[0]"] = "/1" if laundry == "no_charge" else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].payperuse1[0]"] = "/2" if laundry == "pay_per_use" else "/Off"

    guest_parking = s(g("guest_parking", "no")).lower()
    fields["form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].yes[4]"] = "/1" if guest_parking in {"yes", "no_charge", "pay_per_use"} else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].no[4]"] = "/2" if guest_parking == "no" else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].charge2[0]"] = "/1" if guest_parking == "no_charge" else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].payperuse2[0]"] = "/2" if guest_parking == "pay_per_use" else "/Off"

    other_services = g("other_services") or []
    if not isinstance(other_services, list):
        other_services = []
    for idx in range(3):
        service = other_services[idx] if idx < len(other_services) and isinstance(other_services[idx], dict) else {}
        included = boolish(service.get("included", False))
        fields[f"form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].other[{idx}].specify[0]"] = s(service.get("label", ""))
        fields[f"form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].other[{idx}].yes[0]"] = "/1" if included else "/Off"
        fields[f"form1[0].page1[0].body[0].section6[0].suggestions[0].service[0].other[{idx}].no[0]"] = "/2" if not included else "/Off"

    fields["form1[0].page1[0].body[0].section6[0].comment[0]"] = s(g("service_details"))

    electricity = s(g("electricity_responsibility", "tenant")).lower()
    heat = s(g("heat_responsibility", "landlord")).lower()
    water = s(g("water_responsibility", "tenant")).lower()
    fields["form1[0].page1[0].body[0].section6[0].utilities[0].Landlord[0]"] = "/1" if electricity == "landlord" else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].utilities[0].tenant[0]"] = "/2" if electricity == "tenant" else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].utilities[0].Landlord[1]"] = "/1" if heat == "landlord" else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].utilities[0].tenant[1]"] = "/2" if heat == "tenant" else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].utilities[0].Landlord[2]"] = "/1" if water == "landlord" else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].utilities[0].tenant[2]"] = "/2" if water == "tenant" else "/Off"
    fields["form1[0].page1[0].body[0].section6[0].comment2[0]"] = s(g("utility_details"))

    # Section 7-11
    has_discount = boolish(g("has_rent_discount", False))
    fields["form1[0].page1[0].body[0].section7[0].question2[0].yes[0]"] = "/Off" if has_discount else "/1"
    fields["form1[0].page1[0].body[0].section7[0].question2[0].c[0]"] = "/2" if has_discount else "/Off"
    fields["form1[0].page1[0].body[0].section7[0].comment[0]"] = s(g("rent_discount_description"))

    rent_deposit = g("rent_deposit", 0)
    has_rent_deposit = boolish(rent_deposit)
    fields["form1[0].page1[0].body[0].section8[0].question2[0].yes[0]"] = "/Off" if has_rent_deposit else "/1"
    fields["form1[0].page1[0].body[0].section8[0].question2[0].c[0]"] = "/2" if has_rent_deposit else "/Off"
    fields["form1[0].page1[0].body[0].section8[0].question2[0].deposit[0]"] = s(rent_deposit)

    key_deposit = g("key_deposit", 0)
    has_key_deposit = boolish(key_deposit)
    fields["form1[0].page1[0].body[0].section9[0].question2[0].yes[0]"] = "/Off" if has_key_deposit else "/1"
    fields["form1[0].page1[0].body[0].section9[0].question2[0].c[0]"] = "/2" if has_key_deposit else "/Off"
    fields["form1[0].page1[0].body[0].section9[0].question2[0].deposit[0]"] = s(key_deposit)
    fields["form1[0].page1[0].body[0].section9[0].comment[0]"] = s(g("key_deposit_description"))

    smoking_rules = s(g("smoking_rules", "none"))
    smoking_none = smoking_rules.strip().lower() == "none"
    fields["form1[0].page1[0].body[0].section10[0].question2[0].None[0]"] = "/1" if smoking_none else "/Off"
    fields["form1[0].page1[0].body[0].section10[0].question2[0].Smokingrules[0]"] = "/2" if not smoking_none else "/Off"
    fields["form1[0].page1[0].body[0].section10[0].comment[0]"] = "" if smoking_none else smoking_rules

    insurance_required = boolish(g("insurance_required", False))
    fields["form1[0].page1[0].body[0].section11[0].question2[0].choice1[0]"] = "/Off" if insurance_required else "/1"
    fields["form1[0].page1[0].body[0].section11[0].question2[0].choice2[0]"] = "/2" if insurance_required else "/Off"

    # Section 15
    additional_terms = g("additional_terms") or []
    if not isinstance(additional_terms, list):
        additional_terms = []
    has_additional_terms = len(additional_terms) > 0
    fields["form1[0].page1[0].body[0].section15[0].choice1[0]"] = "/Off" if has_additional_terms else "/1"
    fields["form1[0].page1[0].body[0].section15[0].choice1[1]"] = "/2" if has_additional_terms else "/Off"

    # Section 17 signatures
    fields["form1[0].page1[0].body[0].section17[0].landlords[0].signature1[0].name[0]"] = s(g("landlord_name"))
    for idx in range(2):
        tenant = tenants[idx] if idx < len(tenants) and isinstance(tenants[idx], dict) else {}
        full_name = (f"{tenant.get('first_name', '')} {tenant.get('last_name', '')}").strip()
        fields[f"form1[0].page1[0].body[0].section17[0].tenants[0].signature{idx + 1}[0].name[0]"] = full_name

    reader = PdfReader(PDF_PATH)
    writer = PdfWriter(clone_from=reader)

    for page in writer.pages:
        writer.update_page_form_field_values(page, fields)

    if reader.trailer.get("/Root") and reader.trailer["/Root"].get("/AcroForm"):
        writer._root_object["/AcroForm"].update(
            {
                "/NeedAppearances": BooleanObject(True)
            }
        )

    out = BytesIO()
    writer.write(out)
    out.seek(0)
    return out.read()

def fill_lease(data: dict) -> str:
    """Return a complete HTML document for Ontario's Standard Form of Lease with fields filled from ``data``."""

    def esc(x) -> str:
        if x is None:
            return ""
        s = str(x)
        return (
            s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def g(key, default=""):
        v = data.get(key, default)
        if v is None:
            return default
        return v

    def fill(x) -> str:
        return f'<span class="fill">{esc(x)}</span>' if x not in (None, "") else '<span class="fill">&nbsp;</span>'

    def money(x) -> str:
        try:
            if x is None:
                return ""
            f = float(x)
            return f"{f:,.2f}"
        except (TypeError, ValueError):
            return esc(x)

    def cb(on: bool) -> str:
        return "☑" if on else "☐"

    def laundry_checks(val: str):
        v = (val or "").lower()
        return (
            cb(v == "yes"),
            cb(v == "no"),
            cb(v == "no_charge"),
            cb(v == "pay_per_use"),
        )

    def parking_checks(val: str):
        return laundry_checks(val)

    landlord_name = g("landlord_name")
    landlord_unit = g("landlord_unit")
    landlord_street_number = g("landlord_street_number")
    landlord_street_name = g("landlord_street_name")
    landlord_po_box = g("landlord_po_box")
    landlord_city = g("landlord_city")
    landlord_province = g("landlord_province")
    landlord_postal_code = g("landlord_postal_code")
    landlord_phone = g("landlord_phone")
    landlord_email = g("landlord_email")
    email_notices = bool(g("email_notices_agreed", False))
    emergency_yes = bool(g("emergency_contact_provided", False))
    emergency_info = g("emergency_contact_info")

    unit = g("unit")
    street_number = g("street_number")
    street_name = g("street_name")
    city = g("city")
    postal_code = g("postal_code")
    rental_province = g("province", "")

    parking_description = g("parking_description")
    is_condo = bool(g("is_condo", False))

    start_date = g("start_date")
    tenancy_type = (g("tenancy_type") or "").lower()
    end_date = g("end_date")
    other_tenancy = g("other_tenancy_description")

    rent_payment_day = g("rent_payment_day")
    rent_frequency = (g("rent_frequency") or "").lower()
    rent_frequency_other = g("rent_frequency_other")

    base_rent = g("base_rent")
    parking_rent = g("parking_rent")
    extra_services = g("extra_services") or []
    if not isinstance(extra_services, list):
        extra_services = []
    total_rent = g("total_rent")
    rent_payable_to = g("rent_payable_to")
    payment_method = g("payment_method")

    has_partial = bool(g("has_partial_period", False))
    partial_amount = g("partial_amount")
    partial_payment_date = g("partial_payment_date")
    partial_from_date = g("partial_from_date")
    partial_to_date = g("partial_to_date")
    nsf_charge = g("nsf_charge")

    gas_included = bool(g("gas_included", False))
    ac_included = bool(g("ac_included", False))
    storage_included = bool(g("storage_included", False))
    laundry = g("laundry", "no")
    guest_parking = g("guest_parking", "no")
    other_services = g("other_services") or []
    if not isinstance(other_services, list):
        other_services = []
    service_details = g("service_details")

    elec = (g("electricity_responsibility") or "").lower()
    heat = (g("heat_responsibility") or "").lower()
    water = (g("water_responsibility") or "").lower()
    utility_details = g("utility_details")

    has_discount = bool(g("has_rent_discount", False))
    discount_desc = g("rent_discount_description")

    rent_deposit = float(g("rent_deposit") or 0)
    key_deposit = float(g("key_deposit") or 0)
    key_deposit_desc = g("key_deposit_description")

    smoking_rules = g("smoking_rules", "none")
    smoking_is_none = (smoking_rules or "").lower() == "none"

    insurance_required = bool(g("insurance_required", False))

    additional_terms = g("additional_terms") or []
    if not isinstance(additional_terms, list):
        additional_terms = []

    tenants = g("tenants") or []
    if not isinstance(tenants, list):
        tenants = []

    ly, ln, lnc, lpu = laundry_checks(laundry)
    gy, gn, gnc, gpu = parking_checks(guest_parking)

    fixed_on = tenancy_type == "fixed"
    monthly_on = tenancy_type == "monthly"
    other_term_on = tenancy_type == "other"

    freq_month = rent_frequency == "monthly"
    freq_other = rent_frequency == "other"

    # Section 1: four tenant rows
    trows = []
    for i in range(4):
        if i < len(tenants) and isinstance(tenants[i], dict):
            t = tenants[i]
            fn = t.get("first_name", "") or ""
            ln_ = t.get("last_name", "") or ""
        else:
            fn = ""
            ln_ = ""
        # Columns are Last Name, then First Name (per Form 2229E)
        trows.append(f"<tr><td>{fill(ln_)}</td><td>{fill(fn)}</td></tr>")
    tenant_rows_html = "\n".join(trows)

    # Tenant full names for signatures
    def tenant_full(ti: int) -> str:
        if ti >= len(tenants) or not isinstance(tenants[ti], dict):
            return ""
        t = tenants[ti]
        return esc(f"{t.get('first_name', '')} {t.get('last_name', '')}".strip())

    # Other services rows (up to 3)
    os_rows = []
    for i in range(3):
        if i < len(other_services) and isinstance(other_services[i], dict):
            lbl = esc(other_services[i].get("label", ""))
            inc = bool(other_services[i].get("included", False))
            os_rows.append(
                f"<tr><td>{fill(lbl)}</td><td style=\"text-align:center\">{cb(inc)}</td>"
                f"<td style=\"text-align:center\">{cb(not inc)}</td></tr>"
            )
        else:
            os_rows.append(
                f'<tr><td>{fill("")}</td><td style="text-align:center">{cb(False)}</td>'
                f'<td style="text-align:center">{cb(False)}</td></tr>'
            )
    other_services_html = "\n".join(os_rows)

    # Extra rent lines
    extra_lines = []
    for es in extra_services:
        if not isinstance(es, dict):
            continue
        extra_lines.append(
            f'<tr><td colspan="2">{esc(es.get("label", ""))}</td>'
            f'<td>${money(es.get("amount", 0))}</td></tr>'
        )
    if not extra_lines:
        extra_lines.append(
            f'<tr><td colspan="2">{fill("")}</td><td>{fill("")}</td></tr>'
        )
    extra_rent_rows = "\n".join(extra_lines)

    # Email block for section 3
    email_lines = [f"Landlord: {fill(landlord_email)}"]
    for i, t in enumerate(tenants):
        if isinstance(t, dict):
            email_lines.append(f"Tenant {i + 1}: {fill(t.get('email', ''))}")
    email_block = "<br/>".join(email_lines)

    # Additional terms numbered list
    if additional_terms:
        add_terms_body = "<ol>" + "".join(f"<li>{esc(x)}</li>" for x in additional_terms) + "</ol>"
        add_select_none = cb(False)
        add_select_attach = cb(True)
    else:
        add_terms_body = ""
        add_select_none = cb(True)
        add_select_attach = cb(False)

    opening_note = (
        "This tenancy agreement (or lease) is required for tenancies entered into on March 1, 2021 or later. "
        "It does not apply to care homes, sites in mobile home parks and land lease communities, most social housing, "
        "certain other special tenancies or co-operative housing (see Part A of General Information)."
        "<br/><br/>"
        "Residential tenancies in Ontario are governed by the Residential Tenancies Act, 2006. This agreement cannot take away a right "
        "or responsibility under the Residential Tenancies Act, 2006."
        "<br/><br/>"
        "Under the Ontario Human Rights Code, everyone has the right to equal treatment in housing without discrimination or "
        "harassment."
        "<br/><br/>"
        "All sections of this agreement are mandatory and cannot be changed."
    )

    def footer(n: int) -> str:
        return f"""<div class="page-footer">
  <div class="footer-grid">
    <span>2229E (2020/12) © Queen's Printer for Ontario, 2020</span>
    <span class="footer-center">Disponible en français</span>
    <span class="footer-right">Page {n} of 14</span>
  </div>
</div>"""

    def page_wrap(num: int, inner: str) -> str:
        return f'<div class="page">{inner}{footer(num)}</div>'

    # Appendix pages 9–14 (verbatim from Form 2229E static PDF text)
    appendix_p9 = """<div class="section-band">Appendix: General Information</div>
<p>This Appendix sets out basic information for landlords and tenants. It is not intended as legal advice, and it is not an official interpretation of the Residential Tenancies Act, 2006 (the Act). Please refer to the Act for the specific rules.</p>
<p>The Landlord and Tenant Board also provides information about landlords' and tenants' rights and responsibilities under the Act.</p>
<p><strong>Landlord and Tenant Board:</strong><br/>
Toll free: 1-888-332-3234<br/>
Toronto area: 416-645-8080<br/>
TTY: Bell Relay Service at 1-800-855-0511<br/>
Website: www.tribunalsontario.ca/ltb/</p>
<div class="section-band">A. When to Use This Form</div>
<p>This form (standard form of lease) must be used for most residential tenancy agreements (leases).</p>
<p><strong>This form should not be used for:</strong></p>
<ul>
<li>care homes,</li>
<li>sites in mobile home parks or land lease communities,</li>
<li>social and supportive housing that is exempt from the rent increase guideline (see the regulation under the Act for specific exemptions),</li>
<li>member units in co-operative housing, and</li>
<li>any other accommodation that is exempt from the Act (see Section 5 of the Act).</li>
</ul>
<div class="section-band">B. Change of Landlord</div>
<p>A new landlord has the same rights and duties as the previous landlord. A new landlord must follow all the terms of this agreement unless the tenant and new landlord agree to other terms. A new landlord should provide the tenant with their legal name and address.</p>
<div class="section-band">C. Renewing a Tenancy Agreement (Part V of the Act)</div>
<p>If the landlord and tenant agree that the tenancy will last for a specific period of time, this is called a fixed term tenancy. This is because both the start and end date are set out in the tenancy agreement.</p>
<p>The end of an agreement does not mean the tenant has to move out or sign a renewal or new agreement in order to stay. The rules of the agreement will still apply and the tenant still has the right to stay:</p>
<ul>
<li>as a monthly tenant, if the agreement was for a fixed term or monthly tenancy,</li>
<li>as a weekly tenant, if the agreement was for a weekly tenancy, or</li>
<li>as a daily tenant, if the agreement was for a daily tenancy.</li>
</ul>
<p>The landlord and tenant can also agree to renew the agreement for another fixed term or enter into a new agreement. In any case, changes to the rent must follow the rules under the Act (see Part I below for further information).</p>
<div class="section-band">D. Ending the Tenancy (Part V of the Act)</div>
<p>The landlord or tenant must follow the rules of the Act when ending a tenancy.</p>
<p><strong>When the tenant can end the tenancy</strong></p>
<p>The tenant can end a tenancy by giving the landlord proper notice using the appropriate Landlord and Tenant Board form. They must give:</p>
<ul>
<li>at least 60 days' notice if they have a monthly or fixed term tenancy, or</li>
<li>at least 28 days' notice if they have a daily or weekly tenancy.</li>
</ul>"""

    appendix_p10 = """<p>For a fixed term tenancy, the notice cannot be effective before the last day of the fixed term. For a monthly or weekly tenancy, the notice must be effective on the last day of a rental period (e.g. month or week).</p>
<p>In certain situations, a tenant who has experienced sexual or domestic violence can give 28 days' notice to end the tenancy at any time, even if the tenant has a fixed term agreement (e.g., one year agreement). They must use the notice form approved by the Landlord and Tenant Board.</p>
<p><strong>When the landlord can end the tenancy</strong></p>
<p>The landlord can only give the tenant notice to end the tenancy in certain situations. These situations are set out in the Act. The landlord cannot evict the tenant unless the landlord follows the proper rules. These rules are set out in the Act. In most cases, the landlord must give proper notice to end the tenancy using the right form. Forms are available on the Landlord and Tenant Board's website.</p>
<p>If the landlord gives a tenant notice to end the tenancy, the tenant does not have to move out.</p>
<p>The landlord can give the tenant notice to end the tenancy in certain situations where the tenant is at fault. Examples include:</p>
<ul>
<li>tenant does not pay the full rent when it is due,</li>
<li>tenant causes damage to the rental unit or building, and</li>
<li>tenant substantially interferes with the reasonable enjoyment of other tenants or the landlord.</li>
</ul>
<p>The landlord may also give notice to end a tenancy in certain situations that are not the tenant's fault, but only at the end of the term or rental period. In these cases, landlords must still give proper notice, and tenants may be entitled to compensation and/or the right to return to the unit. Examples include:</p>
<ul>
<li>landlord or purchaser needs the unit for themselves, an immediate family member, or caregiver, and</li>
<li>landlord needs to do extensive repairs or renovations that require a building permit and vacant possession of the unit.</li>
</ul>
<p>If the tenant does not move out, the landlord must apply to the Landlord and Tenant Board in order to evict the tenant. The Landlord and Tenant Board will hold a hearing and decide if the tenancy should end. Both the landlord and the tenant can come to the hearing and explain their side to the Landlord and Tenant Board. If the Landlord and Tenant Board orders an eviction, the eviction order can only be enforced by the Sheriff (Court Enforcement Officer).</p>
<p>It is an offence for the landlord to evict a tenant without following this process. If convicted, the landlord could face a fine of up to $50,000 (for an individual) or $250,000 (for a corporation).</p>
<p><strong>If the Landlord and Tenant agree to end the tenancy</strong></p>
<p>The tenant and landlord can agree to end a tenancy at any time by using the proper Landlord and Tenant Board form. Some landlords may ask the tenant to sign that form when signing the tenancy agreement (lease). In most cases, an agreement to end a tenancy signed at the beginning of the tenancy agreement is unenforceable and the tenant does not have to move out.</p>
<p>There is more information on how to end a tenancy and reasons for eviction in the Act and in brochures on the Landlord and Tenant Board website.</p>
<div class="section-band">E. Giving Notices and Documents (Part XII of the Act)</div>
<p>The landlord and tenant have to deliver some official notices and other documents in writing. These notices and documents can be:</p>
<ul>
<li>hand delivered,</li>
<li>left in a mail box or a place where mail is ordinarily delivered, or</li>
<li>mailed (this will count as delivered five days after mailing).</li>
</ul>
<p>There are also other ways to serve notices and documents. For more information, contact the Landlord and Tenant Board or see the Rules of Practice on its website.</p>"""

    appendix_p11 = """<div class="section-band">F. Rent and Rent Receipts (Part VII of the Act)</div>
<p>Rent is the amount the tenant pays to the landlord to occupy the rental unit and receive services or facilities agreed to in this agreement.</p>
<p>The tenant must pay their rent on time. If they do not, the landlord can give them notice to end the tenancy.</p>
<p>If the tenant asks for a receipt for rent or any payment or deposit, the landlord must give them one for free. This also applies to a former tenant who asks for a receipt within 12 months after the end of their tenancy.</p>
<div class="section-band">G. Rent Discounts (Part VII of Act)</div>
<p>The landlord can offer the tenant a discount for paying rent on or before the date it is due. This discount can be up to two per cent of the lawful rent.</p>
<p>The landlord can also offer rent-free periods or discounts in one of three ways:</p>
<ul>
<li>Rent-free periods of up to three months within any 12-month period,</li>
<li>A discount of up to one month's rent spread evenly over eight months, or</li>
<li>A discount of up to two months' rent, with up to one month's rent spread evenly over the first seven months, and up to one month's rent discounted in one of the last five months.</li>
</ul>
<p>These types of discounts must be agreed to in writing.</p>
<div class="section-band">H. Deposits (Part VII of the Act)</div>
<p>The landlord can only collect a deposit for the last month's rent and a refundable key deposit. The tenant does not have to provide any other form of deposit, such as pet or damage deposits. If the tenant pays anything more, the tenant can apply to the Landlord and Tenant Board to get the money back.</p>
<p><strong>Rent deposit (i.e. last month's rent):</strong> The landlord can require a rent deposit on or before the tenant enters into the tenancy agreement. The landlord must apply this money to the rent for the last period of the tenancy. The rent deposit must not be more than one month's rent or the rent for one rental period (e.g., one week in a weekly tenancy), whichever is less.</p>
<p>The landlord must pay the tenant interest on the rent deposit every year. If the rent increases after the tenant has paid a rent deposit, the landlord can require the tenant to top-up the rent deposit so that it is the same as the new rent. The landlord can use the interest on the rent deposit to top-up the rent deposit.</p>
<p>If the landlord is unable to let the tenant move into the rental unit, the landlord must return the deposit, unless the tenant agrees to rent a different unit.</p>
<p><strong>Key deposit:</strong> If the landlord collects a deposit for key(s), remote entry devices or cards, the landlord must return the deposit when the tenant gives back their key(s) at the end of the tenancy.</p>
<p>The landlord can charge the tenant for additional keys that the tenant requests (for example, if the tenant wants an extra key or if the tenant has lost their key), but the charge cannot be more than actual cost of the keys. This is not a key deposit.</p>
<div class="section-band">I. Rent Increases and Decreases (Part VII of the Act)</div>
<p>Normally, the landlord can increase the rent only once every 12 months. The landlord must use the proper Landlord and Tenant Board form and give the tenant at least 90 days' notice before the rent increase is to take effect.</p>
<p><strong>Guideline Rent Increases</strong></p>
<p>In most cases, the rent can be increased by no more than the rent increase guideline unless the Landlord and Tenant Board approves a rent increase above the guideline. The guideline for each year can be found on the Landlord and Tenant Board's website. Some newer units are not subject to the rent increase guideline, including:</p>
<ul>
<li>A unit in a new building, if no part of the building was occupied for residential purposes on or before November 15, 2018;</li>
<li>A unit in a new addition to an existing building, if no part of the addition was occupied for residential purposes on or before November 15, 2018; and,</li>
<li>A new second unit in an existing house, such as a basement apartment, that was created after November 15, 2018 and that meets the requirements set out in the Act.</li>
</ul>"""

    appendix_p12 = """<p><strong>Rent Increases above the Guideline</strong></p>
<p>The landlord can apply to the Landlord and Tenant Board for approval to raise the rent by more than the rent increase guideline. Affected tenants can oppose this application at the Landlord and Tenant Board.</p>
<p>This kind of rent increase is called an above-guideline rent increase. The Landlord and Tenant Board can allow this kind of rent increase if:</p>
<ul>
<li>the landlord's municipal taxes and charges have increased significantly,</li>
<li>the landlord has done major repairs or renovations, or</li>
<li>the costs of external security services (i.e. not performed by the landlord's employees) have increased, or external security services are being provided for the first time.</li>
</ul>
<p>The landlord and tenant can also agree to an above-guideline rent increase, if the landlord agrees to renovate or add a new service for the tenant. Certain rules apply.</p>
<p><strong>Rent Reductions:</strong></p>
<p>The landlord must reduce the rent if:</p>
<ul>
<li>the municipal property tax goes down by more than 2.49 per cent, or</li>
<li>the rent was increased above the guideline to pay for repairs or renovations and the costs have been fully paid for (this only applies to tenants who were living in the unit when the above guideline rent increase happened).</li>
</ul>
<p>The tenant can apply to the Landlord and Tenant Board to reduce their rent if:</p>
<ul>
<li>municipal property taxes or charges on the rental property go down,</li>
<li>the landlord reduced or removed a service without reducing the rent, or</li>
<li>the landlord did not keep a promise they made in an agreement for a rent increase above the guideline.</li>
</ul>
<div class="section-band">J. Maintenance and Repairs (Part III, IV, V and XIV of the Act)</div>
<p>The landlord must keep the rental unit and property in good repair and comply with all health, safety and maintenance standards. This includes the maintenance and repair of things that came with the unit, such as appliances, and of common areas, such as parking lots, elevators, and hallways.</p>
<p>The tenant must pay their rent, even if they have problems with the maintenance and repair of their unit or property. If the tenant is having a maintenance or repair problem, the tenant should let the landlord know. If needed, the tenant can apply to the Landlord and Tenant Board.</p>
<p>The tenant is responsible for any damage to the rental property caused by the tenant, the tenant's guest or another person who lives in the rental unit. This applies to any damage caused on purpose or by not being careful enough. This does not include damage that results from normal use of the rental unit over time ("wear and tear"). The landlord can apply to the Landlord and Tenant Board if the tenant has not repaired such damage.</p>
<p>The tenant is responsible for ordinary cleanliness of the rental unit, except for any cleaning the landlord agreed to do.</p>
<div class="section-band">K. Vital Services (Part I and III of the Act)</div>
<p>"Vital services" are hot or cold water, fuel, electricity, gas and heat.</p>
<p>The landlord must ensure that a rental unit has heating equipment capable of maintaining a minimum temperature of 20° Celsius from September 1 to June 15. Some municipal by-laws may have stricter requirements.</p>
<p>The landlord cannot withhold or shut off the reasonable supply of a vital service, care service or food that the landlord must supply under the tenancy agreement. If a vital service is cut-off because the landlord failed to pay their bill, the landlord is considered to have withheld that service. However, if a vital service is cut-off or disconnected because the tenant failed to pay their own utility bill, the tenant cannot claim that the landlord withheld a vital service.</p>
<p>The landlord cannot deliberately interfere with the reasonable supply of any vital service, care service or food, whether or not the landlord is obligated to supply it under the tenancy agreement.</p>"""

    appendix_p13 = """<div class="section-band">L. Harassment (Part III and IV of the Act)</div>
<p>It is against the law for the landlord (or anyone acting for the landlord, such as a superintendent or property manager) to harass the tenant, or for the tenant to harass the landlord. If the landlord or the tenant is experiencing harassment they can apply to the Landlord and Tenant Board.</p>
<div class="section-band">M. Discrimination</div>
<p>If the landlord (or anyone acting for the landlord) discriminates against the tenant based on prohibited grounds of discrimination under the Ontario Human Rights Code (the Code), they may be violating the tenant's rights under the Code. The Landlord and Tenant Board may be able to consider discrimination if it relates to an application under the Residential Tenancies Act, 2006. In other situations, the tenant may have to take their case to the Human Rights Tribunal of Ontario.</p>
<div class="section-band">N. Landlord's Entry into Rental Unit (Part III of the Act)</div>
<p>The tenant is entitled to reasonable enjoyment of the rental unit (e.g. quiet enjoyment, reasonable privacy, freedom from unreasonable disturbance and exclusive use of the rental unit).</p>
<p>The landlord can enter the rental unit with 24 hours' written notice only for the following reasons:</p>
<ul>
<li>make repairs,</li>
<li>inspect the unit to see if repairs are needed, if the inspection is reasonable,</li>
<li>show the rental unit to a possible buyer, insurer or mortgage lender,</li>
<li>let a real estate agent show the unit to a possible buyer,</li>
<li>have a property inspection done before converting the residential building into a condominium, or</li>
<li>for any reasonable purpose listed in the tenancy agreement.</li>
</ul>
<p>The written notice must include the reason for the entry and state the date and time (between 8 a.m. and 8 p.m.) that the landlord will enter the unit. With proper notice, the landlord can enter the unit when the tenant is not at home.</p>
<p>The landlord does not need to give a notice to enter:</p>
<ul>
<li>in case of emergency,</li>
<li>if the tenant consents to entry,</li>
<li>if the tenancy agreement requires the landlord to clean the unit, or</li>
<li>if the tenancy is coming to an end and the landlord wants to show the unit to a potential new tenant – the landlord can only show the unit between 8:00 a.m. and 8:00 p.m. and must make a reasonable effort to let the tenant know when this will happen.</li>
</ul>
<div class="section-band">O. Locks (Part III and IV of the Act)</div>
<p>The landlord cannot change the locks of the rental unit unless the landlord gives the new keys to the tenant. The tenant cannot change the locks of the rental unit without the consent of the landlord.</p>
<div class="section-band">P. Assign or Sublet (Part VI of the Act)</div>
<p>The tenant may assign or sublet the rental unit to another person only with the consent of the landlord. The landlord cannot arbitrarily or unreasonably withhold consent to a potential assignee or sublet of the rental unit.</p>
<p><strong>1. Assignment:</strong> In an assignment, the tenant transfers their right to occupy the rental unit to someone else. The new person takes the place of the tenant, and the tenancy agreement stays the same.</p>
<p><strong>2. Sublet:</strong> A sublet occurs when the tenant moves out of the rental unit, lets another person (the 'sub-tenant') live there until a specified date, and can return to live in the unit before the tenancy ends. The tenancy agreement and the landlord-tenant relationship do not change.</p>
<p>A tenant who sublets a rental unit cannot:</p>
<ul>
<li>charge a higher rent than the landlord does for the rental unit,</li>
<li>collect any additional fees for subletting the rental unit, or</li>
<li>charge the sub-tenant for additional goods or services.</li>
</ul>"""

    appendix_p14 = """<div class="section-band">Q. Guests (Part III of the Act)</div>
<p>The landlord cannot stop tenants from having guests, require the tenant to notify the landlord or get the landlord's permission before having guests. The landlord cannot charge extra fees or raise the rent due to guests in the rental unit. However, the tenant is responsible for the behaviour of their guests.</p>
<p>The landlord cannot prevent the tenant from having a roommate, as long as municipal by-laws on occupancy standards are respected.</p>
<p>If a tenant rents their whole unit to someone else (e.g. short-term rental), this person is not a "guest". The tenant may have to get the landlord's permission.</p>
<div class="section-band">R. Pets (Part III of the Act)</div>
<p>A tenancy agreement cannot prohibit animals in the rental unit or in or around the residential building.</p>
<p>There are some cases where the landlord can apply to the Landlord and Tenant Board to evict a tenant who has a pet. These are some common examples:</p>
<ul>
<li>the pet makes too much noise, damages the unit or causes other tenants to have allergic reactions,</li>
<li>the breed or species is inherently dangerous, or</li>
<li>the rules of the condominium corporation do not allow pets.</li>
</ul>
<div class="section-band">S. Smoking (Part V of the Act)</div>
<p>The Act does not discuss smoking in a rental unit. The landlord and tenant can use Section 10 of this lease to agree to either allow or prohibit smoking in the unit, and/or on the landlord's property.</p>
<p>Even if the lease doesn't prohibit smoking, the landlord may apply to the Landlord and Tenant Board to end the tenancy if the smoking:</p>
<ul>
<li>substantially interferes with reasonable enjoyment of the landlord or other tenants,</li>
<li>causes undue damage,</li>
<li>impairs safety, or</li>
<li>substantially interferes with another lawful right, privilege or interest of the landlord.</li>
</ul>
<p>If the tenant believes that other people smoking in their building affects their health or safety, contravenes maintenance standards, or substantially interferes with their reasonable enjoyment of the rental unit, they should discuss it with their landlord before contacting the Landlord and Tenant Board.</p>
<div class="section-band">T. Smoke and Carbon Monoxide Alarms</div>
<p>The landlord must provide the rental unit with working smoke alarms and, where applicable, carbon monoxide alarms.</p>
<p>The landlord is responsible for keeping smoke and carbon monoxide alarms in working condition, which includes replacing the batteries. The tenant must not disconnect or tamper with any smoke or carbon monoxide alarm and must notify the landlord immediately of any alarms not working properly.</p>
<div class="section-band">U. Resolving Disputes</div>
<p>The landlord and tenant are required to follow the law. If they have problems or disagreements, the landlord and tenant should first discuss the issue and attempt to resolve it themselves. If the landlord or tenant feels that the other is not obeying the law, they may contact the Landlord and Tenant Board for information about their rights and responsibilities, including whether they may apply to the Landlord and Tenant Board to resolve the dispute.</p>
<p class="guide-link"><strong>Guide to the Standard Lease</strong><br/>www.ontario.ca/standardlease</p>"""

    css = """<style>
html, body { margin: 0; padding: 0; background: #fff; color: #000; font-family: Arial, Helvetica, sans-serif; font-size: 10.5pt; line-height: 1.35; }
.doc-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; border-bottom: 1px solid #000; padding-bottom: 8px; }
.doc-header .ont { font-size: 14pt; }
.doc-header .title-right { text-align: right; max-width: 75%; }
.section-band { background: #D9D9D9; font-weight: bold; border-top: 2px solid #000; padding: 6px 8px; margin-top: 10px; }
.note-box { background: #F0F0F0; border-top: 1px solid #CCCCCC; border-bottom: 1px solid #CCCCCC; padding: 10px 12px; margin: 10px 0; }
.note-inline { font-size: 9pt; margin-top: 6px; }
table.form { border-collapse: collapse; width: 100%; margin: 8px 0; }
table.form td, table.form th { border: 1px solid #000; padding: 6px 8px; vertical-align: top; }
.fill { border-bottom: 1px solid #000; min-height: 1em; display: inline-block; min-width: 2em; }
.sig-table td, .sig-table .sig-row td { height: 48px; vertical-align: bottom; }
.page { position: relative; padding-bottom: 36px; page-break-after: always; }
.page:last-child { page-break-after: auto; }
.page-footer { position: absolute; bottom: 0; left: 0; right: 0; font-size: 9pt; padding-top: 8px; border-top: 1px solid #ccc; }
.footer-grid { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 8px; }
.footer-center { text-align: center; grid-column: 2; }
.footer-right { text-align: right; grid-column: 3; }
ul.compact { margin: 6px 0; padding-left: 22px; }
p { margin: 6px 0; }
@media print {
  .page { page-break-after: always; }
  .page:last-child { page-break-after: auto; }
  @page { margin: 10mm; size: letter; }
}
</style>"""

    p1 = f"""
<div class="doc-header">
  <div class="ont">Ontario ✦</div>
  <div class="title-right"><strong>Residential Tenancy Agreement (Standard Form of Lease)</strong></div>
</div>
<div class="note-box"><strong>Note</strong><br/>{opening_note}</div>
<div class="section-band">1. Parties to the Agreement</div>
<p>Residential Tenancy Agreement between:</p>
<table class="form">
<tr><th colspan="2">Landlord(s)</th></tr>
<tr><td colspan="2">Landlord's Legal Name<br/>{fill(landlord_name)}</td></tr>
<tr><td colspan="2" class="note-inline"><strong>Note:</strong> See Part B in General Information</td></tr>
<tr><th colspan="2">and Tenant(s)</th></tr>
<tr><th>Last Name</th><th>First Name</th></tr>
{tenant_rows_html}
</table>
<div class="section-band">2. Rental Unit</div>
<p>The landlord will rent to the tenant the rental unit at:</p>
<table class="form">
<tr>
<td>Unit (e.g., unit 1 or basement unit)<br/>{fill(unit)}</td>
<td>Street Number<br/>{fill(street_number)}</td>
<td>Street Name<br/>{fill(street_name)}</td>
</tr>
<tr>
<td>City/Town<br/>{fill(city)}</td>
<td>Province<br/>{fill(rental_province)}</td>
<td>Postal Code<br/>{fill(postal_code)}</td>
</tr>
<tr><td colspan="3">Number of vehicle parking spaces and description (e.g., indoor/outdoor, location)<br/>{fill(parking_description)}</td></tr>
<tr><td colspan="3">The rental unit is a unit in a condominium.<br/>
{cb(is_condo)} Yes &nbsp; {cb(not is_condo)} No<br/>
If yes, the tenant agrees to comply with the condominium declaration, by-laws and rules, as provided by the landlord.</td></tr>
</table>
"""

    p2 = f"""
<div class="section-band">3. Contact Information</div>
<p><strong>Address for Giving Notices or Documents to the Landlord</strong></p>
<table class="form">
<tr>
<td>Unit<br/>{fill(landlord_unit)}</td>
<td>Street Number<br/>{fill(landlord_street_number)}</td>
<td>Street Name<br/>{fill(landlord_street_name)}</td>
<td>PO Box<br/>{fill(landlord_po_box)}</td>
</tr>
<tr>
<td>City/Town<br/>{fill(landlord_city)}</td>
<td>Province<br/>{fill(landlord_province)}</td>
<td colspan="2">Postal Code/ZIP Code<br/>{fill(landlord_postal_code)}</td>
</tr>
</table>
<p>Both the landlord and tenant agree to receive notices and documents by email, where allowed by the Landlord and Tenant Board's Rules of Procedure.<br/>
{cb(email_notices)} Yes &nbsp; {cb(not email_notices)} No</p>
<p>If yes, provide email addresses:<br/>{email_block}</p>
<p>The landlord is providing phone and/or email contact information for emergencies or day-to-day communications:<br/>
{cb(emergency_yes)} Yes &nbsp; {cb(not emergency_yes)} No</p>
<p>If yes, provide information:<br/>Phone: {fill(landlord_phone)}<br/>{fill(emergency_info)}</p>
<p class="note-inline"><strong>Note:</strong> See Part B and E in General Information</p>
<div class="section-band">4. Term of Tenancy Agreement</div>
<p>This tenancy starts on:<br/>Date (yyyy/mm/dd) {fill(start_date)}</p>
<p>This tenancy agreement is for: (select an option below and fill in details as needed)</p>
<p>{cb(fixed_on)} a fixed length of time ending on:<br/>Date (yyyy/mm/dd) {fill(end_date if fixed_on else '')}</p>
<p>{cb(monthly_on)} a monthly tenancy</p>
<p>{cb(other_term_on)} other (such as daily, weekly, please specify):<br/>{fill(other_tenancy if other_term_on else '')}</p>
<p class="note-inline"><strong>Note:</strong> The tenant does not have to move out at the end of the term. See Parts C and D in General Information.</p>
"""

    p3 = f"""
<div class="section-band">5. Rent</div>
<p>a) Rent is to be paid on the (e.g., first, second, last) {fill(rent_payment_day)} day of each (select one):<br/>
{cb(freq_month)} Month &nbsp; {cb(freq_other)} Other (e.g., weekly) {fill(rent_frequency_other if freq_other else '')}</p>
<p>b) The tenant will pay the following rent:</p>
<table class="form">
<tr><th>Description</th><th></th><th>Amount</th></tr>
<tr><td colspan="2">Base rent for the rental unit</td><td>${money(base_rent)}</td></tr>
<tr><td colspan="2">Parking (if applicable)</td><td>${money(parking_rent)}</td></tr>
{extra_rent_rows}
<tr><th colspan="2">Total Rent (Lawful Rent)</th><th>${money(total_rent)}</th></tr>
</table>
"""

    p4 = f"""
<p>This is the lawful rent for the unit, subject to any rent increases allowed under the Residential Tenancies Act, 2006. For example, the landlord and tenant may agree to a seasonal rent increase for additional services of air conditioning or a block heater plug-in. This amount does not include any rent discounts (see Section 7 and Part G in General Information).</p>
<p>c) Rent is payable to:<br/>{fill(rent_payable_to)}</p>
<p>d) Rent will be paid using the following methods:<br/>{fill(payment_method)}</p>
<p class="note-inline"><strong>Note:</strong> The tenant cannot be required to pay rent by post-dated cheques or automatic payments, but can choose to do so.</p>
<p>e) If the first rental period (e.g., month) is a partial period, the tenant will pay a partial rent of ${money(partial_amount) if has_partial else '_______'} on<br/>
Date (yyyy/mm/dd) {fill(partial_payment_date if has_partial else '')}. This partial rent covers the rental of the unit from<br/>
Date (yyyy/mm/dd) {fill(partial_from_date if has_partial else '')} to<br/>
Date (yyyy/mm/dd) {fill(partial_to_date if has_partial else '')}.</p>
<p>f) If the tenant's cheque is returned because of non-sufficient funds (NSF), the tenant will have to pay the landlord's administration charge of ${money(nsf_charge)} plus any NSF charges made by the landlord's bank.</p>
<p class="note-inline"><strong>Note:</strong> The landlord's administration charge for an NSF cheque cannot be more than $20.00</p>
<div class="section-band">6. Services and Utilities</div>
<p>The following services are included in the lawful rent for the rental unit, as specified:</p>
<table class="form">
<tr><th>Service</th><th>Yes</th><th>No</th><th>No Charge</th><th>Pay Per use</th></tr>
<tr><td>Gas</td><td>{cb(gas_included)}</td><td>{cb(not gas_included)}</td><td></td><td></td></tr>
<tr><td>Air conditioning</td><td>{cb(ac_included)}</td><td>{cb(not ac_included)}</td><td></td><td></td></tr>
<tr><td>Additional storage space</td><td>{cb(storage_included)}</td><td>{cb(not storage_included)}</td><td></td><td></td></tr>
<tr><td>On-Site Laundry</td><td>{ly}</td><td>{ln}</td><td>{lnc}</td><td>{lpu}</td></tr>
<tr><td>Guest Parking</td><td>{gy}</td><td>{gn}</td><td>{gnc}</td><td>{gpu}</td></tr>
</table>
<table class="form">
<tr><th>Other (specify)</th><th>Yes</th><th>No</th></tr>
{other_services_html}
</table>
<p>Provide details about services or list any additional services if needed (if necessary add additional pages):<br/>{fill(service_details)}</p>
"""

    p5 = f"""
<p><strong>The following utilities are the responsibility of:</strong></p>
<table class="form">
<tr><th>Utility</th><th>Landlord</th><th>Tenant</th></tr>
<tr><td>Electricity</td><td>{cb(elec == 'landlord')}</td><td>{cb(elec == 'tenant')}</td></tr>
<tr><td>Heat</td><td>{cb(heat == 'landlord')}</td><td>{cb(heat == 'tenant')}</td></tr>
<tr><td>Water</td><td>{cb(water == 'landlord')}</td><td>{cb(water == 'tenant')}</td></tr>
</table>
<p>If the tenant is responsible for any utilities, provide details of the arrangement, e.g. tenant sets up account with and pays the utility provider, tenant pays a portion of the utility costs (if necessary add additional pages):<br/>{fill(utility_details)}</p>
<div class="section-band">7. Rent Discounts</div>
<p>Select one:</p>
<p>{cb(not has_discount)} There is no rent discount.<br/>
or<br/>
{cb(has_discount)} The lawful rent will be discounted as follows:<br/>
Provide description of rent discount (if necessary add additional pages):<br/>{fill(discount_desc if has_discount else '')}</p>
<p class="note-inline"><strong>Note:</strong> See Part G in General Information for what types of discounts are allowed.</p>
<div class="section-band">8. Rent Deposit</div>
<p>Select one:</p>
<p>{cb(rent_deposit == 0)} A rent deposit is not required.<br/>
or<br/>
{cb(rent_deposit != 0)} The tenant will pay a rent deposit of ${money(rent_deposit) if rent_deposit else '_______'}. This can only be applied to the rent for the last rental period of the tenancy.</p>
<p class="note-inline"><strong>Note:</strong> This amount cannot be more than one month's rent or the rent for one rental period (e.g., one week in a weekly tenancy), whichever is less. This cannot be used as a damage deposit. The landlord must pay the tenant interest on the rent deposit every year. See Part H in General Information.</p>
<div class="section-band">9. Key Deposit</div>
<p>Select one:</p>
<p>{cb(key_deposit == 0)} A key deposit is not required.<br/>
or<br/>
{cb(key_deposit != 0)} The tenant will pay a refundable key deposit of ${money(key_deposit) if key_deposit else '_______'} to cover the cost of replacing the keys, remote entry devices or cards if they are not returned to the landlord at the end of the tenancy.</p>
<p>If a refundable key deposit is required, provide description and number of keys, access cards and remote entry devices:<br/>{fill(key_deposit_desc if key_deposit else '')}</p>
<p class="note-inline"><strong>Note:</strong> The key deposit cannot be more than the expected replacement cost. See Part H in General Information.</p>
"""

    p6 = f"""
<div class="section-band">10. Smoking</div>
<p>Under provincial law, smoking is not allowed in any indoor common areas of the building. The tenant agrees to these additional rules on smoking:</p>
<p>Select one:</p>
<p>{cb(smoking_is_none)} None<br/>
or<br/>
{cb(not smoking_is_none)} Smoking rules<br/>
Provide description of smoking rules (if necessary add additional pages):<br/>{fill('' if smoking_is_none else smoking_rules)}</p>
<p class="note-inline"><strong>Note:</strong> In making and enforcing smoking rules, the landlord must follow the Ontario Human Rights Code. See Parts M and S in General Information.</p>
<div class="section-band">11. Tenant's Insurance</div>
<p>Select one:</p>
<p>{cb(not insurance_required)} There are no tenant insurance requirements.<br/>
or<br/>
{cb(insurance_required)} The tenant must have liability insurance at all times. If the landlord asks for proof of coverage, the tenant must provide it. It is up to the tenant to get contents insurance if they want it.</p>
<div class="section-band">12. Changes to the Rental Unit</div>
<p>The tenant may install decorative items, such as pictures or window coverings. This is subject to any reasonable restrictions set out in the additional terms under Section 15.</p>
<p>The tenant cannot make other changes to the rental unit without the landlord's permission.</p>
<div class="section-band">13. Maintenance and Repairs</div>
<p>The landlord must keep the rental unit and property in good repair and comply with all health, safety and maintenance standards.</p>
<p>The tenant must repair or pay for any undue damage to the rental unit or property caused by the wilful or negligent conduct of the tenant, the tenant's guest or another person who lives in the rental unit.</p>
<p>The tenant is responsible for ordinary cleanliness of the rental unit, except for any cleaning the landlord agreed to do.</p>
<p class="note-inline"><strong>Note:</strong> See Part J in General Information.</p>
<div class="section-band">14. Assignment and Subletting</div>
<p>The tenant may assign or sublet the rental unit to another person only with the consent of the landlord. The landlord cannot arbitrarily or unreasonably withhold consent to a sublet or potential assignee.</p>
<p class="note-inline"><strong>Note:</strong> There are additional rules if the tenant wants to assign or sublet the rental unit. See Part P in General Information.</p>
"""

    p7 = f"""
<div class="section-band">15. Additional Terms</div>
<p>Landlords and tenants can agree to additional terms. Examples may include terms that:</p>
<ul class="compact">
<li>Require the landlord to make changes to the unit before the tenant moves in, and</li>
<li>Provide rules for use of common spaces and/or amenities.</li>
</ul>
<p>These additional terms should be written in plain language and clearly set out what the landlord or tenant must or must not do to comply with the term. If typed, the additional terms should be in a font size that is at least 10 points.</p>
<p>An additional term cannot take away a right or responsibility under the Residential Tenancies Act, 2006.</p>
<p>If a term conflicts with the Residential Tenancies Act, 2006 or any other terms set out in this form, the term is void (not valid or legally binding) and it cannot be enforced. Some examples of void and unenforceable terms include those that:</p>
<ul class="compact">
<li>Do not allow pets (however, the landlord can require the tenant to comply with condominium rules, which may prohibit certain pets),</li>
<li>Do not allow guests, roommates, any additional occupants,</li>
<li>Require the tenant to pay deposits, fees or penalties that are not permitted under the Residential Tenancies Act 2006 (e.g., damage or pet deposits, interest on rent arrears), and</li>
<li>Require the tenant to pay for all or part of the repairs that are the responsibility of the landlord.</li>
</ul>
<p>See General Information for more details.</p>
<p>The landlord and tenant may want to get legal advice before agreeing to any additional terms.</p>
<p>Select one:</p>
<p>{add_select_none} There are no additional terms.<br/>
or<br/>
{add_select_attach} This tenancy agreement includes an attachment with additional terms that the landlord and tenant agreed to.</p>
{add_terms_body}
<div class="section-band">16. Changes to this Agreement</div>
<p>After this agreement is signed, it can be changed only if the landlord and tenant agree to the changes in writing.</p>
<p class="note-inline"><strong>Note:</strong> The Residential Tenancies Act, 2006 allows some rent increases and requires some rent reductions without agreement between the landlord and tenant. See Part I in General Information.</p>
"""

    sig_landlord_rows = []
    for i in range(4):
        if i == 0:
            sig_landlord_rows.append(
                f"<tr class=\"sig-row\"><td>{fill(landlord_name)}</td><td></td><td></td></tr>"
            )
        else:
            sig_landlord_rows.append('<tr class="sig-row"><td></td><td></td><td></td></tr>')
    sig_landlord_html = "\n".join(sig_landlord_rows)

    sig_tenant_rows = []
    for i in range(8):
        name = tenant_full(i) if i < len(tenants) else ""
        sig_tenant_rows.append(
            f'<tr class="sig-row"><td>{fill(name)}</td><td></td><td></td></tr>'
        )
    sig_tenant_html = "\n".join(sig_tenant_rows)

    p8 = f"""
<div class="section-band">17. Signatures</div>
<p>By signing this agreement, the landlord(s) and the tenant(s) agree to follow its terms. The landlord(s) or tenant(s) can sign this lease electronically if they both agree.</p>
<p>Unless otherwise agreed in the additional terms under Section 15, if there is more than one tenant, each tenant is responsible for all tenant obligations under this agreement, including the full amount of rent.</p>
<p><strong>Landlord(s):</strong></p>
<table class="form sig-table">
<tr><th>Name</th><th>Signature</th><th>Date (yyyy/mm/dd)</th></tr>
{sig_landlord_html}
</table>
<p><strong>Tenant(s):</strong></p>
<table class="form sig-table">
<tr><th>Name</th><th>Signature</th><th>Date (yyyy/mm/dd)</th></tr>
{sig_tenant_html}
</table>
<p class="note-inline"><strong>Note:</strong> All of the landlords and tenants listed on the first page in Section 1 (Parties to the Agreement) must sign here. The landlord must give a copy of this agreement to the tenant within 21 days after the tenant signs it.</p>
"""

    pages = [
        page_wrap(1, p1),
        page_wrap(2, p2),
        page_wrap(3, p3),
        page_wrap(4, p4),
        page_wrap(5, p5),
        page_wrap(6, p6),
        page_wrap(7, p7),
        page_wrap(8, p8),
        page_wrap(9, appendix_p9),
        page_wrap(10, appendix_p10),
        page_wrap(11, appendix_p11),
        page_wrap(12, appendix_p12),
        page_wrap(13, appendix_p13),
        page_wrap(14, appendix_p14),
    ]

    body = "\n".join(pages)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Residential Tenancy Agreement (Standard Form of Lease) — 2229E (2020/12)</title>
{css}
</head>
<body>
{body}
</body>
</html>"""


if __name__ == "__main__":
    test_data = {
        "landlord_name": "John Smith",
        "landlord_unit": "101",
        "landlord_street_number": "100",
        "landlord_street_name": "King Street West",
        "landlord_po_box": "",
        "landlord_city": "Toronto",
        "landlord_province": "Ontario",
        "landlord_postal_code": "M5X 1A9",
        "landlord_phone": "416-555-0100",
        "landlord_email": "john@example.com",
        "email_notices_agreed": True,
        "emergency_contact_provided": True,
        "emergency_contact_info": "416-555-0100",
        "unit": "204",
        "street_number": "45",
        "street_name": "Bay Street",
        "city": "Toronto",
        "postal_code": "M5J 2X5",
        "parking_description": "1 underground spot, P-14",
        "is_condo": False,
        "start_date": "2025/05/01",
        "tenancy_type": "fixed",
        "end_date": "2026/04/30",
        "other_tenancy_description": "",
        "rent_payment_day": "first",
        "rent_frequency": "monthly",
        "rent_frequency_other": "",
        "base_rent": 2800.00,
        "parking_rent": 150.00,
        "extra_services": [
            {"label": "Water", "amount": 0}
        ],
        "total_rent": 2950.00,
        "rent_payable_to": "John Smith",
        "payment_method": "E-transfer",
        "has_partial_period": False,
        "partial_amount": 0,
        "partial_payment_date": "",
        "partial_from_date": "",
        "partial_to_date": "",
        "nsf_charge": 20.00,
        "gas_included": True,
        "ac_included": True,
        "storage_included": False,
        "laundry": "no_charge",
        "guest_parking": "pay_per_use",
        "other_services": [],
        "service_details": "",
        "electricity_responsibility": "landlord",
        "heat_responsibility": "landlord",
        "water_responsibility": "tenant",
        "utility_details": "Tenant sets up own water account",
        "has_rent_discount": False,
        "rent_discount_description": "",
        "rent_deposit": 2950.00,
        "key_deposit": 50.00,
        "key_deposit_description": "2 front door keys, 1 fob",
        "smoking_rules": "none",
        "insurance_required": True,
        "additional_terms": [
            "No smoking anywhere on the property"
        ],
        "tenants": [
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@example.com",
            },
            {
                "first_name": "Bob",
                "last_name": "Smith",
                "email": "bob@example.com",
            },
        ],
    }
    html = fill_lease(test_data)
    with open("test_lease_output.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Test lease written to test_lease_output.html")
