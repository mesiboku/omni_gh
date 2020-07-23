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
dest_URL = 'http://localhost:8069'
dest_DB = 'GH_LIVE_LATEST_2020-07-07'

dest_USER = 'admin'
dest_PASS = '0mn1gh_2019admin'

# STAGING CONNECTION
dest_common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(dest_URL))
dest_uid = dest_common.authenticate(dest_DB, dest_USER, dest_PASS, {})
dest_models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(dest_URL))



def processFix():
	print("INITIATE FIXED...")
	args = [('state', '=', 'open')]

	get_open_invoices = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'account.invoice', 'search', args)
	total_invoice_open = len(get_open_invoices)
	total_invoice_open_disc = 0

	for invoice in get_open_invoices:
		line_fields = ['id', 'number', 'account_id', 'company_id']
		line_data = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'account.invoice', 'read', invoice, line_fields)

		print(line_data[0]['company_id'][0])
		#if invoice.account_id.company_id.id != invoice.company_id.id:
		#	print(invoice.number)
		#	total_invoice_open_disc +=1

	print('TOTAL OPEN INVOICE: ' + str(total_invoice_open))
	print('TOTAL OPEN INVOICE WITH ACCOUNT COMPANY INFO WITH DISCREPANCY INVOICE COMPANY INFO: ' + str(total_invoice_open_disc))

processFix()



