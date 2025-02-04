import logging
import requests
from odoo import http
import random
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import json
import base64
import binascii
from odoo.exceptions import AccessError


_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'
    code = fields.Selection(selection_add=[('chapa', 'chapa')],
                            ondelete={'chapa': 'set default'},
                            help="The technical code of this payment provider",
                            string="Code")
    chapa_public_api_key = fields.Char(
        string="Chapa Public API Key", help="The API key of the webservice user", required_if_provider='chapa',
        groups='base.group_system')
    chapa_private_key = fields.Char(
        string="Chapa Private Key", help="The client key of the webservice user",
        required_if_provider='chapa')
    chapa_payment_initialize_url = fields.Char(
        string = "Payment INitialize endpoint",
        default="https://api.chapa.co/v1/transaction/initialize"
    )
    
    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['chapa'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res

    def _chapa_make_request(self, url, payload=None, method='GET'):
        callback_url= self.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/get-status-chapa"
        return_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/payment/status"
        payload['customization'] ={
                    "title": "Payment",
                    "description": "Payment For ..."
                    }
        
        payload["callback_url"]=callback_url,
        payload["return_url"]=return_url
        headers = {
            'Authorization': f'Bearer {self.chapa_private_key}',
            'Content-Type': 'application/json'
            }
        self.ensure_one()
        print(payload)
        print(callback_url)
        response = requests.post(self.chapa_payment_initialize_url, json=payload, headers=headers)
        response_content = response.json()
        print(response_content)
        payload["api_url"] = response_content['payload']["checkout_url"]
        return payload
    
 