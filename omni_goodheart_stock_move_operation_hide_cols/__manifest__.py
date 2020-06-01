# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Stock Lot Operation Hide Columns',
    'version' : '1.1',
    'summary': 'Hide Columns',
    'sequence': 30,
    'author': "OmniTechnical",
    'website': "https://www.omnitechnical.com/",
    'description': """    
        Hiding Columns in Operations adding of Lot/Serial Number
            * Destination Package
            * Owner
    """,
    'category': 'Addons',
    'depends' : ['stock'],
    'data': [
        'views/stock_move_operations.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
