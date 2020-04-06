# # Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# from odoo import api, fields, models, _
# from odoo.addons import decimal_precision as dp
# from odoo.exceptions import UserError, ValidationError
# from odoo.tools import float_round
# import logging
# _logger = logging.getLogger(__name__)
#
#
# class MrpBomLines(models.Model):
#     _inherit = 'mrp.bom.line'
#
#     check_box = fields.Boolean('Round Up')
#
#     @api.one
#     def method(self):
#     for line in self.check_box:
#              line.check_box()
#
#     @api.onchange('check_box')
#     def checkbox_roundup(self):
#         for bom in self:
#             for moves in self.bom_id:
#                 if self.check_box == True:
#                     # raise UserError('Error')
#                     moves.product_qty = round(moves.product_qty)
#
#     # @api.multi
#     # def write(self, vals):
#     #     for production in self:
#     #         for moves in self.move_raw_ids:
#     #                 moves.product_uom_qty = round(moves.product_uom_qty)
#     #     return super(RoundOff,self).write(vals)
