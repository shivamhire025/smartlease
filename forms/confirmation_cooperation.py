from io import BytesIO
import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject


PDF_PATH = os.path.join(
    os.path.dirname(__file__), "320.pdf"
)


def fill_confirmation_cooperation_pdf(data: dict) -> bytes:
    """Fill OREA Form 320 Confirmation of Co-operation and Representation PDF."""

    def g(key, default=""):
        value = data.get(key, default)
        if value is None:
            return default
        return value

    def s(value) -> str:
        if value is None:
            return ""
        return str(value)

    def checkbox(value: bool) -> str:
        return "/1" if value else "/Off"

    seller_representation = s(g("seller_representation")).strip().lower()
    coop_representation = s(g("coop_representation")).strip().lower()
    coop_commission_type = s(g("coop_commission_type")).strip().lower()

    fields = {
        "txtbuyer1": s(g("buyer_1_name")),
        "txtbuyer2": s(g("buyer_2_name")),
        "txtseller1": s(g("seller_1_name")),
        "txtseller2": s(g("seller_2_name")),
        "txtp_streetnum": s(g("street_number")),
        "txtp_street": s(g("street_name")),
        "txtp_UnitNumber": s(g("unit")),
        "txtp_city": s(g("city")),
        "txtp_state": s(g("province", "ON")),
        "txtp_zipcode": s(g("postal_code")),
        "chkOpt_ListBrok1": checkbox(seller_representation == "single"),
        "chkOpt_provide": checkbox(seller_representation == "self_represented"),
        "chkOpt_ListBrok2": checkbox(seller_representation == "designated"),
        "chkOpt_ListBrok2a": checkbox(seller_representation == "multiple_seller"),
        "chkOpt_ListBrok3": checkbox(seller_representation == "multiple_buyer"),
        "chkOpt_CoOp": checkbox(coop_representation == "buyer_direct"),
        "chkOpt_CoOp2": checkbox(coop_representation == "buyer_commission"),
        "chkOpt_CBrokComm": checkbox(coop_commission_type == "mls"),
        "chkOpt_CBrokComm2": checkbox(coop_commission_type == "other"),
        "txtp_bal2ndMortgage": s(g("coop_commission_mls_amount")),
        "txtcoopCommisionC1": s(g("coop_commission_other")),
        "txtaddn_coop": s(g("coop_additional_comments")),
        "txtaddn_list": s(g("seller_additional_comments")),
        "txtaddn_list1": s(g("seller_additional_comments_2")),
        "txts_broker": s(g("seller_brokerage_name")),
        "txts_brkaddr": s(g("seller_brokerage_address")),
        "txts_brkphone": s(g("seller_brokerage_phone")),
        "txts_brkfax": s(g("seller_brokerage_fax")),
        "txtSellSign": s(g("seller_brokerage_name")),
        "txts_brkagent": s(g("seller_agent_name")),
        "txtl_broker": s(g("coop_brokerage_name")),
        "txtl_brkaddr": s(g("coop_brokerage_address")),
        "txtl_brkphone": s(g("coop_brokerage_phone")),
        "txtl_brkfax": s(g("coop_brokerage_fax")),
        "txtBuySign": s(g("coop_brokerage_name")),
        "txtl_brkagent": s(g("coop_agent_name")),
        "txtbuyersig1": s(g("buyer_1_name")),
        "txtbuyersig2": s(g("buyer_2_name")),
        "txtsellersig1": s(g("seller_1_name")),
        "txtsellersig2": s(g("seller_2_name")),
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
