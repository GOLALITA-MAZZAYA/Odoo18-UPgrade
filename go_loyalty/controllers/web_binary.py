import base64
import logging
import mimetypes
import os

import werkzeug
from odoo.exceptions import AccessError, UserError
from odoo.http import Response, request
from odoo.tools import str2bool
from odoo.tools.image import image_guess_size_from_field_name
from odoo.tools.safe_eval import safe_eval

from odoo import SUPERUSER_ID, _, http

_logger = logging.getLogger(__name__)


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

    @http.route(
        ["/go/api/image/<int:rec_id>/<string:field>/<string:model>"],
        type="http",
        auth="public",
        csrf=False,
    )
    def content_image_partner(
        self, rec_id, field="image_512", model="res.partner", **kwargs
    ):
        try:
            allowed_fields = {
                "image_128",
                "image_256",
                "image_512",
                "image_1024",
                "image_icon",
                "image",
                "image1",
                "image2",
                "image3",
                "image4",
                "image_1920",
                "map_banner",
                "banner_image",
                "offer_image",
            }

            allowed_models = {
                "res.partner",
                "partner.category",
                "merchant.banner",
                "product.template",
                "advertisement.banner",
                "loyalty.notification.list",
                "loyalty.whatsapp.message",
            }

            if field not in allowed_fields:
                _logger.warning("Invalid image field requested: %s", field)
                raise werkzeug.exceptions.NotFound(_("Invalid image field."))

            if model not in allowed_models:
                _logger.warning("Invalid model requested: %s", model)
                raise werkzeug.exceptions.NotFound(_("Invalid model name."))

            IrBinary = request.env["ir.binary"].sudo()
            record = IrBinary._find_record(
                xmlid=None,
                res_model=model,
                res_id=rec_id,
                access_token=None,
                field=field,
            )

            stream = IrBinary._get_image_stream_from(
                record,
                field,
                filename=None,
                filename_field="name",
                mimetype=None,
                width=0,
                height=0,
                crop=False,
            )

            send_file_kwargs = {
                "as_attachment": False,
                "immutable": True,
                "max_age": http.STATIC_CACHE_LONG,
            }
            return stream.get_response(**send_file_kwargs)

        except UserError as exc:
            _logger.error(
                "UserError while serving image for %s[%s.%s]: %s",
                rec_id,
                model,
                field,
                exc,
            )

            # Use fallback placeholder
            width, height = image_guess_size_from_field_name(field)
            placeholder = request.env.ref("web.image_placeholder").sudo()
            stream = (
                request.env["ir.binary"]
                .sudo()
                ._get_image_stream_from(
                    placeholder, "raw", width=width, height=height, crop=False
                )
            )
            return stream.get_response()

        except werkzeug.exceptions.NotFound:
            raise

        except Exception as e:
            _logger.exception(
                "Unexpected error serving image %s[%s.%s]: %s", rec_id, model, field, e
            )

            # Fallback generic placeholder
            placeholder = request.env.ref("web.image_placeholder").sudo()
            stream = (
                request.env["ir.binary"]
                .sudo()
                ._get_image_stream_from(
                    placeholder, "raw", width=0, height=0, crop=False
                )
            )
            return stream.get_response()
