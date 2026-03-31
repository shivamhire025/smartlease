from io import BytesIO
from datetime import datetime
import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject


PDF_PATH = os.path.join(
    os.path.dirname(__file__), "200.pdf"
)


def fill_listing_agreement_pdf(data: dict) -> bytes:
    """Fill OREA Form 200 Listing Agreement PDF and return bytes."""

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

    list_start_d, list_start_m, list_start_y = split_date(g("listing_start_date"))
    list_end_d, list_end_m, list_end_y = split_date(g("listing_end_date"))
    ack_d, ack_m, ack_y = split_date(g("acknowledgement_date"))

    fields = {
        "txtl_broker": s(g("listing_brokerage")),
        "txtl_brkphone": s(g("listing_brokerage_phone")),
        "txtl_brkaddr": s(g("listing_brokerage_address")),
        "txtl_brkcity": s(g("listing_brokerage_city")),
        "txtl_brkstate": s(g("listing_brokerage_province")),
        "txtl_brkzipcode": s(g("listing_brokerage_postal_code")),
        "txtseller1": s(g("seller_1_name")),
        "txtseller2": s(g("seller_2_name")),
        "txtsellersig1": s(g("seller_1_name")),
        "txtsellersig2": s(g("seller_2_name")),
        "txtp_streetnum": s(g("street_number")),
        "txtp_street": s(g("street_name")),
        "txtp_UnitNumber": s(g("unit")),
        "txtp_city": s(g("city")),
        "txtp_state": s(g("province", "ON")),
        "txtp_zipcode": s(g("postal_code")),
        "txtComAt": s(g("commencement_time")),
        "txtp_listdate_d": list_start_d,
        "txtp_listdate_mmmm": list_start_m,
        "txtp_listdate_yy": list_start_y,
        "txtp_expiredate_d": list_end_d,
        "txtp_expiredate_mmmm": list_end_m,
        "txtp_expiredate_yy": list_end_y,
        "txtp_listprice": s(g("listing_price")),
        "txtp_listpricewords": s(g("listing_price_words")),
        "txtAttachedSchedule": s(g("schedules", "A")),
        "txtListBrkComm": s(g("listing_commission")),
        "txtcommis_writ": s(g("listing_commission_words")),
        "txtCBrokComm": s(g("coop_commission")),
        "txtp_bal1stdeed123": s(g("holdover_days")),
        "txtl_brkagentsig": s(g("listing_agent_name")),
        "txtl_brkname": s(g("listing_agent_name")),
        "txts_phone1": s(g("seller_1_phone")),
        "txts2_phone1": s(g("seller_2_phone")),
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
