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
dest_URL = 'http://203.160.190.162:8069'
dest_DB = 'GH-prodtest'
dest_PASS = '0mn1gh_202007admin'

# TEST
#dest_URL = 'http://localhost:8069'
#dest_DB = 'GH_LIVE_LATEST_2020-07-07'

dest_USER = 'admin'
#dest_PASS = '0mn1gh_2019admin'



# STAGING CONNECTION
dest_common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(dest_URL))
dest_uid = dest_common.authenticate(dest_DB, dest_USER, dest_PASS, {})
dest_models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(dest_URL))



def processFix():
	print("INITIATE FIXED...")
	args = [('state', '=', 'open'),('type','=','out_invoice')]
	str_logs =""

	#get_invoice = dest_models.execute_kw(dest_DB, dest_uid, dest_PASS, 'account.payment.unmatch', 'realignedSalesInvoiceJLEntries',[])

	get_open_invoices = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'account.invoice', 'search', args)
	total_invoice_open = len(get_open_invoices)
	total_invoice_open_disc = 0
	total_invoice_open_not_disc = 0
	int_progress_bar = 0
	print('Total Sales Invoice: ' + str(total_invoice_open))
	str_logs += 'Total Sales Invoice: ' + str(total_invoice_open) + '\n'

	for invoice in get_open_invoices:
		int_progress_bar +=1
		line_fields = ['id', 'number', 'account_id', 'company_id']
		line_data = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'account.invoice', 'read', invoice, line_fields)
		

		acc_acc_args = [('id', '=', line_data[0]['account_id'][0])]
		get_account_account = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'account.account', 'search', acc_acc_args)
		account_line_fields = ['id', 'company_id']
		account_line_data = dest_models.execute(dest_DB, dest_uid, dest_PASS, 'account.account', 'read', get_account_account, account_line_fields)
		invoice_company_id = line_data[0]['company_id'][0]
		account_company_id = account_line_data[0]['company_id'][0]
		invoice_id  = line_data[0]['id']
		if invoice_company_id != account_company_id:
			total_invoice_open_disc +=1
			print(invoice_id)
			print('Invoice Number ' + line_data[0]['number'] + ' Discrepancy Found Total of ' + str(total_invoice_open_disc) + '/' + str(total_invoice_open))
			str_logs += 'Invoice Number ' + line_data[0]['number'] + ' Discrepancy Found\n'

			get_invoice = dest_models.execute_kw(dest_DB, dest_uid, dest_PASS, 'account.payment.unmatch', 'realignedSalesInvoiceJLEntries',[int(invoice_id)])

			print('Invoice Number ' + line_data[0]['number'] + ' Discrepancy STATUS ' + get_invoice)
			str_logs += 'Invoice Number ' + line_data[0]['number'] + 'STATUS + '+ get_invoice +' Discrepancy Foun d\n'
		else:
			total_invoice_open_not_disc +=1
			#print('Invoice Number ' + line_data[0]['number'] + ' IS OK Total of ' + str(total_invoice_open_not_disc) + '/' + str(total_invoice_open))
		print('Invoice Number ' + line_data[0]['number'] + ' CHECK Total of ' + str(int_progress_bar) + '/' + str(total_invoice_open))
		


			

	print('TOTAL OPEN INVOICE: ' + str(total_invoice_open))
	print('TOTAL OPEN OK INVOICE: ' + str(total_invoice_open_not_disc))
	print('TOTAL OPEN INVOICE WITH ACCOUNT COMPANY INFO WITH DISCREPANCY INVOICE COMPANY INFO: ' + str(total_invoice_open_disc))
	print('DONE')

	str_logs += 'TOTAL OPEN INVOICE: ' + str(total_invoice_open) + '\n'
	str_logs += 'TOTAL OPEN OK INVOICE: ' + str(total_invoice_open_not_disc) + '\n'
	str_logs += 'TOTAL OPEN INVOICE WITH ACCOUNT COMPANY INFO WITH DISCREPANCY INVOICE COMPANY INFO: ' + str(total_invoice_open_disc) + '\n'


	#Create a Log File
	if os.path.isdir('/odoo/TemporaryFiles'):
		txt_dir_path = '/odoo/TemporaryFiles'
		FILENAME = txt_dir_path + '/INTERCOMPANY_LOG' + '.log'

		with open(FILENAME, "wb") as f:
			text = str_logs
			f.write(text)
	else:
		print('ERROR')

processFix()



