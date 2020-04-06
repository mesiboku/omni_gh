# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# if use relativedelta 
from dateutil.relativedelta import relativedelta 
# from dateutil.parser import parser
import time
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
import fnmatch
from odoo.addons import decimal_precision as dp
import pytz
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError

class productionSchedule(models.Model):
	_name = 'omni.gh.production.schedule'

	_description = 'Production Schedule'

	@api.model
	def create(self, vals):
		res = super(productionSchedule, self).create(vals)
		return res


	@api.multi
	def write(self, vals):
		res = super(productionSchedule, self).write(vals)
		return res

	name = fields.Char('Schedule Name', default=lambda x: _('New Production Schedule'))
	start_dt = fields.Datetime(string="Start shift")
	end_dt = fields.Datetime(string='End shift')
	equipments = fields.Many2one('maintenance.equipment', 'Equipment')
	product_id = fields.Many2one('product.product', 'Product')
	description = fields.Char('Description')
	sale_manufacturing = fields.Char('Sale Manufacturing', readonly=True)
	sale_manufacturing_count = fields.Integer('# of MR', readonly=True, compute='_get_mr')



	def _get_mr(self):
		if self:
			if self.sale_manufacturing:
				self.update({
					'sale_manufacturing_count': 1
					})


	@api.multi
	def action_view_manufacturing_request(self):
		action = self.env.ref('omni_gh_sale_manufacturing_request.action_sale_manufacturing').read()[0]
		if self.sale_manufacturing:
			manufacturing_request = self.env['omni.gh.sale.manufacturing']
			data = manufacturing_request.search([('id','=',self.sale_manufacturing)])
			action['views'] = [(self.env.ref('omni_gh_sale_manufacturing_request.view_sale_manufacturing_form').id, 'form')]
			action['res_id'] = data.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		return action


