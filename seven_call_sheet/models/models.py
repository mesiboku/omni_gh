# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 
import logging
_logger = logging.getLogger(__name__)

import xlwt 
import xlrd
import datetime
import base64
import os, sys
from odoo.exceptions import UserError, AccessError

from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

import odoo.tools as tools

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


class GHCallSheet(models.Model):
	_name = 'seven_call_sheet.call_sheet'
	_description = 'Seven Eleven Call Sheet'
	_order = 'call_date desc, id desc'

	name = fields.Char(string='CS No.', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

	call_date = fields.Date(
		string='Date',
		default=fields.Datetime.now()
	)

	call_sheet_line_ids = fields.One2many(
		'seven_call_sheet.call_sheet_line',
		'call_sheet_id',
		string='Order Lines',
	)

	state = fields.Selection([
		('draft', 'DRAFT'),
		('submitted', 'SUBMITTED')
	], default="draft")

	#CHANGES MADE SDS
	@api.one
	def _getFilename(self):
		self.filename = '%s.xls' % self.name

	filename = fields.Char('file name',compute ='_get_filename')
	coll_sheet_file_import = fields.Binary(string='Collection Sheet Excel')
	coll_sheet_file_export = fields.Binary(string='Collection Sheet Excel Template') #, default=lambda self:self._get_default_file()
	coll_sheet_file_export_with_area = fields.Binary(string='Collection Sheet Excel Template.xls')


	cone_1_label = fields.Char('Cone 1 Column name')
	cone_2_label = fields.Char('Cone 2 Column name')
	cone_3_label = fields.Char('Cone 3 Column name')

	cone_4_label = fields.Char('Cone 4 Column name')
	cone_5_label = fields.Char('Cone 5 Column name')
	cone_6_label = fields.Char('Cone 6 Column name')
	cone_7_label = fields.Char('Cone 7 Column name')
	cone_8_label = fields.Char('Cone 8 Column name')
	cone_9_label = fields.Char('Cone 9 Column name')
	cone_10_label = fields.Char('Cone 10 Column name')


	def _get_filename(self):
		self.filename =  "1.xls"

	@api.model
	def _get_default_file(self):
		addons_paths = tools.config['addons_path']
		addons_lists = addons_paths.split(',')
		xls_dir_path = ""
		if os.path.isdir('/odoo/TemporaryFiles'):
			xls_dir_path = '/odoo/TemporaryFiles'
		else:
			for addons_list in addons_lists:
				if os.path.isdir(addons_list + '/seven_call_sheet'):
					xls_dir_path = addons_list + '/seven_call_sheet'
					break
		FILENAME = xls_dir_path + '/call_sheet_template.xls'
		#FILENAME = '/odoo/TemporaryFiles/call_sheet_template.xls'
		with open(FILENAME, "rb") as file:
			return  base64.b64encode(file.read())


	def _getStringValue(self, value):
		if isinstance(value, float):
			value = str(int(value))
		elif isinstance(value, int):
			value = str(value)
		return value


	call_date_submitted = fields.Datetime(string='Date Submitted', copy=False)

	sale_ids = fields.Many2many('sale.order', string='Sales Order', copy=False)
	picking_ids = fields.Many2many('stock.picking', string='Delivery Order', copy=False)
	invoice_ids = fields.Many2many('account.invoice', string='Sales Invoice', copy=False)

	sale_count = fields.Integer(string='Sale Orders', compute='_compute_sale_ids')
	delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')
	invoice_count = fields.Integer(string='# of Invoices', compute='_compute_invoice_ids', readonly=True)

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('goodheart.cs') or _('New')
		result = super(GHCallSheet, self).create(vals)
		return result

	@api.depends('sale_ids')
	def _compute_sale_ids(self):
		for order in self:
			order.sale_count = len(order.sale_ids)

	@api.depends('picking_ids')
	def _compute_picking_ids(self):
		for order in self:
			order.delivery_count = len(order.picking_ids)

	@api.depends('invoice_ids')
	def _compute_invoice_ids(self):
		for order in self:
			order.invoice_count = len(order.invoice_ids)

	@api.depends('call_sheet_line_ids')
	def _update_cone_lines(self):
		for rec in self:

			c1 = 0
			c2 = 0
			c3 = 0
			c4 = 0
			c5 = 0
			c6 = 0
			c7 = 0
			c8 = 0
			c9 = 0
			c10 = 0
			for line in rec.call_sheet_line_ids:
				c1 += line.cone_1
				c2 += line.cone_2
				c3 += line.cone_3
				c4 += line.cone_4
				c5 += line.cone_5
				c6 += line.cone_6
				c7 += line.cone_7
				c8 += line.cone_8
				c9 += line.cone_9
				c10 += line.cone_10

			rec.total_cone_1 = c1
			rec.total_cone_2 = c2
			rec.total_cone_3 = c3
			rec.total_cone_4 = c4
			rec.total_cone_5 = c5
			rec.total_cone_6 = c6
			rec.total_cone_7 = c7
			rec.total_cone_8 = c8
			rec.total_cone_9 = c9
			rec.total_cone_10 = c10

	@api.model
	def _default_cone_1(self):
		product_id = self.env['product.product'].search([('name','=','RDCS-SPS-09 (kit)')], limit=1)
		return product_id

	@api.model
	def _default_cone_2(self):
		product_id = self.env['product.product'].search([('name','=','RDCS-SPS-26-CNLD (kit)')], limit=1)
		return product_id

	@api.model
	def _default_cone_3(self):
		product_id = self.env['product.product'].search([('name','=','RDCS-SPS-22-CNLD (kit)')], limit=1)
		return product_id

	@api.model
	def _default_cone_uom_delv(self):		
		#product_uom_id = self.env['product.uom'].search([('name','=','box(144pcs)')], limit=1)
		product_uom_id = self.env['product.uom'].search([('id','=',42)], limit=1)
		return product_uom_id


	sales_area_id = fields.Many2one(
		'partner_seven_extension.sales_area',
		string='Sales Area',
	)

	cone_1_id = fields.Many2one(
		'product.product',
		string='Cone 1',
		required=True,
		default=_default_cone_1,
	)

	cone_2_id = fields.Many2one(
		'product.product',
		string='Cone 2',
		required=True,
		default=_default_cone_2,
	)

	cone_3_id = fields.Many2one(
		'product.product',
		string='Cone 3',
		required=True,
		default=_default_cone_3,
	)

	cone_4_id = fields.Many2one(
		'product.product',
		string='Cone 4',
		required=True,
		default=_default_cone_1,
	)

	cone_5_id = fields.Many2one(
		'product.product',
		string='Cone 5',
		required=True,
		default=_default_cone_2,
	)

	cone_6_id = fields.Many2one(
		'product.product',
		string='Cone 6',
		required=True,
		default=_default_cone_3,
	)

	cone_7_id = fields.Many2one(
		'product.product',
		string='Cone 7',
		required=True,
		default=_default_cone_1,
	)

	cone_8_id = fields.Many2one(
		'product.product',
		string='Cone 8',
		required=True,
		default=_default_cone_2,
	)

	cone_9_id = fields.Many2one(
		'product.product',
		string='Cone 9',
		required=True,
		default=_default_cone_3,
	)

	cone_10_id = fields.Many2one(
		'product.product',
		string='Cone 10',
		required=True,
		default=_default_cone_3,
	)

	cone_1_product_uom = fields.Many2one(
		'product.uom',
		string= 'Cone 1 UOM',
		required=True,
		default=_default_cone_uom_delv,
	)
	cone_2_product_uom = fields.Many2one(

		'product.uom',
		string= 'Cone 2 UOM',
		required=True,
		default=_default_cone_uom_delv,
	)
	cone_3_product_uom = fields.Many2one(

		'product.uom',
		string= 'Cone 3 UOM',
		required=True,
		default=_default_cone_uom_delv,
	)


	cone_4_product_uom = fields.Many2one(

		'product.uom',
		string= 'Cone 4 UOM',
		required=True,
		default=_default_cone_uom_delv,
	)
	cone_5_product_uom = fields.Many2one(

		'product.uom',
		string= 'Cone 5 UOM',
		required=True,
		default=_default_cone_uom_delv,
	)
	cone_6_product_uom = fields.Many2one(

		'product.uom',
		string= 'Cone 6 UOM',
		required=True,
		default=_default_cone_uom_delv,
	)	
	cone_7_product_uom = fields.Many2one(

		'product.uom',
		string= 'Cone 7 UOM',
		required=True,
		default=_default_cone_uom_delv,
	)
	cone_8_product_uom = fields.Many2one(

		'product.uom',
		string= 'Cone 8 UOM',
		required=True,
		default=_default_cone_uom_delv,
	)
	cone_9_product_uom = fields.Many2one(

		'product.uom',
		string= 'Cone 9 UOM',
		required=True,
		default=_default_cone_uom_delv,
	)	
	cone_10_product_uom = fields.Many2one(

		'product.uom',
		string= 'Cone 10 UOM',
		required=True,
		default=_default_cone_uom_delv,
	)


	total_cone_1 = fields.Integer(
		string='Cone 1 Total',
		compute="_update_cone_lines",
		store=True
	)

	total_cone_2 = fields.Integer(
		string='Cone 2 Total',
		compute="_update_cone_lines",
		store=True
	)

	total_cone_3 = fields.Integer(
		string='Cone 3 Total',
		compute="_update_cone_lines",
		store=True
	)

	total_cone_4 = fields.Integer(
		string='Cone 4 Total',
		compute="_update_cone_lines",
		store=True
	)

	total_cone_5 = fields.Integer(
		string='Cone 5 Total',
		compute="_update_cone_lines",
		store=True
	)

	total_cone_6 = fields.Integer(
		string='Cone 7 Total',
		compute="_update_cone_lines",
		store=True
	)

	total_cone_7 = fields.Integer(
		string='Cone 7 Total',
		compute="_update_cone_lines",
		store=True
	)

	total_cone_8 = fields.Integer(
		string='Cone 8 Total',
		compute="_update_cone_lines",
		store=True
	)

	total_cone_9 = fields.Integer(
		string='Cone 9 Total',
		compute="_update_cone_lines",
		store=True
	)

	total_cone_10 = fields.Integer(
		string='Cone 10 Total',
		compute="_update_cone_lines",
		store=True
	)

	price_box = fields.Float(
		string='Cone 1 Price',
	)

	price_box_2 = fields.Float(
		string='Cone 2 Price',
	)

	price_box_3 = fields.Float(
		string='Cone 3 Price',
	)

	price_box_4 = fields.Float(
		string='Cone 4 Price',
	)

	price_box_5 = fields.Float(
		string='Cone 5 Price',
	)

	price_box_6 = fields.Float(
		string='Cone 6 Price',
	)

	price_box_7 = fields.Float(
		string='Cone 7 Price',
	)

	price_box_8 = fields.Float(
		string='Cone 8 Price',
	)

	price_box_9 = fields.Float(
		string='Cone 9 Price',
	)

	price_box_10 = fields.Float(
		string='Cone 10 Price',
	)

	tax_id = fields.Many2one(
		'account.tax',
		string='VAT',
	)

	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

	warehouse_id = fields.Many2one(
		'stock.warehouse',
		string='Warehouse',
		required=True
	)
	
	def area_changed(self):
		for rec in self:
			for s in rec.call_sheet_line_ids:
				s.unlink()

		pt = self.env['res.partner']
		ids = pt.search([('parent_id.name','=','Philippine Seven Corporation'),
			('area_id.id','=',self.sales_area_id.id), ('active','=',True)])

		for store_id in ids:
			_logger.info("This is my debug message ! ")
			_logger.info(store_id.id)
			for rec in self:
				rec.write({
					'call_sheet_line_ids': [(0,0,{
						'partner_id': store_id.id,
						'store_status_note': store_id.store_status_note,
						})]
					})

	def getConeQty(self, line, number = 0):
		rec = self
		qty_cone = 0
		unit_price_cone = 0
		if number > 0:
			cone = 'cone_' + str(number) + '_id'
			cone_uom = 'cone_' + str(number) + '_product_uom'
			line_cone = 'cone_' + str(number)
			price_box = 'price_box' if number == 1 else 'price_box_' + str(number)

		bom_obj = self.env['mrp.bom']
		bom_obj_cone = bom_obj.search([('product_tmpl_id','=', rec[cone].product_tmpl_id.id),
									   ('company_id','=', rec.company_id.id) ], limit=1)

		if bom_obj_cone:
			unit_price_cone = self.price_box / bom_obj_cone.product_qty
			qty_cone = line[line_cone] * bom_obj_cone.product_qty
		else:
			#Unit Price per Piece
			if rec[cone_uom].uom_type == 'bigger':
				unit_price_cone = rec[price_box] / rec[cone_uom].factor_inv
				qty_cone = line[line_cone] * rec[cone_uom].factor_inv
			elif rec[cone_uom].uom_type == 'smaller':
				unit_price_cone = rec[price_box] * rec[cone_uom].factor
				qty_cone = line[line_cone] / rec[cone_uom].factor
			else:
				unit_price_cone = rec[price_box] * 1
				qty_cone = line[line_cone] * 1

		return [qty_cone, unit_price_cone]


	@api.multi
	def submit_approval(self):
		#for every line item check if with order
		for rec in self:
			rec.state = 'submitted'
			rec.call_date_submitted = fields.Datetime.now()

			sale_ids = []
			picking_ids = []
			invoice_ids= []

			for line in rec.call_sheet_line_ids:
				# UPDATE STORE STATUS NOTE IN PARTNER RECORD
				partner = self.env['res.partner'].search([('id','=',line.partner_id.id)])
				call_sheet_line_obj = self.env['seven_call_sheet.call_sheet_line'].search([('id', '=', line.id)])
				if partner:
					partner.write({'store_status_note': line.store_status_note})

				total_boxes = line.cone_1 + line.cone_2 + line.cone_3 + line.cone_4 + line.cone_5 + line.cone_6 + line.cone_7 + line.cone_8 + line.cone_9 + line.cone_10

				if (total_boxes > 0):
					if not line.legacy_invoice_number:
						raise UserError(_('Store %s has no Legacy Invoice Number. Please populate the Legacy Invoice Number.' % line.partner_id.name))

					#Convertion of Quantity
					unit_price_cone_1 = 0
					unit_price_cone_2 = 0
					unit_price_cone_3 = 0
					unit_price_cone_4 = 0
					unit_price_cone_5 = 0
					unit_price_cone_6 = 0
					unit_price_cone_7 = 0
					unit_price_cone_8 = 0
					unit_price_cone_9 = 0
					unit_price_cone_10 = 0

					qty_cone_1 = 0
					qty_cone_2 = 0
					qty_cone_3 = 0
					qty_cone_4 = 0
					qty_cone_5 = 0
					qty_cone_6 = 0
					qty_cone_7 = 0
					qty_cone_8 = 0
					qty_cone_9 = 0
					qty_cone_10 = 0


					record_list = {}
					numbers =  [1,2,3,4,5,6,7,8,9,10]
					for number in numbers:
						qty_cone_number = 'qty_cone_' + str(number)
						unit_price_number  =  'unit_price_cone_' + str(number)
						record_list[qty_cone_number], record_list[unit_price_number] = rec.getConeQty(line, number)
					
					#Create Sales Order
					seven_eleven_id = self.env['res.partner'].search([('name','=','Philippine Seven Corporation')])[0]					
					#prepare order lines
					mylist =[]

					for number in numbers:
						cone = 'cone_' + str(number)
						rec_cone = 'cone_' + str(number) + '_id'
						qty_cone_number = 'qty_cone_' + str(number)
						unit_price_number  =  'unit_price_cone_' + str(number)
						if line[cone]:
							mylist.append((0,0,{
							'product_id': rec[rec_cone].id,
							'product_uom_qty': record_list[qty_cone_number],
							'price_unit': record_list[unit_price_number],
							'tax_id': [(6, 0, rec[rec_cone].taxes_id.ids)],
							}))

					if seven_eleven_id:
						so = self.env['sale.order'].sudo().create({
							'partner_id': seven_eleven_id.id,
							'partner_invoice_id': seven_eleven_id.id,
							'partner_shipping_id': line.partner_id.id,
							'warehouse_id': rec.warehouse_id.id,
							'company_id': rec.company_id.id,
							'order_line': mylist
							})

						# LINK SO
						if so:
							sale_ids.append(so.id)
							#Update the Link Sales Order
							call_sheet_line_obj.write(
								{
									'sales_id': so.id
								})

						#Check if it can be confirmed, then confirm
						if (so.pending_ra <= 2):
							so.sudo().action_confirm()

							# LINK PICKING
							picking = self.env['stock.picking'].search([('origin','=', so.name)], limit=1)

							force_company_id = rec.warehouse_id.company_id.id
							picking = self.env['stock.picking'].sudo().with_context(force_company=force_company_id).search([('origin','=', so.name)], limit=1)
							if picking:
								picking.with_context(force_company=force_company_id).write({'company_id': self.env.user.company_id.id})
								picking_ids.append(picking.id)
								#Update the Delivery Order
								call_sheet_line_obj.write({
									'stock_picking_id': picking.id
									})

							#raise Warning(picking.move_lines)
							#Change the UOM of Picking Lines based on Callsheet Lines UOM
							for move_line in picking.move_lines:
								#Check Move lines sale_line_id

								bom_obj =self.env['mrp.bom'] 							
								bom_product = bom_obj.search([('product_tmpl_id','=', move_line.sale_line_id.product_id.product_tmpl_id.id)], limit=1)
								if not bom_product:
									#Check Cone 1
									if rec.cone_1_id.id == move_line.product_id.id:
										move_line.write({
											'product_uom_qty': line.cone_1,
											'product_uom': rec.cone_1_product_uom.id
											})
									#Check Cone 2
									elif rec.cone_2_id.id == move_line.product_id.id:
										move_line.write({
											'product_uom_qty': line.cone_2,
											'product_uom': rec.cone_2_product_uom.id
											})
									#Check Cone 3
									elif rec.cone_3_id.id == move_line.product_id.id:
										move_line.write({
											'product_uom_qty': line.cone_3,
											'product_uom': rec.cone_3_product_uom.id
											})

									#Check Cone 4
									if rec.cone_4_id.id == move_line.product_id.id:
										move_line.write({
											'product_uom_qty': line.cone_4,
											'product_uom': rec.cone_4_product_uom.id
											})
									#Check Cone 5
									elif rec.cone_5_id.id == move_line.product_id.id:
										move_line.write({
											'product_uom_qty': line.cone_5,
											'product_uom': rec.cone_5_product_uom.id
											})
									#Check Cone 6
									elif rec.cone_6_id.id == move_line.product_id.id:
										move_line.write({
											'product_uom_qty': line.cone_6,
											'product_uom': rec.cone_6_product_uom.id
											})

									#Check Cone 7
									elif rec.cone_7_id.id == move_line.product_id.id:
										move_line.write({
											'product_uom_qty': line.cone_7,
											'product_uom': rec.cone_7_product_uom.id
											})
									#Check Cone 8
									elif rec.cone_8_id.id == move_line.product_id.id:
										move_line.write({
											'product_uom_qty': line.cone_8,
											'product_uom': rec.cone_8_product_uom.id
											})
									#Check Cone 9
									elif rec.cone_9_id.id == move_line.product_id.id:
										move_line.write({
											'product_uom_qty': line.cone_9,
											'product_uom': rec.cone_9_product_uom.id
											})

									#Check Cone 10
									else:
										move_line.write({
											'product_uom_qty': line.cone_10,
											'product_uom': rec.cone_10_product_uom.id
											})

							#Check if Invoice Number already Exist
							if line.legacy_invoice_number:
								current_invoice_check = self.env['account.invoice'].search([('number', '=', line.legacy_invoice_number.zfill(5))])
								if current_invoice_check:
									raise UserError(_('Legacy Invoice Number %s already exists. Please Change the Invoice Number.' % line.legacy_invoice_number.zfill(5)))								

							#Raise Invoice
							inv = so.sudo().action_invoice_create()
							# LINK INVOICE
							invoice_ids.append(inv[0])
							call_sheet_line_obj.write({
								'invoice_id': inv[0]})

							current_invoice = self.env['account.invoice'].sudo().search([('id', '=', inv[0])])
							if current_invoice:
								current_invoice.sudo().action_invoice_open()
								current_invoice.sudo().write({'legacy_invoice': line.legacy_invoice_number})
								number = current_invoice.move_id.name
								if number and line.legacy_invoice_number:
									#number_list = number.split('/')
									#move_legacy_invoice_number = number_list[0] + '/' + number_list[1] + '/' + line.legacy_invoice_number.zfill(5)
									current_invoice.move_id.sudo().write({'name': line.legacy_invoice_number.zfill(5)})

						else:
							so.state = "hold"
			
			rec.sale_ids = sale_ids
			rec.picking_ids = picking_ids
			rec.invoice_ids = invoice_ids
		return True
		
	@api.multi
	def action_view_sale(self):
		sales = self.mapped('sale_ids')
		action = self.env.ref('sale.action_orders').read()[0]
		if len(sales) > 1:
			action['domain'] = [('id', 'in', sales.ids)]
		elif len(sales) == 1:
			action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
			action['res_id'] = sales.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		return action

	@api.multi
	def action_view_delivery(self):
		pickings = self.mapped('picking_ids')
		action = self.env.ref('stock.action_picking_tree_all').read()[0]
		if len(pickings) > 1:
			action['domain'] = [('id', 'in', pickings.ids)]
		elif len(pickings) == 1:
			action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
			action['res_id'] = pickings.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		return action

	@api.multi
	def action_view_invoice(self):
		invoices = self.mapped('invoice_ids')
		action = self.env.ref('account.action_invoice_tree1').read()[0]
		if len(invoices) > 1:
			action['domain'] = [('id', 'in', invoices.ids)]
		elif len(invoices) == 1:
			action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
			action['res_id'] = invoices.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		return action


	@api.one
	def generateCollSheetRecord(self):
		uid = self._uid
		addons_paths = tools.config['addons_path']
		addons_lists = addons_paths.split(',')
		xls_dir_path = ""
		if os.path.isdir('/odoo/TemporaryFiles'):
			xls_dir_path = '/odoo/TemporaryFiles'
		else:
			for addons_list in addons_lists:
				if os.path.isdir(addons_list + '/seven_call_sheet'):
					xls_dir_path = addons_list + '/seven_call_sheet'
					break

		FILENAME = xls_dir_path + '/collection_sheet_UID'+str(uid) + '.xls'
		#FILENAME = "/odoo/TemporaryFiles/collection_sheet_UID"+str(uid) +".xls"
		with open(FILENAME, "wb") as f:
			text = self.coll_sheet_file_import
			f.write(base64.b64decode(text))
		xl_workbook = xlrd.open_workbook(FILENAME)
		xl_sheet = xl_workbook.sheet_by_index(0)
		seven_corporation = self.env['res.partner'].search([('name','=', 'Philippine Seven Corporation')])
		seven_call_sheet_line_obj = self.env['seven_call_sheet.call_sheet_line']
		for row in range(1, xl_sheet.nrows):

			store_number = str(int(xl_sheet.cell(row, 0).value or 0))
			store_name = xl_sheet.cell(row, 1).value

			store_address = xl_sheet.cell(row, 2).value
			store_manager = xl_sheet.cell(row, 3).value

			legacy_invoice_number = self._getStringValue(xl_sheet.cell(row, 4).value)

			store_sun_number = self._getStringValue(xl_sheet.cell(row, 5).value)
			store_smart_number = self._getStringValue(xl_sheet.cell(row, 6).value)
			store_globe_number = self._getStringValue(xl_sheet.cell(row, 7).value)
			store_landline = self._getStringValue(xl_sheet.cell(row, 8).value)
			store_status_note = xl_sheet.cell(row, 9).value
			store_cone_1 = int(xl_sheet.cell(row, 10) and xl_sheet.cell(row, 10).value or 0)
			store_cone_2 = int(xl_sheet.cell(row, 11) and xl_sheet.cell(row, 11).value or 0)
			store_cone_3 = int(xl_sheet.cell(row, 12) and xl_sheet.cell(row, 12).value or 0)

			store_cone_4 = int(xl_sheet.cell(row, 13) and xl_sheet.cell(row, 13).value or 0)
			store_cone_5 = int(xl_sheet.cell(row, 14) and xl_sheet.cell(row, 14).value or 0)
			store_cone_6 = int(xl_sheet.cell(row, 15) and xl_sheet.cell(row, 15).value or 0)
			store_cone_7 = int(xl_sheet.cell(row, 16) and xl_sheet.cell(row, 16).value or 0)
			store_cone_8 = int(xl_sheet.cell(row, 17) and xl_sheet.cell(row, 17).value or 0)
			store_cone_9 = int(xl_sheet.cell(row, 18) and xl_sheet.cell(row, 18).value or 0)
			store_cone_10 = int(xl_sheet.cell(row, 19) and xl_sheet.cell(row, 19).value or 0)

			if len(store_number.strip()) == 0:
				raise UserError(_('Row %d has no Store Number. Please add a Store Number to proceed.' % row))
			elif store_number == '0':
				raise UserError(_('Row %d has no Store Number. Please add a Store Number to proceed.' % row))

			#Check 			
			res_partner_obj = self.env['res.partner'].search([('parent_id','=', seven_corporation and seven_corporation.id),
															  ('area_id','=', self.sales_area_id.id),
															  ('store_number','=', str(store_number).strip())])

			partner_id = res_partner_obj and res_partner_obj.id or False
			# If No Records Found
			if not res_partner_obj:
				res = res_partner_obj.create({
					'parent_id': seven_corporation and seven_corporation.id,
					'type': 'delivery',
					'store_number': str(store_number),
					'store_name': store_name,
					'store_manager': store_manager,
					'globe_number': store_globe_number,
					'sun_number': store_sun_number,
					'smart_number': store_smart_number,
					'area_id' : self.sales_area_id.id,
					'name': store_number + ' ' + store_name,
					'street': store_address,
					})
				partner_id = res.id
			else:
				vals = {}
				if len(store_name.strip()) != 0 and str(store_name).strip() != res_partner_obj.store_name:
					vals['store_name'] = store_name

				if len(store_manager.strip()) != 0 and str(store_manager).strip() != res_partner_obj.store_manager:
					vals['store_manager'] = store_manager

				if len(store_globe_number.strip()) != 0 and str(store_globe_number).strip() != res_partner_obj.globe_number:
					vals['globe_number'] = store_globe_number

				if len(store_sun_number.strip()) != 0 and str(store_sun_number).strip() != res_partner_obj.sun_number:
					vals['sun_number'] = store_sun_number

				if len(store_smart_number.strip()) != 0 and str(store_smart_number).strip() != res_partner_obj.smart_number:
					vals['smart_number'] = store_smart_number

				if len(store_address.strip()) != 0 and str(store_address).strip() != res_partner_obj.street:
					vals['street'] = store_address


				vals['name'] = store_number + ' ' + store_name

				res_partner_obj.write(vals)
			
			seven_call_sheet_line_obj.create({
				'call_sheet_id': self.id,
				'partner_id': partner_id,
				'legacy_invoice_number': legacy_invoice_number,
				'cone_1':store_cone_1,
				'cone_2':store_cone_2,
				'cone_3':store_cone_3,
				'cone_4':store_cone_4,
				'cone_5':store_cone_5,
				'cone_6':store_cone_6,
				'cone_7':store_cone_7,
				'cone_8':store_cone_8,
				'cone_9':store_cone_9,
				'cone_10':store_cone_10,
				})
		return True

class CallSheetLine(models.Model):
	_name = 'seven_call_sheet.call_sheet_line'

	partner_id = fields.Many2one(
		'res.partner',
		string='Store',
		domain=[('parent_id.name','=','Philippine Seven Corporation'), ]
	)

	store_number = fields.Char(
		string='Store Number',
		compute='_get_info'
	)

	store_name = fields.Char(
		string='Store Name',
		compute='_get_info'
	)

	store_manager = fields.Char(
		string='Store Manager',
		compute='_get_info'
	)

	call_sheet_id = fields.Many2one(
		'seven_call_sheet.call_sheet',
		string='Call Sheet',
	)

	sun_number = fields.Char(
		string='Sun Number',
		compute='_get_info'
	)

	globe_number = fields.Char(
		string='Globe Number',
		compute='_get_info'
	)

	smart_number = fields.Char(
		string='Smart Number',
		compute='_get_info'
	)

	landline_number = fields.Char(
		string='Landline',
		compute='_get_info'
	)

	cone_1 = fields.Integer(
		string='C1',
	)

	cone_2 = fields.Integer(
		string='C2',
	)

	cone_3 = fields.Integer(
		string='C3',
	)

	cone_4 = fields.Integer(
		string='C4',
	)

	cone_5 = fields.Integer(
		string='C5',
	)

	cone_6 = fields.Integer(
		string='C6',
	)

	cone_7 = fields.Integer(
		string='C7',
	)

	cone_8 = fields.Integer(
		string='C8',
	)

	cone_9 = fields.Integer(
		string='C9',
	)

	cone_10 = fields.Integer(
		string='C10',
	)
	total_unit_price = fields.Float(
		string='Total Unit Price',
		compute="_value_amount"
	)

	sales_id = fields.Many2one('sale.order',string="Sales Order")
	invoice_id = fields.Many2one('account.invoice',string="Sales Invoice")
	stock_picking_id = fields.Many2one('stock.picking',string="Delivery")

	store_status_note = fields.Char()

	legacy_invoice_number = fields.Char('Legacy Invoice')

	@api.multi
	def viewPartnerOrder(self):
		self.ensure_one()
		count = self.cone_1 + self.cone_2 + self.cone_3
		if count > 0:
			return True
		return False

	@api.depends('cone_1','cone_2', 'cone_3', 'cone_4','cone_5', 'cone_6', 'cone_7','cone_8', 'cone_9', 'cone_10', 'call_sheet_id.price_box')
	def _value_amount(self):
		for rec in self:
			record_list = {}
			numbers = [1,2,3,4,5,6,7,8,9,10]
			for number in numbers:
				cone = 'cone_' + str(number)
				cone_name = 'cone_' + str(number) + '_id'
				price_box = 'price_box' if number == 1 else 'price_box_' + str(number)

				cone_prod = 'cone_' + str(number) + '_product'
				cone_price = 'cone_' + str(number) + '_price'
				taxes_cone_prod = 'taxes_cone_' + str(number)

				record_list[cone_prod], record_list[cone_price] =  rec.call_sheet_id[cone_name], rec.call_sheet_id[price_box] 

				record_list[taxes_cone_prod] = rec.call_sheet_id[cone_name].taxes_id.compute_all(record_list[cone_price] ,False,
																								 rec[cone],
																								 product=rec.call_sheet_id[cone_name],
																								 partner=rec.partner_id)
				cone_tax = 0.00
				cone_unit_price = 0.00
				cone_total_amount = 0.00

				cone_tax = sum(t.get('amount', 0.0) for t in record_list[taxes_cone_prod].get('taxes', []))
				cone_unit_price = record_list[taxes_cone_prod]['total_excluded']
				cone_total_amount = sum(t.get('amount', 0.0) for t in record_list[taxes_cone_prod].get('taxes', [])) + record_list[taxes_cone_prod]['total_excluded']

				#Summary
				rec.total_amount += cone_total_amount
				rec.tax += cone_tax
				rec.total_unit_price += cone_unit_price


	@api.depends('partner_id')
	def _get_info(self):
		for rec in self:
			rec.store_number = rec.partner_id.store_number
			rec.store_name = rec.partner_id.store_name
			rec.store_manager = rec.partner_id.store_manager
			rec.sun_number = rec.partner_id.sun_number
			rec.globe_number = rec.partner_id.globe_number
			rec.smart_number = rec.partner_id.smart_number
			rec.landline_number = rec.partner_id.landline_number

	@api.onchange('partner_id')
	def _get_store_status_note(self):
		for rec in self:
			rec.store_status_note = rec.partner_id.store_status_note

	tax = fields.Float(
		string='VAT',
		compute="_value_amount"
	)

	total_amount = fields.Float(
		string='Amount',
		compute="_value_amount"
	)



class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	@api.multi
	def action_invoice_open(self):
		res = super(AccountInvoice, self).action_invoice_open()
		if res:
			for invoice in self:
				if invoice.legacy_invoice:
					if len(invoice.legacy_invoice) > 0:
						invoice.write({'number': invoice.legacy_invoice.zfill(5)})
						account_move = self.env['account.move'].search([('id', '=', invoice.move_id.id)])
						if account_move:
							account_move.write({'name': invoice.legacy_invoice.zfill(5)})
		return res

	@api.multi
	def write(self, vals):
		#_logger.info(vals)
		if 'legacy_invoice' in vals:
			#Check if Legacvy Invoice Exists
			account_invoice = self.env['account.invoice'].search([('legacy_invoice', '=', vals['legacy_invoice'])])
			if account_invoice:
				raise UserError(_('Legacy Invoice Number %s already exists. Please Change the Invoice Number.' % vals['legacy_invoice']))
			account_move = self.env['account.move'].search([('id', '=', self.move_id.id)])
			if account_move:
				account_move.write({'name': vals['legacy_invoice'].zfill(5)})
		res = super(AccountInvoice, self).write(vals)
		return res