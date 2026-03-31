from io import BytesIO
from datetime import datetime
import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject


PDF_PATH = os.path.join(
    os.path.dirname(__file__), "300.pdf"
)


def fill_buyer_representation_pdf(data: dict) -> bytes:
    """Fill OREA Form 300 Buyer Representation Agreement PDF and return bytes."""

    def g(key, default=""):
        value = data.get(key, default)
        if value is None:
            return default
        return value

    def s(value) -> str:
        if value is None:
            return ""
        return str(value)

    def split_date(value: str) -> tuple[str, str, str]:
        v = s(value).strip()
        if not v:
            return "", "", ""
        try:
            dt = datetime.strptime(v, "%Y/%m/%d")
            return dt.strftime("%d"), dt.strftime("%B"), dt.strftime("%y")
        except ValueError:
            return "", "", ""

    start_d, start_m, start_y = split_date(g("start_date"))
    expiry_d, expiry_m, expiry_y = split_date(g("expiry_date"))
    ack_d, ack_m, ack_y = split_date(g("acknowledgement_date"))

    fields = {
        "txts_broker": s(g("brokerage_name")),
        "txts_brkaddr": s(g("brokerage_address")),
        "txts_brkcity": s(g("brokerage_city")),
        "txts_brkstate": s(g("brokerage_province", "ON")),
        "txts_brkzipcode": s(g("brokerage_postal_code")),
        "txts_brkphone": s(g("brokerage_phone")),
        "txts_brkfax": s(g("brokerage_fax")),
        "txtbuyer1": s(g("buyer_1_name")),
        "txtbuyer2": s(g("buyer_2_name")),
        "txtbuyersig1": s(g("buyer_1_name")),
        "txtbuyersig2": s(g("buyer_2_name")),
        "txtb_streetnum": s(g("buyer_street_number")),
        "txtb_street": s(g("buyer_street_name")),
        "txtb_city": s(g("buyer_city")),
        "txtb_zipcode": s(g("buyer_postal_code")),
        "txtCommencingTime": s(g("commencement_time")),
        "txtCommencingDate_d": start_d,
        "txtCommencingDate_m": start_m,
        "txtCommencingDate_yy": start_y,
        "txtExpiringDate_d": expiry_d,
        "txtExpiringDate_m": expiry_m,
        "txtExpiringDate_yy": expiry_y,
        "txtp_type": s(g("property_type")),
        "txtp_type2": s(g("property_type_2")),
        "txtp_location": s(g("geographic_location")),
        "txtp_location2": s(g("geographic_location_2")),
        "txtAttachedSchedule": s(g("schedules", "A")),
        "txtp_commision": s(g("commission_percent")),
        "txtp_commision_writ": s(g("commission_words")),
        "txtcommissionProp": s(g("lease_commission")),
        "txtholdover": s(g("holdover_days")),
        "txts_brkagent": s(g("agent_name")),
        "txts_brkagentsig": s(g("agent_name")),
        "txtb_phone1": s(g("buyer_1_phone")),
        "txtb2_phone1": s(g("buyer_2_phone")),
        "txtcopy_d": ack_d,
        "txtcopy_m": ack_m,
        "txtcopy_y": ack_y,
        "txtAddSchedule": s(g("schedule_a_content")),
    }

    reader = PdfReader(PDF_PATH)
    writer = PdfWriter(clone_from=reader)

    for page in writer.pages:
        writer.update_page_form_field_values(page, fields)

    if reader.trailer.get("/Root") and reader.trailer["/Root"].get("/AcroForm"):
        writer._root_object["/AcroForm"].update(
            {
                NameObject("/NeedAppearances"): BooleanObject(True)
            }
        )

    out = BytesIO()
    writer.write(out)
    out.seek(0)
    return out.read()
