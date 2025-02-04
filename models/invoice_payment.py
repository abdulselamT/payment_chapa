from odoo import models, fields
class AccountMove(models.Model):
    _inherit = 'account.move'
    def paywithterminal(self):
        vals={
            "res_model":'account.move',
            "res_id":self.id,
        }
        vals.update(self._get_default_payment_link_values())
        payment=self.env['payment.link.wizard'].create(vals)
        return {
            'type':'ir.actions.act_url',
            'target':'self',
            'url':payment.link
        }