# -*- coding: utf-8 -*-
{
    'name': "Goodheart Shoot to Print - Sales Invoice",

    'summary': """
        Adds a custom sales invoice report template.""",

    'description': """
        Adds a custom sales invoice report template.
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_invoicing','purchase','sale_management','quality','web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/report_cl_sales_inv.xml',
        'views/templates.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}