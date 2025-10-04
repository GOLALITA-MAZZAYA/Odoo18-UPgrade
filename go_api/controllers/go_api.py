# -*- coding: utf-8 -*-
import json
from odoo import http, _
from odoo.http import request, Response
from werkzeug.urls import url_join
from odoo.tools.safe_eval import safe_eval
import json
import ast
import logging


_logger = logging.getLogger(__name__)


class GoAPIController(http.Controller):

    @staticmethod
    def _validate_token(data):
        token = data.get("token")
        if not token:
            return {"error": _("Token is missing")}
        user = request.env["res.users"].sudo().search([("token", "=", token)], limit=1)
        if not user:
            return {"error": _("Invalid User Token")}
        return user

    @staticmethod
    def _get_json_request():
        try:
            if not request.httprequest.data:
                return {"error": _("No JSON payload provided")}
            data = json.loads(request.httprequest.data.decode("utf-8"))
            if not isinstance(data, dict):
                return {"error": _("Invalid JSON format")}
            return data
        except json.JSONDecodeError:
            return {"error": _("Malformed JSON payload")}

    @staticmethod
    def _authenticate_user(login, password, expected_org=None):
        credential = {"login": login, "password": password, "type": "password"}
        auth_info = request.session.authenticate(request.session.db, credential)
        uid = auth_info.get("uid")
        if not uid:
            return {"error": _("Wrong login/password")}
        user = request.env["res.users"].sudo().browse(uid)

        if expected_org and user.partner_id.org_type != expected_org:
            return {"error": _(f"Not Belongs to {expected_org.upper()} APP")}
        return user

    @staticmethod
    def _prepare_user_response(user, data):
        web_base_url = (
            request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )
        token = user.get_user_access_token()

        user.token = token
        user.device_id = data.get("device_id")
        user.device_token = data.get("device_token")
        user.device_type = data.get("device_type")

        main_member = not bool(user.partner_id.family_head_member_id)

        return {
            "token": token,
            "id": user.id,
            "main_member": main_member,
            "tracking_partner_id": user.partner_id.id,
            "name": user.partner_id.name,
            "email": user.partner_id.email,
            "member_type": user.employee_type,
            "login_id": user.login,
            "family_head_id": user.partner_id.id,
            "phone": user.partner_id.phone,
            "employer": user.partner_id.parent_id.name,
            "barcode": user.partner_id.barcode,
            "paused_notification": user.pause_notification,
            "employer_icon": url_join(
                web_base_url,
                f"/go/api/image/{user.partner_id.parent_id.id}/image_512/res.partner",
            ),
            "icon": url_join(
                web_base_url,
                f"/go/api/image/{user.partner_id.id}/image_512/res.partner",
            ),
        }

    def _handle_token_request(self, expected_org, **post):
        res = {}
        try:
            data = request.params or self._get_json_request()
            if "error" in data:
                return data

            login = data.get("login")
            password = data.get("password")
            if not login or not password:
                return {"error": _("No login or password found in parameters")}

            user = self._authenticate_user(login, password, expected_org)
            if isinstance(user, dict):
                return user

            res = self._prepare_user_response(user, data)
            request.session.logout()
        except Exception as e:
            res["error"] = _("Something Went Wrong! %s") % e
        return res

    @http.route(
        ["/go/api/user/get_token"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token(self, **post):
        return self._handle_token_request("golalita", **post)

    @http.route(
        ["/go/api/user/get_token/sjc"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_sjc(self, **post):
        return self._handle_token_request("sjc", **post)

    @http.route(
        ["/go/api/gulfexc/get_token"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_gulfexchange(self, **post):
        return self._handle_token_request("gulfexchange", **post)

    @http.route(
        ["/go/api/user/get_token/gulf/exchange"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_ge(self, **post):
        return self._handle_token_request("gulfexchange", **post)

    @http.route(
        ["/go/api/user/get_token/beema"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_beema(self, **post):
        return self._handle_token_request("beema", **post)

    @http.route(
        ["/go/api/user/get_token/daam"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_daam(self, **post):
        return self._handle_token_request("daam", **post)

    @http.route(
        ["/go/api/user/get_token/qatar/insurance"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_qib(self, **post):
        return self._handle_token_request("qatarinsurance", **post)

    @http.route(
        ["/go/api/user/get_token/qlm"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_qlm(self, **post):
        return self._handle_token_request("qlm", **post)

    @http.route(
        ["/go/api/user/get_token/masrif"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_masrif(self, **post):
        return self._handle_token_request("masrif", **post)

    @http.route(
        ["/go/api/user/get_token/barwa"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_barwa(self, **post):
        return self._handle_token_request("barwa", **post)

    @http.route(
        ["/go/api/user/get_token/alzamanexchange"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_alzamanexchange(self, **post):
        return self._handle_token_request("alzamanexchange", **post)

    @http.route(
        ["/go/api/user/get_token/qatar/post/stop"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_qatar_post(self, **post):
        return self._handle_token_request("qatar_post", **post)

    @http.route(
        ["/go/api/user/get_token/hayyakam/stopaa"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_get_token_hayyakam(self, **post):
        return self._handle_token_request("hayyakam", **post)

    @http.route(
        ["/go/api/user/get_token/new"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="http",
        cors="*",
    )
    def go_get_token_new(self, **post):
        try:
            data = request.params or self._get_json_request()
            if "error" in data:
                return Response(
                    json.dumps(data), mimetype="application/json", status=400
                )

            login = data.get("login")
            password = data.get("password")
            if not login or not password:
                return Response(
                    json.dumps(
                        {"error": _("No login or password found in parameters")}
                    ),
                    mimetype="application/json",
                    status=400,
                )

            user = self._authenticate_user(login, password)
            if not user:
                return Response(
                    json.dumps({"error": _("Invalid login or password")}),
                    mimetype="application/json",
                    status=401,
                )

            res = self._prepare_user_response(user, data)
            res.pop("main_member", None)

            request.session.logout()
            return Response(json.dumps(res), mimetype="application/json", status=200)

        except Exception as e:
            res = {"error": _("Something went wrong: %s") % e}
            return Response(json.dumps(res), mimetype="application/json", status=500)

    @http.route(
        ["/go/api/user/delete_token"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_delete_token(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            token = data.get("token")
            if not token:
                return {"error": _("No token provided")}

            current_user = (
                request.env["res.users"].sudo().search([("token", "=", token)], limit=1)
            )
            if not current_user:
                return {"error": _("Invalid User Token")}

            current_user.sudo().token = False
            return {"success": _("Token '%s' Deleted Successfully" % token)}

        except Exception as e:
            return {"error": _("Something went wrong: %s" % e)}

    @http.route(
        ["/go/api/user/refresh_token"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_refresh_token(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            token = data.get("token")
            if not token:
                return {"error": _("No token provided")}

            current_user = (
                request.env["res.users"].sudo().search([("token", "=", token)], limit=1)
            )
            if not current_user:
                return {"error": _("Invalid User Token")}

            try:
                current_user.sudo().token = False
                new_token = current_user.get_user_access_token()
                current_user.sudo().token = new_token

                res = {
                    "token": new_token,
                    "name": current_user.partner_id.name,
                    "email": current_user.partner_id.email,
                    "login_id": current_user.login,
                    "phone": current_user.partner_id.phone,
                }
                return res

            except Exception as e:
                return {"error": _("Something went wrong: %s" % e)}

        except Exception as e:
            return {"error": _("Something went wrong: %s" % e)}

    def _adjust_many2many_domain(self, domain):
        new_domain = []
        for condition in domain:
            if isinstance(condition, list) and len(condition) == 3:
                field, operator, value = condition
                if isinstance(value, list) and operator == "=":
                    operator = "in"
                new_domain.append([field, operator, value])
            else:
                new_domain.append(condition)
        return new_domain

    def _get_model(self, model_name, user):
        if not model_name or not user:
            return {"error": _("Invalid model or user")}
        try:
            Model = request.env[model_name].with_user(user.id)
            if model_name == "res.partner":
                Model = Model.sudo()
            return Model
        except Exception as e:
            return {"error": _("Model Not Found: %s" % e)}

    def _prepare_search_params(self, model_name, data, id=None):
        try:
            Model = request.env[model_name]
        except Exception as e:
            _logger.warning("Failed to access model '%s': %s", model_name, e)
            return [], ["id"], 0, None

        if id:
            try:
                all_fields = list(Model.fields_get().keys())
                fields = all_fields if all_fields else ["id"]
            except Exception as e:
                _logger.warning(
                    "Failed to get fields for model '%s': %s", model_name, e
                )
                fields = ["id"]
            return [("id", "=", id)], fields, 0, None

        domain = []
        if "domain" in data:
            try:
                domain = ast.literal_eval(data.get("domain", "[]"))
                if not isinstance(domain, list):
                    domain = []
            except Exception as e:
                _logger.warning("Failed to parse 'domain' from request: %s", e)
                domain = []

        try:
            all_fields = list(Model.fields_get().keys())
        except Exception as e:
            _logger.warning("Failed to get fields for model '%s': %s", model_name, e)
            all_fields = []

        default_field = "name" if "name" in all_fields else "id"
        fields = [default_field]

        if "fields" in data:
            try:
                user_fields = ast.literal_eval(data.get("fields"))
                if isinstance(user_fields, list):
                    valid_fields = [f for f in user_fields if f in all_fields]
                    if valid_fields:
                        fields = valid_fields
            except Exception as e:
                _logger.warning("Failed to parse 'fields' from request: %s", e)

        try:
            offset = int(data.get("offset", 0))
        except (ValueError, TypeError) as e:
            _logger.warning("Invalid offset value '%s': %s", data.get("offset"), e)
            offset = 0

        try:
            limit = int(data.get("limit")) if data.get("limit") else None
        except (ValueError, TypeError) as e:
            _logger.warning("Invalid limit value '%s': %s", data.get("limit"), e)
            limit = None

        return domain, fields, offset, limit

    def _search_records(self, Model, domain, fields, offset, limit):
        try:
            order_field = "sequence" if "sequence" in Model.fields_get() else "id"
            return Model.search_read(
                domain,
                fields=fields,
                offset=offset,
                order=f"{order_field} asc",
                limit=limit,
            )
        except Exception as e:
            _logger.warning("Search failed: %s", e)
            return []

    def safe_parse_images(self, records):
        if not isinstance(records, list):
            return records
        try:
            for record in records:
                if isinstance(record, dict):
                    for field, value in record.items():
                        if isinstance(value, bytes):
                            record[field] = value.decode("utf-8")
        except Exception as e:
            _logger.warning("Failed to decode image: %s", e)
        return records

    @http.route(
        ["/go/api/<string:model>/search", "/go/api/<string:model>/search/<int:id>"],
        auth="public",
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_search_data(self, model=None, id=None, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            Model = self._get_model(model, current_user)
            if isinstance(Model, dict):
                return Model

            domain, fields, offset, limit = self._prepare_search_params(model, data, id)
            domain = self._adjust_many2many_domain(domain)

            result = self._search_records(Model, domain, fields, offset, limit)
            result = self.safe_parse_images(result)

            return result

        except Exception as e:
            _logger.exception("API go_search_data failed")
            return {"error": _("Something went wrong")}

    @http.route(
        ["/go/api/<string:model>/update", "/go/api/<string:model>/update/<int:rec_id>"],
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def go_update_data(self, model=None, rec_id=None, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            Model = self._get_model(model, current_user)
            if isinstance(Model, dict):
                return Model

            update_vals = data.get("update_vals")
            return self._update_record(Model, rec_id, update_vals)

        except Exception as e:
            _logger.exception("Error in go_update_data: %s", e)
            return {"error": _("Unexpected Error: %s") % str(e)}

    def _update_record(self, Model, rec_id, update_vals):
        if not rec_id:
            return {"error": _("Record ID is required")}

        record = Model.browse(rec_id)
        if not record.exists():
            return {"error": _("Record with ID %s not found") % rec_id}

        if not update_vals or not isinstance(update_vals, dict):
            return {"error": _("update_vals must be provided as a dictionary")}

        if record._name == "res.users" and update_vals.get("email"):
            update_vals["login"] = update_vals["email"]

        try:
            record.write(update_vals)
            return {"success": _("Record Updated Successfully")}
        except Exception as e:
            _logger.exception(
                "Error while updating %s (ID %s): %s", record._name, rec_id, e
            )
            return {"error": _("Failed to update record: %s") % str(e)}

    @http.route(
        [
            "/go/api/<string:model>/unlink/",
            "/go/api/<string:model>/unlink/<int:rec_id>",
        ],
        type="json",
        auth="public",
        csrf=False,
        cors="*",
        methods=["POST"],
    )
    def go_unlink_data(self, model=None, rec_id=None, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            Model = self._get_model(model, current_user)
            if isinstance(Model, dict):
                return Model

            return self._unlink_records(Model, rec_id, data.get("unlink_ids"))

        except Exception as e:
            _logger.exception("Error in go_unlink_data: %s", e)
            return {"error": _("Unexpected Error: %s") % str(e)}

    def _unlink_records(self, Model, rec_id=None, unlink_ids=None):
        ids_to_delete = []
        if rec_id:
            ids_to_delete = [rec_id]
        elif unlink_ids:
            try:
                if isinstance(unlink_ids, str):
                    unlink_ids = ast.literal_eval(unlink_ids)
                if not isinstance(unlink_ids, list):
                    return {"error": _("unlink_ids must be a list")}
                ids_to_delete = unlink_ids
            except Exception as e:
                _logger.exception("Failed to parse unlink_ids: %s", e)
                return {"error": _("Invalid unlink_ids format: %s") % str(e)}
        else:
            return {"error": _("No record IDs provided for deletion")}

        records = Model.browse(ids_to_delete)
        if not records.exists():
            return {"error": _("No valid records found to delete")}

        try:
            records.unlink()
            if len(ids_to_delete) == 1:
                return {
                    "success": _("Record Successfully Deleted: %s" % ids_to_delete[0])
                }
            return {"success": _("Records Successfully Deleted: %s" % ids_to_delete)}
        except Exception as e:
            _logger.exception("Failed to delete records %s: %s", ids_to_delete, e)
            return {"error": _("Failed to delete records: %s") % str(e)}

    @http.route(
        ["/go/api/<string:model>/create"],
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def go_create_data(self, model=None, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            Model = self._get_model(model, current_user)
            if isinstance(Model, dict):
                return Model

            create_vals = data.get("create_vals")
            if not create_vals:
                return {"error": _("create_vals not found in request")}

            return self._create_records(Model, create_vals)

        except Exception as e:
            _logger.exception("Error in go_create_data: %s", e)
            return {"error": _("Unexpected error: %s") % str(e)}

    def _create_records(self, Model, create_vals):
        if isinstance(create_vals, str):
            try:
                create_vals = ast.literal_eval(create_vals)
            except Exception as e:
                _logger.exception("Failed to parse create_vals: %s", e)
                return {"error": _("Invalid create_vals format: %s") % str(e)}

        if isinstance(create_vals, dict):
            create_vals = [create_vals]

        if not isinstance(create_vals, list) or not all(
            isinstance(v, dict) for v in create_vals
        ):
            return {
                "error": _("create_vals must be a dictionary or a list of dictionaries")
            }

        res = []
        for vals in create_vals:
            try:
                record = Model.create(vals)
                if record:
                    res.append(record.id)
            except Exception as e:
                _logger.exception("Failed to create record: %s", e)
                return {"error": _("Failed to create record: %s") % str(e)}

        if len(res) == 1:
            return {"success": _("Record successfully created"), "id": res[0]}
        else:
            return {"success": _("Records successfully created"), "ids": res}

    import ast

    def _call_method_on_record(self, record, method_name, args=None, kwargs=None):
        if not record.exists():
            return {"error": _("Record with ID %s not found") % record.id}

        args = args or []
        kwargs = kwargs or {}

        if not isinstance(args, list):
            return {"error": _("Args must be a list")}
        if not isinstance(kwargs, dict):
            return {"error": _("Kwargs must be a dictionary")}

        try:
            result = getattr(record, method_name)(*args, **kwargs)
            return {"success": result}
        except Exception as e:
            return {"error": _("Method call failed: %s") % e}

    @http.route(
        ["/go/api/<string:model>/<int:id>/method/<string:method_name>"],
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def go_method_call(self, model=None, id=None, method_name=None, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            Model = self._get_model(model, current_user)
            if isinstance(Model, dict):
                return Model

            record = Model.browse(id)

            args, kwargs = [], {}
            if "args" in data:
                try:
                    args = ast.literal_eval(data["args"])
                except Exception:
                    return {"error": _("Invalid args format, should be a Python list")}
            if "kwargs" in data:
                try:
                    kwargs = ast.literal_eval(data["kwargs"])
                except Exception:
                    return {
                        "error": _("Invalid kwargs format, should be a Python dict")
                    }

            return self._call_method_on_record(record, method_name, args, kwargs)

        except Exception as e:
            return {"error": _("Unexpected error: %s") % e}

    @http.route(
        "/website/get_languages",
        type="json",
        auth='user',
        website=True,
        csrf=False,
        methods=["POST"],
    )
    def website_languages(self, **kwargs):
        website = request.website
        languages = website.sudo().language_ids  # ensure safe access
        return [
            {"code": lg.code, "url_code": lg.url_code, "name": lg.name}
            for lg in languages
        ]


