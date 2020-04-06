# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Changes Stock Operation',
    'version' : '1.1',
    'summary': 'Changes in Stock Operation and Stock Operation Line',
    'sequence': 30,
    'author': "OmniTechnical",
    'website': "https://www.omnitechnical.com/",
    'description': """    
        * Added Uom Field based on Purchase Order Uom
        * Unhide the Destination Package 
        * Required the Source and Destination Package if Product is in Manufacturing Routes
        * Auto Fill Done Qty when Selecting Source and Destination Package Qty Done = Reserved
    """,
    'category': 'Addons',
    'depends' : ['stock',
                 'purchase', 
                 'omni_goodheart_stock_move_operation_hide_cols',
                 'sale_stock',
                 'stock_account'],
    'data': [
        'views/stock_move.xml',
        'views/stock_move_line.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