class productionScheduleSummary(models.Model):
	_name = 'omni.gh.production.schedule.summary'


	name = fields.Char('Schedule Name', default=lambda x: _('Production Schedule'), readonly=True)
	start_dt = fields.Date(string="Start shift")
	end_dt = fields.Date(string='End shift')
	date_from = fields.Date('Date From')
	day_of_week = fields.Char()
	date_to = fields.Date('Date To')
	summary_header = fields.Text('Summary Header')
	equipments_summary = fields.Text('Equipments Summary')
	hours = fields.Boolean(default = False)



	@api.model
	def default_get(self, fields):

		hourly_data = []

		if self._context is None:
			self._context = {}

		else:
			hourly_data = self._context['hourly']


		res = super(productionScheduleSummary, self).default_get(fields)
		start_dt = datetime.today()
		dt_start = start_dt.strftime(dt)
		end_dt = start_dt + relativedelta(days=30)
		dt_end = end_dt.strftime(dt)

		if hourly_data == True:
			day = []
			if start_dt.today().weekday() == 0:
				day = 'Monday'
			elif start_dt.today().weekday() == 1:
				day = 'Tuesday'
			elif start_dt.today().weekday() == 2:
				day = 'Wednesday'
			elif start_dt.today().weekday() == 3:
				day = 'Thursday'
			elif start_dt.today().weekday() == 4:
				day = 'Friday'
			elif start_dt.today().weekday() == 5:
				day = 'Saturday'
			elif start_dt.today().weekday() == 6:
				day = 'Sunday'
			else:
				day = 'None'

			res.update({'start_dt': dt_start, 'day_of_week': day, 'end_dt': dt_end, 'hours': hourly_data})

			if not self.start_dt:
				day = []
				if start_dt.today().weekday() == 0:
					day = 'Monday'
				elif start_dt.today().weekday() == 1:
					day = 'Tuesday'
				elif start_dt.today().weekday() == 2:
					day = 'Wednesday'
				elif start_dt.today().weekday() == 3:
					day = 'Thursday'
				elif start_dt.today().weekday() == 4:
					day = 'Friday'
				elif start_dt.today().weekday() == 5:
					day = 'Saturday'
				elif start_dt.today().weekday() == 6:
					day = 'Sunday'
				else:
					day = 'None'

				res.update({'start_dt': dt_start, 'day_of_week': day, 'end_dt': dt_end, 'hours': hourly_data})
		else:
			res.update({'start_dt': dt_start, 'end_dt': dt_end})


			if not self.start_dt and self.end_dt:
				date_today = datetime.datetime.today()
				first_day = datetime.datetime(date_today.year,
											  date_today.month, 1, 0, 0, 0)
				first_temp_day = first_day + relativedelta(months=1)
				last_temp_day = first_temp_day - relativedelta(days=1)
				last_day = datetime.datetime(last_temp_day.year,
											 last_temp_day.month,
											 last_temp_day.day, 23, 59, 59)
				date_froms = first_day.strftime(dt)
				date_ends = last_day.strftime(dt)
				res.update({'start_dt': date_froms, 'end_dt': date_ends, 'hours': hourly_data})
		# raise Warning(res)
		return res


	@api.onchange('start_dt','end_dt')
	def get_production_summary(self):
		res = {}
		all_detail = []
		date_range_list = []
		time_range_list = []
		production_schedule = self.env['omni.gh.production.schedule']
		equipments = self.env['maintenance.equipment']
		summary_header_list = ['Equipments']
		main_header = []


		if self.start_dt or self.end_dt:
			if self._context.get('tz', False):
				timezone = pytz.timezone(self._context.get('tz', False))
			else:
				timezone = pytz.timezone('UTC')

			# d_frm_obj = datetime.strptime(self.start_dt, dt)\
			# 	.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
			# d_to_obj = datetime.strptime(self.end_dt, dt)\
			# 	.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)

			d_frm_obj = datetime.strptime(str(self.start_dt),"%Y-%m-%d")
			d_to_obj = datetime.strptime(str(self.end_dt),"%Y-%m-%d")

			temp_date = d_frm_obj

			if temp_date.weekday() == 0:
				day = 'Monday'
			elif temp_date.weekday() == 1:
				day = 'Tuesday'
			elif temp_date.weekday() == 2:
				day = 'Wednesday'
			elif temp_date.weekday() == 3:
				day = 'Thursday'
			elif temp_date.weekday() == 4:
				day = 'Friday'
			elif temp_date.weekday() == 5:
				day = 'Saturday'
			elif temp_date.weekday() == 6:
				day = 'Sunday'
			else:
				day = 'None'
			self.update({
				'day_of_week': day
				})

			if self.hours == True:
				# start_dt = datetime.strptime(self.start_dt,"%Y-%m-%d %H:%M:%S")
				# start_dt = start_dt.replace(minute=00, hour=00, second=00)
				# self.start_dt = start_dt
				for x in range(25):
					if x != 0:
						val = ''
						# val = str(temp_date.strftime("%H")) + ' ' + (x > 12 and 'PM' or 'AM' )
						val = str(temp_date.strftime("%I")) + ' ' + str(temp_date.strftime("%p")) 

						summary_header_list.append(val)
						time_range_list.append(temp_date.strftime(dt))
						temp_date = temp_date + timedelta(hours=1)
						date_range_list = time_range_list
				all_detail.append(summary_header_list)
				equipment_ids = equipments.search([])
				all_equipments_detail = []

				for x in equipment_ids:
					equipment_details = {}
					equipment_list_stats = []
					equipment_details.update({'name': x.name or ''})
					check_prod_schedule = production_schedule.search([('equipments','in',x.ids)])

					if not check_prod_schedule:

						for y in date_range_list:
							equipment_list_stats.append({
								'state': 3,
								'date': y,
								'equipment_id': x.id
								})
					else:
						# from_dt = datetime.strptime(str(self.start_dt),"%Y-%m-%d %H:%M:%S")
						from_dt = datetime.strptime(str(self.start_dt),"%Y-%m-%d")
						from_dt = from_dt.replace(minute=00, hour=00, second=00)
						to_dt = from_dt.replace(minute=59, hour=23, second=59)
						dt_from = from_dt.strftime(dt)
						dt_to = to_dt.strftime(dt)
						# in_prod_ids = (production_schedule.search([('equipments','in',x.ids),('start_dt', '>=', self.start_dt),('start_dt', '<=', self.start_dt)]))
						# out_prod_ids = (production_schedule.search([('equipments','in',x.ids),('end_dt', '>=', self.end_dt),('end_dt', '<=', self.end_dt)]))
						in_prod_ids = (production_schedule.search([('equipments','in',x.ids),('end_dt', '>=', dt_from)]))
						# out_prod_ids = (production_schedule.search([('equipments','in',x.ids),('end_dt', '<=', dt_to),('end_dt', '>=', dt_to)]))
						is_reserve = 3

						_logger.info(dt_from)
						_logger.info(dt_to)
						_logger.info(in_prod_ids)
						# _logger.info(out_prod_ids)

						for y in date_range_list:
							# y = datetime.strptime(y, dt)
							# ch_dt = y[:10] + ' 23:59:59'
							# ttime = datetime.strptime(ch_dt, dt)
							# c = ttime.replace(tzinfo=timezone).astimezone(pytz.timezone('UTC'))
							# chk_date = c.strftime(dt)
							chk_date = datetime.strptime(y, dt)
							product_name = ''
							if in_prod_ids:

								for resrv in in_prod_ids:

									product_name = resrv.product_id.name
									checkin_date = datetime.strptime(resrv.start_dt, dt)
									checkout_date = datetime.strptime(resrv.end_dt, dt)
									tz_check_in = pytz.utc.localize(checkin_date).astimezone(timezone)
									tz_check_out = pytz.utc.localize(checkout_date).astimezone(timezone)
									chk_date_check_in = tz_check_in.strftime(dt)
									chk_date_check_out = tz_check_out.strftime(dt)
									date_check_in = datetime.strptime(chk_date_check_in, dt)
									date_check_out = datetime.strptime(chk_date_check_out, dt)

									if date_check_out.date() == date_check_in.date() and date_check_in <= chk_date and date_check_out >= chk_date:
										is_reserve = 1
										_logger.info("1")

									elif date_check_out.date() != chk_date.date() and date_check_out.date() > date_check_in.date() and chk_date >= date_check_in and chk_date <= date_check_out:
										is_reserve = 1
										_logger.info("2")
									elif date_check_out.date() == chk_date.date() and date_check_out.date() > date_check_in.date() and chk_date >= date_check_in and date_check_out >= chk_date:
										is_reserve = 1
										_logger.info("3")
									else:
										is_reserve = 3

							# if out_prod_ids:

							# 	for resrv in out_prod_ids:
							# 		product_name = resrv.product_id.name
							# 		checkin_date = datetime.strptime(resrv.start_dt, dt)
							# 		checkout_date = datetime.strptime(resrv.end_dt, dt)
							# 		tz_check_in = pytz.utc.localize(checkin_date).astimezone(timezone)
							# 		tz_check_out = pytz.utc.localize(checkout_date).astimezone(timezone)
							# 		chk_date_check_in = tz_check_in.strftime(dt)
							# 		chk_date_check_out = tz_check_out.strftime(dt)
							# 		date_check_in = datetime.strptime(chk_date_check_in, dt)
							# 		date_check_out = datetime.strptime(chk_date_check_out, dt)

							# 		if date_check_out.date() > date_check_in.date():
							# 			is_reserve = 1

							# _logger.info('IS RESERVED ' + str(is_reserve))
							if is_reserve == 1:
								equipment_list_stats.append({'state': '1',
														'date': '',
														'product': product_name})
							elif is_reserve == 2:
								equipment_list_stats.append({'state': '2',
														'date': '',
														'product': product_name})
							elif is_reserve == 4:
								equipment_list_stats.append({'state': '4',
														'date': '',
														'product': product_name})
							else:
								equipment_list_stats.append({'state': '3',
														'date': '',
														'product': product_name})
					equipment_details.update({'value': equipment_list_stats})
					all_equipments_detail.append(equipment_details)
			else:

				while(temp_date <= d_to_obj):
					val = ''
					val = (str(temp_date.strftime("%a")) + ' ' +
						   str(temp_date.strftime("%b")) + ' ' +
						   str(temp_date.strftime("%d")))
					summary_header_list.append(val)
					date_range_list.append(temp_date.strftime
										   (dt))
					temp_date = temp_date + timedelta(days=1)

				equipment_ids = equipments.search([])


				all_equipments_detail = []
				for x in equipment_ids:
					equipment_details = {}
					equipment_list_stats = []
					equipment_details.update({'name': x.name or ''})
					check_prod_schedule = production_schedule.search([('equipments','in',x.ids)])

					# raise Warning(check_prod_schedule)

					if not check_prod_schedule:

						for y in date_range_list:
							equipment_list_stats.append({
								'state': 3,
								'date': y,
								'equipment_id': x.id
								})
					else:
						# from_dt = datetime.strptime(str(self.start_dt),"%Y-%m-%d %H:%M:%S")
						from_dt = datetime.strptime(str(self.start_dt),"%Y-%m-%d")

						# start_dt = datetime.strftime(self.start_dt, dt)
						# end_dt = datetime.strftime(self.end_dt, dt)
						# dt_from = start_dt.strftime(dt)
						# dt_to = end_dt.strftime(dt)
						# in_prod_ids = (production_schedule.search([('equipments','in',x.ids),('start_dt', '<=', self.start_dt),('end_dt', '>=', self.start_dt)]))
						# out_prod_ids = (production_schedule.search([('equipments','in',x.ids),('end_dt', '<=', self.end_dt),('end_dt', '>=', self.end_dt)]))

						# in_prod_ids = (production_schedule.search([('equipments','in',x.ids),('start_dt', '>=', self.start_dt),('end_dt', '<=', self.end_dt)]))
						in_prod_ids = (production_schedule.search([('equipments','in',x.ids),('end_dt', '>=', self.start_dt)]))
						is_reserve = 3
						get_dt = []

						for y in date_range_list:
							ch_dt = y[:10] + ' 23:59:59'
							ttime = datetime.strptime(ch_dt, dt)
							c = ttime.replace(tzinfo=timezone).astimezone(pytz.timezone('UTC'))
							# chk_date = c.strftime(dt)
							chk_date = datetime.strptime(y, dt)

							_logger.info('CHECK IF INSIDE OF in_prod_ids ' + str(in_prod_ids))
							product_name = ''
							if in_prod_ids:

								for in_x in in_prod_ids:
									product_name = in_x.product_id.name
									checkin_date = datetime.strptime(in_x.start_dt, dt)
									checkout_date = datetime.strptime(in_x.end_dt, dt)
									tz_check_in = pytz.utc.localize(checkin_date).astimezone(timezone)
									tz_check_out = pytz.utc.localize(checkout_date).astimezone(timezone)
									chk_date_check_in = tz_check_in.strftime(dt)
									chk_date_check_out = tz_check_out.strftime(dt)
									date_check_in = datetime.strptime(chk_date_check_in, dt)
									date_check_out = datetime.strptime(chk_date_check_out, dt)

									# if date_check_out.date() == date_check_in.date() and date_check_in <= chk_date and date_check_out >= chk_date:
									# 	is_reserve = 1
									# elif date_check_out.date() > date_check_in.date() and chk_date >= date_check_in:
									# 	is_reserve = 1
									get_dt = str(chk_date_check_in)
									# if chk_date.date() >= date_check_in.date() and chk_date.date() <= date_check_out.date():
									if date_check_in.date() <= chk_date.date() <= date_check_out.date():
										is_reserve = 1
									else:
										is_reserve = 3

							# _logger.info('CHECK IF INSIDE OF out_prod_ids ' + str(out_prod_ids))
							# if out_prod_ids:

							# 	for in_x in out_prod_ids:
							# 		checkin_date = datetime.strptime(in_x.start_dt, dt)
							# 		checkout_date = datetime.strptime(in_x.end_dt, dt)
							# 		tz_check_in = pytz.utc.localize(checkin_date).astimezone(timezone)
							# 		tz_check_out = pytz.utc.localize(checkout_date).astimezone(timezone)
							# 		chk_date_check_in = tz_check_in.strftime(dt)
							# 		chk_date_check_out = tz_check_out.strftime(dt)
							# 		date_check_in = datetime.strptime(chk_date_check_in, dt)
							# 		date_check_out = datetime.strptime(chk_date_check_out, dt)


							# 		if date_check_out.date() > date_check_in.date():
							# 			if chk_date <= date_check_out and chk_date >= from_dt:
							# 				is_reserve = 1
							# 			else:
							# 				is_reserve = 3
							# 		else:
							# 			is_reserve = 3
							
							_logger.info('IS RESERVED ' + str(is_reserve))
							if is_reserve == 1:
								equipment_list_stats.append({'state': '1',
														'date': get_dt,
														'product': product_name})
							elif is_reserve == 2:
								equipment_list_stats.append({'state': '2',
														'date': get_dt,
														'product': product_name})
							elif is_reserve == 4:
								equipment_list_stats.append({'state': '4',
														'date': get_dt,
														'product': product_name})
							else:
								equipment_list_stats.append({'state': '3',
														'date': get_dt,
														'product': product_name})
					equipment_details.update({'value': equipment_list_stats})
					all_equipments_detail.append(equipment_details)
		main_header.append({'header': summary_header_list})
		self.summary_header = str(main_header)
		self.equipments_summary = str(all_equipments_detail)
		return res






