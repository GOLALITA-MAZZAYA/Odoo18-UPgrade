import base64
import mimetypes
import os

from odoo.http import request, Response
from odoo import http


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

    @http.route(
        "/contract_matrix/attachment/<int:contract_matrix_id>",
        type="http",
        auth="public",
        website=True,
        csrf=False,
    )
    def download_attachment(self, contract_matrix_id, **kwargs):
        try:
            # Fetch the contract matrix record
            contract_matrix = (
                request.env["contract.matrix"].sudo().browse(contract_matrix_id)
            )

            if not contract_matrix.exists() or not contract_matrix.contract_file:
                return Response("File not found", status=404)

            # Decode the file if it is base64 encoded
            file_content = base64.b64decode(contract_matrix.contract_file)
            file_name = contract_matrix.contract_filename or "contract_file"

            # Get file extension from filename or fallback
            file_extension = os.path.splitext(file_name)[1].lower()
            if not file_extension:
                mime_type, _ = mimetypes.guess_type(file_name)
                if mime_type:
                    file_extension = mimetypes.guess_extension(mime_type) or ".bin"
                    file_name += file_extension
                else:
                    file_name += ".bin"

            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_name)
            if not mime_type:
                mime_type = "application/octet-stream"

            # Return response
            return request.make_response(
                file_content,
                headers=[
                    ("Content-Type", mime_type),
                    ("Content-Disposition", f'attachment; filename="{file_name}"'),
                ],
            )
        except Exception as e:
            return Response(f"Error: {str(e)}", status=500)
