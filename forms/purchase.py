from io import BytesIO
from datetime import datetime
import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject


PDF_PATH = os.path.join(
    os.path.dirname(__file__), "100.pdf"
)


def fill_purchase_pdf(data: dict) -> bytes:
    """Fill OREA Form 100 PDF and return bytes."""

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

    offer_d, offer_m, offer_y = split_date(g("offer_date"))
    irrev_d, irrev_m, irrev_y = split_date(g("irrevocability_date"))
    close_d, close_m, close_y = split_date(g("completion_date"))
    req_d, req_m, req_y = split_date(g("requisition_date"))

    fields = {
        "txtp_streetnum": s(g("street_number")),
        "txtp_street": s(g("street_name")),
        "txtp_unitNumber": s(g("unit")),
        "txtp_city": s(g("city")),
        "txtp_state": s(g("province", "Ontario")),
        "txtp_zipcode": s(g("postal_code")),
        "txtp_Subdivision": s(g("frontage")),
        "txtsideOf": s(g("side_of_street")),
        "txtInThe": s(g("municipality")),
        "txtp_ZoningClass": s(g("depth")),
        "txtp_legaldesc": s(g("legal_description")),
        "txtbuyer1": s(g("buyer_1_name")),
        "txtbuyer2": s(g("buyer_2_name")),
        "txtseller1": s(g("seller_1_name")),
        "txtseller2": s(g("seller_2_name")),
        "txtp_price": s(g("purchase_price")),
        "txtp_pricewords": s(g("purchase_price_words")),
        "txtp_depositwords": s(g("deposit_words")),
        "txtp_deposit": s(g("deposit_amount")),
        "txtDepositHolder": s(g("deposit_holder")),
        "txtp_OfferDate_d": offer_d,
        "txtp_OfferDate_mmmm": offer_m,
        "txtp_OfferDate_yy": offer_y,
        "txtp_OfferExpireDate_d": irrev_d,
        "txtp_OfferExpireDate_mmmm": irrev_m,
        "txtp_OfferExpireDate_yy": irrev_y,
        "txtp_irrev_t": s(g("irrevocability_time")),
        "txtp_closedate_d": close_d,
        "txtp_closedate_mmmm": close_m,
        "txtp_closedate_yy": close_y,
        "txtp_fundingDate_d": req_d,
        "txtp_fundingDate_mmmm": req_m,
        "txtp_fundingDate_yy": req_y,
        "txtp_propincludes": s(g("chattels_included")),
        "txtp_propexcludes": s(g("fixtures_excluded")),
        "txtp_LeasedItems": s(g("rental_items")),
        "txtAttachedSchedule": s(g("schedules", "A")),
        "txtAddSchedule": s(g("schedule_a_content")),
        "txtp_otherliensdesc": s(g("present_use")),
        "hidinc_add": s(g("hst_treatment")),
        "txtbuyersig1": s(g("buyer_1_name")),
        "txtbuyersig2": s(g("buyer_2_name")),
        "txtsellersig1": s(g("seller_1_name")),
        "txtsellersig2": s(g("seller_2_name")),
        "txtBStreet": s(g("buyer_address")),
        "txtBPhone": s(g("buyer_phone")),
        "txtSStreet": s(g("seller_address")),
        "txtSPhone": s(g("seller_phone")),
        "txtl_broker": s(g("listing_brokerage")),
        "txtl_brkphone": s(g("listing_brokerage_phone")),
        "txtl_brkagent": s(g("listing_agent")),
        "txts_broker": s(g("coop_brokerage")),
        "txts_brkphone": s(g("coop_brokerage_phone")),
        "txts_brkagent": s(g("coop_agent")),
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
