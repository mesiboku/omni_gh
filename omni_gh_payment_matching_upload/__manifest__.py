# -*- coding: utf-8 -*-
{
    'name': "Payment Matching Upload",

    'summary': """
        An Uploading Function for Payment""",

    'description': """
        This will function as Payment Matching Automation using spreadsheet.
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    # Created By Samuel Salvador 
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'gh_po_fields'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_payment_upload.xml',
        'views/payment_views.xml',
    ],

    # always loaded
    #'data': [],
}