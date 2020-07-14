#!/usr/bin/python

import sys, os
import base64

# import xmlrpc
import xmlrpclib

from datetime import datetime
import time

import pandas as pd

# from random import randint

# ODOO SERVER CONNECTION
# PROD
# dest_URL = 'http://203.160.190.162:8069'
# dest_DB = 'GH-prodtest'

# TEST
dest_URL = 'http://203.160.190.162:8069'
dest_DB = 'GH-prodtest'

dest_USER = 'admin'
dest_PASS = '0mn1gh_2019admin'

# STAGING CONNECTION
dest_common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(dest_URL))
dest_uid = dest_common.authenticate(dest_DB, dest_USER, dest_PASS, {})
dest_models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(dest_URL))

# SUBMIT ALL PENDING CALLSHEET
def process_callsheet():
	print("CALLSHEET SUBMIT ON GOING...")
	start = time.time()

	count = 0
	# count_update = 0

	args = [('state', '=', 'pending')]
	# args = [('name', '=', 'CS00132')]
	get_pending_callsheet = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet', 'search', args)

	if get_pending_callsheet:
		for callsheet in get_pending_callsheet:
			print callsheet

			callsheet_fields = ['id', 'name', 'call_sheet_line_ids', 'sale_ids']
			callsheet_data = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet', 'read', callsheet, callsheet_fields)

			callsheet_id = callsheet_data[0]['id']
			callsheet_name = callsheet_data[0]['name']
			callsheet_lines = callsheet_data[0]['call_sheet_line_ids']
			callsheet_sale_ids = callsheet_data[0]['sale_ids']

			print "PROCESSING CALLSHEET: " + str(callsheet_name)

			# CREATE SALES ORDER
			# if not callsheet_sale_ids:
			# 	calesheet_create_salesorder = dest_models.execute_kw(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet', 'create_salesorder', callsheet)
			# 	if calesheet_create_salesorder:
			# 		print "CREATED SALES ORDER: " + (calesheet_create_salesorder)

			if callsheet_lines:

				# CREATE SALES ORDER
				count_update = 0
				for line in callsheet_lines:
					line_fields = ['id', 'store_name', 'sales_id']
					line_data = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet_line', 'read', line, line_fields)
					
					if line_data:
						line_sales_id = line_data[0]['sales_id']
						line_store_name = line_data[0]['store_name']

						if not line_sales_id:
							calesheet_create_salesorder = dest_models.execute_kw(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet_line', 'create_salesorder', [line])
							if calesheet_create_salesorder:
								count_update += 1
								print "[%s] %s - CREATED SALES ORDER FOR STORE: %s" % (str(count_update), str(callsheet_name), str(line_store_name))

				# APPROVE SALES ORDER
				count_update = 0
				for line in callsheet_lines:
					line_fields = ['id', 'store_name', 'sales_id']
					line_data = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet_line', 'read', line, line_fields)
					
					if line_data:
						line_sales_id = line_data[0]['sales_id']
						line_store_name = line_data[0]['store_name']

						if line_sales_id:
							calesheet_approve_salesorder = dest_models.execute_kw(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet_line', 'approve_salesorder', [line])
							if calesheet_approve_salesorder:
								count_update += 1
								print "[%s] %s - APPROVED SALES ORDER FOR STORE: %s" % (str(count_update), str(callsheet_name), str(line_store_name))

				# CHECKED TRANSFER INFO
				count_update = 0
				for line in callsheet_lines:
					line_fields = ['id', 'store_name', 'sales_id']
					line_data = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet_line', 'read', line, line_fields)
					
					if line_data:
						line_sales_id = line_data[0]['sales_id']
						line_store_name = line_data[0]['store_name']

						if line_sales_id:
							calesheet_check_transferinfo = dest_models.execute_kw(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet_line', 'check_transferinfo', [line])
							if calesheet_check_transferinfo:
								count_update += 1
								print "[%s] %s - CHECKED TRANSFER INFO FOR STORE: %s" % (str(count_update), str(callsheet_name), str(line_store_name))

				# GENERATE INVOICE
				count_update = 0
				for line in callsheet_lines:
					line_fields = ['id', 'store_name', 'invoice_id']
					line_data = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet_line', 'read', line, line_fields)
					
					if line_data:
						line_invoice_id = line_data[0]['invoice_id']
						line_store_name = line_data[0]['store_name']

						if not line_invoice_id:
							calesheet_sales_invoice = dest_models.execute_kw(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet_line', 'sales_invoice', [line])
							if calesheet_sales_invoice:
								count_update += 1
								print "[%s] %s - INVOICE GENERATED FOR STORE: %s" % (str(count_update), str(callsheet_name), str(line_store_name))

				# UPDATE CALLSHEET STATUS
				update_status = False
				for line in callsheet_lines:
					line_fields = ['id', 'sales_id', 'invoice_id']
					line_data = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet_line', 'read', line, line_fields)
					
					if line_data:
						line_sales_id = line_data[0]['sales_id']
						line_invoice_id = line_data[0]['invoice_id']

						if line_sales_id:
							update_status = True
						else:
							update_status = False

				print update_status
				if update_status:
					calesheet_update = dest_models.execute_kw(dest_DB, dest_uid, dest_PASS, 'seven_call_sheet.call_sheet', 'write', [callsheet, {
						'state': 'submitted',
					}])
					print calesheet_update
					if calesheet_update:
						print "** SUCCESSFULLY SUBMITTED CALLSHEET: %s" % (str(callsheet_name))

			
process_callsheet()