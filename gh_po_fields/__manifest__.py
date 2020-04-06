# -*- coding: utf-8 -*-
{
    'name': "Goodheart Purchases Customization",

    'summary': """
        Adds additional fields and workflows to purchases module.""",

    'description': """
        Adds additional fields and workflows to purchases module.
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','account_invoicing','purchase','sale_management','mrp_plm'],

    # always loaded
    'data': [
        
        'views/views.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}