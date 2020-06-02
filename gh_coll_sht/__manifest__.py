# -*- coding: utf-8 -*-
{
    'name': "Goodheart Collection Sheet",

    'summary': """
        Adds Collection Sheet Report in Call Sheets.""",

    'description': """
        Adds Collection Sheet Report in Call Sheets.
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_invoicing','purchase','sale_management','quality','web','seven_call_sheet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_coll_sht.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}