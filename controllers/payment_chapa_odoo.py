from odoo import http
from odoo.http import request
import json
import requests
import time
from odoo.http import Response
from odoo.exceptions import ValidationError


class Paymentchapa(http.Controller): 
    _return_url = '/get-status-chapa'


    @http.route('/get-status-webhook-chapa', type='json', auth='public',
            methods=['POST'], csrf=False, save_session=False, web=True)
    def chapa_return_webhook(self, **kw):
        data = json.loads(request.httprequest.data)
        callback = data['event'].split('.')[-1]
        trx_ref = data['tx_ref']
        provider = request.env['payment.provider'].sudo().search([('code','=','chapa')])
        private_key=provider.chapa_private_key
        if not trx_ref:
            return Response(json.dumps({"error": "Missing required parameters"}), content_type="application/json", status=400)
        url = f"https://api.chapa.co/v1/transaction/verify/{trx_ref}"
        payload = ''
        headers = {
            'Authorization': f'Bearer {private_key}'
        }

        response = requests.get(url, headers=headers, data=payload)
        data = response.json()
        status = data["status"]
        stat = "Error"
        if status.lower() == "success":
            stat = "Done"
        data = {
            "cartId": trx_ref,
            "respStatus": stat
        }
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'chapa', data)
        tx_sudo._handle_notification_data('chapa', data)
        response_data = {
            "state": tx_sudo.state,
            "tx_id": tx_sudo.id,
            "android_url": request.env['ir.config_parameter'].sudo().get_param('web.base.url') + "/payment/status/poll",
            "web_url": request.env['ir.config_parameter'].sudo().get_param('web.base.url') + "/payment/status"
        }

        if callback:
            response_text = f"{callback}({json.dumps(response_data)})"
            content_type = "application/javascript"
        else:
            response_text = json.dumps(response_data)
            content_type = "application/json"

        return Response(response_text, content_type=content_type, status=200)

        



    @http.route('/get-status-chapa', type='http', auth='public',
            methods=['GET','POST'], csrf=False, save_session=False, web=True)
    def chapa_return(self, **kw):

        # Check if a callback parameter exists for JSONP
        callback = kw.get('callback')
        trx_ref = kw.get('trx_ref')
        # Validate required parameters
        provider = request.env['payment.provider'].sudo().search([('code','=','chapa')])
        private_key=provider.chapa_private_key
        if not trx_ref:
            return Response(json.dumps({"error": "Missing required parameters"}), content_type="application/json", status=400)
        url = f"https://api.chapa.co/v1/transaction/verify/{trx_ref}"
        payload = ''
        headers = {
            'Authorization': f'Bearer {private_key}'
        }

        response = requests.get(url, headers=headers, data=payload)
        data = response.json()
        status = data["status"]
        
        # Process the request
        stat = "Error"
        if status.lower() == "success":
            stat = "Done"
        data = {
            "cartId": trx_ref,
            "respStatus": stat
        }
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'chapa', data)
        tx_sudo._handle_notification_data('chapa', data)
        return {
            
        }