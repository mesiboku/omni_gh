from odoo import api, fields, models, _, tools
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import logging
import math
_logger = logging.getLogger(__name__)

class WorkOrderProduct(models.Model):
    _inherit = 'mrp.production'

    def _get_start_date(self):
        return datetime.now()

    @api.multi
    def button_plan(self):
        # res = super(WorkOrderProduct, self)
        orders_to_plan = self.filtered(lambda order: order.routing_id and order.state == 'confirmed')
        for order in orders_to_plan:
            # x = 0
            for order_line in orders_to_plan.move_raw_ids:
                if order_line.product_uom_qty >  order_line.reserved_availability:
                    raise UserError(_('Cannot Create Work Order Stock Incomplete!'))

        res = super(WorkOrderProduct, self).button_plan()
        # Check if Successfully Saved the Records
        # Update the Work Orders Equipments
        if res:
            for mrp_prod in self:
                mrp_workorder_obj = self.env['mrp.workorder'].search([('production_id','=', mrp_prod.id)])
                if mrp_workorder_obj:
                    for workorder in mrp_workorder_obj:
                        workorder.equips_id = mrp_prod.equips.id
        return res 
