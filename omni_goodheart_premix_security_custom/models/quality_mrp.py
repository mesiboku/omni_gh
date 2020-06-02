from odoo import api, fields, models, _





class QualityMRP(models.Model):
    _inherit = 'mrp.workorder'

    # box_number = fields.Integer('Box Number')
    # categ_id = fields.Many2one("product.category",related="product_id.categ_id")
