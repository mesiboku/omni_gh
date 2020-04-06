from odoo import api, fields, models, _


class EquipmentField(models.Model):
	_inherit = 'mrp.production'

	equips = fields.Many2one(
        'maintenance.equipment', 'Equipment',
        index=True, ondelete='cascade', required=True)



class EquipmentFieldWO(models.Model):
	_inherit = 'mrp.workorder'

	equips_id = fields.Many2one( 'maintenance.equipment', 'Equipment', related='production_id.equips')
