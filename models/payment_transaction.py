import logging
from werkzeug import urls
from odoo import api, models, _,fields
from odoo.exceptions import ValidationError
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_chapa.controllers.payment_chapa_odoo import Paymentchapa

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    chapa_type = fields.Char(string="chapa Transaction Type")
    @api.model
    def _compute_reference(self, provider_code, prefix=None, separator='-',
                           **kwargs):
        if provider_code == 'chapa':
            prefix = payment_utils.singularize_reference_prefix()
        return super()._compute_reference(provider_code, prefix=prefix,
                                          separator=separator, **kwargs)

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'chapa':
            return res
        return self.execute_payment()

    def execute_payment(self):
        api_url = self.provider_id.chapa_payment_initialize_url
        chapa_values = {
            "amount": self.amount,
            "currency":self.currency_id.symbol,
            "email": self.partner_email,
            "tx_ref":   self.reference,
            'return': urls.url_join(self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
                                    Paymentchapa._return_url),
            'callback': urls.url_join(self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
                                      Paymentchapa._return_url),
            'first_name':self.partner_name,
            'phone_number':self.partner_phone,
            'provider_id':self.provider_id.id,
        }
        response_content = self.provider_id._chapa_make_request(
            api_url, chapa_values)
        return response_content

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code,
                                                    notification_data)
        if provider_code != 'chapa':
            return tx
        reference = notification_data.get('cartId', False)
        if not reference:
            raise ValidationError(_("chapa: No reference found."))
        tx = self.search(
            [('reference', '=', reference), ('provider_code', '=', 'chapa')])
        if not tx:
            raise ValidationError(
                _("chapa: No transaction found matching reference"
                  "%s.") % reference)
        return tx

    def _handle_notification_data(self, provider_code, notification_data):
        tx = self._get_tx_from_notification_data(provider_code,
                                                 notification_data)
        tx._process_notification_data(notification_data)
        tx._execute_callback()
        return tx

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'chapa':
            return
        status = notification_data.get('respStatus')
        if status == 'Done':
            self._set_done(state_message="Authorised")
        elif status == 'APPROVED':
            self._set_pending(state_message="Chapa Authorised but on hold for "
                                            "further anti-fraud review")
        elif status in ('E', 'D'):
            self._set_canceled(state_message="Error")
        else:
            _logger.warning("Received unrecognized payment state %s for "
                            "transaction with reference %s",
                            status, self.reference)
            self._set_error("chapa: " + _("Invalid payment status."))
