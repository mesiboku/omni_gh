# -*- coding: utf-8 -*-
{
    'name': "Inventory Dashboard Extension",

    'summary': """
        Inventory Dashboard Extension Filter by Company""",

    'description': """
        Allow to Filter the Inventory Based based on Users Company Logged in
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'views/stock_picking_type_views.xml',
    ],
    # only loaded in demonstration mode
}