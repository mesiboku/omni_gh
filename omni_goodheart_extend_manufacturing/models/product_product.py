# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.addons import decimal_precision as dp

from odoo.exceptions import UserError, ValidationError

from odoo import api, fields, models, _, SUPERUSER_ID

class ProductProduct(models.Model):
	_inherit= 'product.product'

	related_product_id = fields.Many2one('product.product', string="Related Product")
	is_check_related_product = fields.Boolean(string="Check For Related Product", default=False)