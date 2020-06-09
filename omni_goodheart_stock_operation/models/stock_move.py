from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.addons import decimal_precision as dp


class StockMoves(models.Model):
    _inherit ='stock.move'

    purchase_order_uom_id = fields.Many2one('product.uom',related='purchase_line_id.product_uom', string='Unit of Measurement Purchase')
    purchase_ordered_qty = fields.Float(digits=0,related='purchase_line_id.product_qty', string='Qty Purchase')
    show_purchase_order_property = fields.Boolean(compute='_compute_show_po_property', string="Is Show Purchase")
    purchase_quantity_done = fields.Float('Quantity Done', digits=dp.get_precision('Product Unit of Measure'), compute='_quantity_po_done_compute')


    purchase_remaining_quantity = fields.Float('Remaining Quantity', digits=dp.get_precision('Product Unit of Measure'), compute='_remaining_quantity_compute')

    purchase_qty_received = fields.Float(digits=dp.get_precision('Product Unit of Measure'),related='purchase_line_id.qty_received', string='Qty Received')


    @api.depends('move_line_ids.purchase_qty_done', 'move_line_ids.purchase_order_uom_id')
    def _quantity_po_done_compute(self):
    	for move in self:
    		quantity_done = 0
    		for move_line in move._get_move_lines():
    			quantity_done += move_line.purchase_order_uom_id._compute_quantity(move_line.purchase_qty_done, move.purchase_order_uom_id, round=False)
    		move.purchase_quantity_done = quantity_done

    @api.depends('move_line_ids.purchase_qty_done', 'move_line_ids.purchase_order_uom_id')
    def _remaining_quantity_compute(self):
        for move in self:
            move.purchase_remaining_quantity = move.purchase_ordered_qty - move.purchase_line_id.qty_received


    @api.one
    @api.depends('purchase_line_id')
    def _compute_show_po_property(self):
    	if self.purchase_line_id:
    		self.show_purchase_order_property = False
    	else:
    		self.show_purchase_order_property = True

    @api.onchange('purchase_quantity_done', 'purchase_order_uom_id')
    def _change_purchase_qty_done(self):
        if self.purchase_order_uom_id != self.product_uom:
            uom_purchase_factor = 0.0
            if self.purchase_order_uom_id.uom_type == 'bigger':
                uom_purchase_factor = self.purchase_order_uom_id.factor_inv
            elif self.purchase_order_uom_id.uom_type == 'smaller':
                uom_purchase_factor = self.purchase_order_uom_id.factor
            else:
                uom_purchase_factor = 1
            uom_factor = 0.0
            if self.product_uom.uom_type == 'bigger':
                uom_factor = self.product_uom.factor_inv
            elif self.product_uom.uom_type == 'smaller':
                uom_factor = self.product_uom.factor
            else:
                uom_factor = 1
            self.quantity_done = (self.purchase_quantity_done * uom_purchase_factor) * uom_factor
        else:
            self.quantity_done = self.purchase_quantity_done
    	#self.quantity_done = (self.purchase_quantity_done * self.purchase_order_uom_id.factor) * self.product_uom_id.factor

    @api.multi
    def product_price_update_before_done(self, forced_qty=None):
        return super(StockMoves, self).product_price_update_before_done(forced_qty)

    def _action_done(self):        
        #---------------------- START in Stock Account
        self.product_price_update_before_done()
        #---------------------- END in Stock Account Module


        #---------------------- START in stock Module
        self.filtered(lambda move: move.state == 'draft')._action_confirm()

        moves = self.filtered(lambda x: x.state not in ('done', 'cancel'))
        moves_todo = self.env['stock.move']
        # Cancel moves where necessary ; we should do it before creating the extra moves because
        # this operation could trigger a merge of moves.
        for move in moves:
            if move.quantity_done <= 0:
                if float_compare(move.product_uom_qty, 0.0, precision_rounding=move.product_uom.rounding) == 0:
                    move._action_cancel()

        # Create extra moves where necessary
        for move in moves:
            if move.state == 'cancel' or move.quantity_done <= 0:
                continue
            # extra move will not be merged in mrp
            if not move.picking_id:
                moves_todo |= move
            moves_todo |= move._create_extra_move()

        # Split moves where necessary and move quants
        for move in moves_todo:
            rounding = move.product_uom.rounding
            if float_compare(move.quantity_done, move.product_uom_qty, precision_rounding=rounding) < 0:
                # Need to do some kind of conversion here
                qty_split = move.product_uom._compute_quantity(move.product_uom_qty - move.quantity_done, move.product_id.uom_id, rounding_method='HALF-UP')
                new_move = move._split(qty_split)
                for move_line in move.move_line_ids:
                    if move_line.product_qty and move_line.qty_done:
                        # FIXME: there will be an issue if the move was partially available
                        # By decreasing `product_qty`, we free the reservation.
                        # FIXME: if qty_done > product_qty, this could raise if nothing is in stock

                        try:
                            move_line.write({'product_uom_qty': move_line.qty_done})
                        except UserError:
                            pass

                # If you were already putting stock.move.lots on the next one in the work order, transfer those to the new move
                move.move_line_ids.filtered(lambda x: x.qty_done == 0.0).write({'move_id': new_move})
            move.move_line_ids._action_done()
        # Check the consistency of the result packages; there should be an unique location across
        # the contained quants.
        # This Will Be Remove 
        # This CODE BLOCK IS THE CULPRIT FOR THIS ABOMINATION...
        #for result_package in moves_todo\
        #    .mapped('move_line_ids.result_package_id')\
        #    .filtered(lambda p: p.quant_ids and len(p.quant_ids) > 1):

        #    if len(result_package.quant_ids.mapped('location_id')) > 1:
        #        raise UserError(_('You should not put the contents of a package in different locations.'))
        # This CODE BLOCK IS THE CULPRIT FOR THIS ABOMINATION...



        picking = moves_todo and moves_todo[0].picking_id or False
        moves_todo.write({'state': 'done', 'date': fields.Datetime.now()})
        moves_todo.mapped('move_dest_ids')._action_assign()


        # We don't want to create back order for scrap moves
        if all(move_todo.scrapped for move_todo in moves_todo):
            return moves_todo

        if picking:
            picking._create_backorder()

        #---------------------- END in stock Module




        #---------------------- START in Stock Account Module
        # ---- for move in res: ORIGINAL

        for move in moves_todo:
            # Apply restrictions on the stock move to be able to make
            # consistent accounting entries.
            if move._is_in() and move._is_out():
                raise UserError(_("The move lines are not in a consistent state: some are entering and other are leaving the company. "))
            company_src = move.mapped('move_line_ids.location_id.company_id')
            company_dst = move.mapped('move_line_ids.location_dest_id.company_id')
            try:
                if company_src:
                    company_src.ensure_one()
                if company_dst:
                    company_dst.ensure_one()
            except ValueError:
                raise UserError(_("The move lines are not in a consistent states: they do not share the same origin or destination company."))
            if company_src and company_dst and company_src.id != company_dst.id:
                raise UserError(_("The move lines are not in a consistent states: they are doing an intercompany in a single step while they should go through the intercompany transit location."))
            move._run_valuation()

        # for move in res.filtered(lambda m: m.product_id.valuation == 'real_time' and (m._is_in() or m._is_out() or m._is_dropshipped())): ORIGINAL
        for move in moves_todo.filtered(lambda m: m.product_id.valuation == 'real_time' and (m._is_in() or m._is_out() or m._is_dropshipped())):
            move._account_entry_move()

        #---------------------- END in Stock Account Module



        #---------------------- START in Sale Stock Module

        #for line in result.mapped('sale_line_id').sudo(): ORIGINAL
        for line in moves_todo.mapped('sale_line_id').sudo():
            line.qty_delivered = line._get_delivered_qty()

        #---------------------- END in Sale Stock Module

        return moves_todo
        #super(StockMovesLines, self)._action_done()



