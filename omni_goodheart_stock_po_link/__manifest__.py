# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Link Picking and Purchase',
    'version' : '1.1',
    'summary': 'Link Picking and Purchase',
    'sequence': 30,
    'author': "OmniTechnical",
    'website': "https://www.omnitechnical.com/",
    'description': """    
        Link Picking and Purchase
    """,
    'category': 'custom',
    'depends' : ['stock', 'purchase'],
    'data': [
        'wizard/link_picking_purchase_view.xml',
        # 'views/stock_move_line.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
