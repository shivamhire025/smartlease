from io import BytesIO
from datetime import datetime
import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject


PDF_PATH = os.path.join(
    os.path.dirname(__file__), "123.pdf"
)


def fill_waiver_pdf(data: dict) -> bytes:
    """Fill OREA Form 123 Waiver PDF and return bytes."""

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
    dated_d, dated_m, dated_y = split_date(g("dated_date"))
    receipt_d, receipt_m, receipt_y = split_date(g("receipt_date"))

    fields = {
        "txtbuyer1": s(g("buyer_1_name")),
        "txtbuyer2": s(g("buyer_2_name")),
        "txtseller1": s(g("seller_1_name")),
        "txtseller2": s(g("seller_2_name")),
        "txtp_streetnum": s(g("street_number")),
        "txtp_street": s(g("street_name")),
        "txtp_UnitNumber": s(g("unit")),
        "txtp_city": s(g("city")),
        "txtp_state": s(g("province", "Ontario")),
        "txtp_zipcode": s(g("postal_code")),
        "txtp_OfferDate_d": agreement_d,
        "txtp_OfferDate_mmmm": agreement_m,
        "txtp_OfferDate_yy": agreement_y,
        "txtAddSchedule": s(g("conditions_waived")),
        "txtdated_at_1": s(g("dated_at_city")),
        "txtdated1_t": s(g("dated_time")),
        "txtdated1_d": dated_d,
        "txtdated1_m": dated_m,
        "txtdated1_y": dated_y,
        "txtwsig1": s(g("witness_1_name")),
        "txtwsig2": s(g("witness_2_name")),
        "txtvpsig1": s(g("signer_1_name")),
        "txtvpsig2": s(g("signer_2_name")),
        "txtdated2_t": s(g("receipt_time")),
        "txtdated2_d": receipt_d,
        "txtdated2_m": receipt_m,
        "txtdated2_y": receipt_y,
        "txtName": s(g("receipt_acknowledged_by")),
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
