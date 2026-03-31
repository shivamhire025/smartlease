from io import BytesIO
from datetime import datetime
import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject


PDF_PATH = os.path.join(
    os.path.dirname(__file__), "122.pdf"
)


def fill_mutual_release_pdf(data: dict) -> bytes:
    """Fill OREA Form 122 Mutual Release PDF and return bytes."""

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

    agreement_d, agreement_m, agreement_y = split_date(g("agreement_date"))
    irrev_d, irrev_m, irrev_y = split_date(g("irrevocability_date"))
    confirm_d, confirm_m, confirm_y = split_date(g("confirmation_date"))

    fields = {
        "txtbuyer1": s(g("buyer_1_name")),
        "txtbuyer2": s(g("buyer_2_name")),
        "txtseller1": s(g("seller_1_name")),
        "txtseller2": s(g("seller_2_name")),
        "txtl_broker": s(g("listing_brokerage")),
        "txts_broker": s(g("coop_brokerage")),
        "txtp_OfferDate_d": agreement_d,
        "txtp_OfferDate_mmmm": agreement_m,
        "txtp_OfferDate_yy": agreement_y,
        "txtp_streetnum": s(g("street_number")),
        "txtp_street": s(g("street_name")),
        "txtp_UnitNumber": s(g("unit")),
        "txtp_city": s(g("city")),
        "txtp_state": s(g("province", "Ontario")),
        "txtp_zipcode": s(g("postal_code")),
        "txtp_DepositWords": s(g("deposit_words")),
        "txtp_Deposit": s(g("deposit_amount")),
        "txtPayable": s(g("payable_to")),
        "txtPayable2": s(g("payable_to_line2")),
        "hidirrev_v_p": s(g("irrevocability_party")),
        "txtirrevocatime": s(g("irrevocability_time")),
        "txtIrrevocableDate_d": irrev_d,
        "txtIrrevocableDate_m": irrev_m,
        "txtIrrevocableDate_y": irrev_y,
        "txtSignature1": s(g("buyer_1_name")),
        "txtSignature2": s(g("buyer_2_name")),
        "txtSignature3": s(g("seller_1_name")),
        "txtSignature4": s(g("seller_2_name")),
        "txtconfirmDate_d": confirm_d,
        "txtconfirmDate_m": confirm_m,
        "txtconfirmDate_yy": confirm_y,
        "txtconfirmTime": s(g("confirmation_time")),
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
