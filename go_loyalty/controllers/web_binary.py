from odoo import http
from odoo.http import request, Response
import base64


class ContractDownloadController(http.Controller):

    @http.route(
        "/web/binary/contract_download_pdf/<int:id>",
        type="http",
        auth="public",
        website=True,
        csrf=False,
    )
    def download_contract_pdf(self, id, **kw):
        try:
            partner = request.env["res.partner"].sudo().browse(id)
            if not partner.exists() or not partner.contract_copy:
                return request.not_found()

            response = Response()
            response.data = base64.b64decode(partner.contract_copy)
            response.mimetype = "application/pdf"
            return response
        except Exception:
            return request.not_found()

    @http.route(
        "/web/binary/matrix_contract_download_pdf/<int:id>",
        type="http",
        auth="public",
        website=True,
        csrf=False,
    )
    def download_matrix_contract_pdf(self, id, **kw):
        try:
            contract = request.env["contract.matrix"].sudo().browse(id)
            if not contract.exists() or not contract.contract_file:
                return request.not_found()

            response = Response()
            response.data = base64.b64decode(contract.contract_file)
            response.mimetype = "application/pdf"
            return response
        except Exception:
            return request.not_found()

    @http.route(
        "/web/binary/registration_download_pdf/<int:id>",
        type="http",
        auth="public",
        website=True,
        csrf=False,
    )
    def download_registration_pdf(self, id, **kw):
        try:
            partner = request.env["res.partner"].sudo().browse(id)
            if not partner.exists() or not partner.company_registartion:
                return request.not_found()

            response = Response()
            response.data = base64.b64decode(partner.company_registartion)
            response.mimetype = "application/pdf"
            return response
        except Exception:
            return request.not_found()

    @http.route(
        "/web/binary/offer_download_pdf/<int:id>",
        type="http",
        auth="public",
        website=True,
        csrf=False,
    )
    def download_offer_pdf(self, id, **kw):
        try:
            product = request.env["product.template"].sudo().browse(id)
            if not product.exists() or not product.offer_copy:
                return request.not_found()

            pdf_data = base64.b64decode(product.offer_copy)
            response = Response()
            response.data = pdf_data
            response.mimetype = "application/pdf"
            return response
        except Exception:
            return request.not_found()

