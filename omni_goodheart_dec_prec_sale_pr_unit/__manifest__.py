# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sale Order Line Price Unit Decimal Precision',
    'version' : '1.1',
    'summary': 'Sale Order Line Price Unit Decimal Precision',
    'sequence': 30,
    'author': "OmniTechnical",
    'website': "https://www.omnitechnical.com/",
    'description': """    
        Sale Order Line Price Unit Decimal Precision changing to 3 Digits
    """,
    'category': 'Addons',
    'depends' : ['sale', 'decimal_precision'],
    'data': [
        'data/decimal_accuracy.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
