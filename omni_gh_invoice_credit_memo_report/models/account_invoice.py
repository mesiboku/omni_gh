from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.addons import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)



class AccountInvoice(models.Model):
    _inherit = 'account.invoice'



    @api.multi
    def _getTotalDiscount(self):

        total_discount = 0
        for inv in self.invoice_line_ids:

            total_discount += inv.price_unit * (inv.discount/100)
            
        return total_discount


    @api.multi
    def _getTotalTaxes(self):
        total_tax = 0
        for x in self.invoice_line_ids:
            for y in x.invoice_line_tax_ids:
                if y.amount < 0:
                    # (y.amount/100) * (l.price_unit - (l.price_unit * (l.discount/100)))
                    data = (y.amount/100) * (x.price_unit - (x.discount/100))
                    total_tax += data
        return total_tax