class StockMovesLines(models.Model):
    _inherit = 'stock.move.line'

    purchase_line_move_id = fields.Many2one('purchase.order.line',related='move_id.purchase_line_id', string='Purchase Order Line',store=True)
    purchase_order_uom_id = fields.Many2one('product.uom',related='purchase_line_move_id.product_uom', string='Unit of Measurement Purchase',store=True)
    purchase_ordered_qty = fields.Float(digits=0,related='purchase_line_move_id.product_qty', string='Qty Purchase',store=True)
    purchase_qty_received = fields.Float(digits=dp.get_precision('Product Unit of Measure'),related='purchase_line_move_id.qty_received', string='Qty Received',store=True)
    purchase_qty_done = fields.Float('Done', default=0.0, digits=dp.get_precision('Product Unit of Measure'), copy=False)

    purchase_remaining_quantity = fields.Float('Remaining Quantity', related="move_id.purchase_remaining_quantity")


    is_product_route_manuf = fields.Boolean(string='To Manufacture', compute='_getProductToManufacture')

    @api.one
    @api.depends('product_id')
    def _getProductToManufacture(self):
        isProdManufact = False
        if self.product_id:            
            if self.env.ref('mrp.route_warehouse0_manufacture').id in self.product_id.route_ids.ids:
                isProdManufact = True
        self.is_product_route_manuf = isProdManufact

    @api.onchange('package_id','result_package_id')
    def _change_result_package_id(self):        
        if self.package_id:
            #if not 
            self.result_package_id = self.package_id.id
            
    @api.onchange('package_id','result_package_id')
    def _change_result_package_id_2(self):
        self.qty_done = 0.0
        stock_quant_model = self.env['stock.quant']
        if self.result_package_id or self.package_id:
            #Get The Qty Value
            stock_quant_obj = stock_quant_model.search([('package_id', '=', self.package_id.id),
                                                        ('product_id', '=', self.product_id.id),
                                                        ('location_id', '=', self.package_id.location_id.id)])
            quantity = 0.0
            for quant in stock_quant_obj:
                quantity += quant.quantity

            if stock_quant_obj:
                self.qty_done = quantity

    @api.onchange('purchase_qty_done', 'purchase_order_uom_id')
    def _change_purchase_qty_done(self):
        res = {}
        if self.purchase_qty_done and self.product_id.tracking == 'serial':
            if float_compare(self.purchase_qty_done, 1.0, precision_rounding=self.move_id.product_id.uom_id.rounding) != 0:
                message = _('You can only process 1.0 %s for products with unique serial number.') % self.product_id.uom_id.name
                res['warning'] = {'title': _('Warning'), 'message': message}
        if self.purchase_order_uom_id != self.product_uom_id:
            uom_purchase_factor = 0.0
            if self.purchase_order_uom_id.uom_type == 'bigger':
                uom_purchase_factor = self.purchase_order_uom_id.factor_inv
            elif self.purchase_order_uom_id.uom_type == 'smaller':
                uom_purchase_factor = self.purchase_order_uom_id.factor
            else:
                uom_purchase_factor = 1
            uom_factor = 0.0
            if self.product_uom_id.uom_type == 'bigger':
                uom_factor = self.product_uom_id.factor_inv
            elif self.product_uom_id.uom_type == 'smaller':
                uom_factor = self.product_uom_id.factor
            else:
                uom_factor = 1

            self.qty_done = (self.purchase_qty_done * uom_purchase_factor) * uom_factor
        else:
            self.qty_done = self.purchase_qty_done
        return res

    
    
        

    def _action_done(self):        
        for ml in self:
            purchase_qty_done = 0.0
            if ml.purchase_line_move_id:
                if ml.purchase_order_uom_id != ml.product_uom_id:
                    uom_purchase_factor = 0.0
                    uom_factor = 0.0
                    if ml.purchase_order_uom_id.uom_type == 'bigger':
                        uom_purchase_factor = ml.purchase_order_uom_id.factor_inv
                    elif ml.purchase_order_uom_id.uom_type == 'smaller':
                        uom_purchase_factor = ml.purchase_order_uom_id.factor_inv
                    else:
                        uom_purchase_factor = 1

                    if ml.product_uom_id.uom_type == 'bigger':
                        uom_factor = ml.product_uom_id.factor
                    elif ml.product_uom_id.uom_type == 'smaller':
                        uom_factor = ml.product_uom_id.factor
                    else:
                        uom_factor = 1

                    purchase_qty_done = (ml.qty_done/uom_factor) / uom_purchase_factor

                else:
                    purchase_qty_done = ml.qty_done
            ml.write({
                'purchase_qty_done':purchase_qty_done
                })

        super(StockMovesLines, self)._action_done()
