# -*- coding: utf-8 -*-
{
    'name': "Goodheart Stock Operation",
    
    'summary': """
        Scheduler Script to Fix the Done PO with zero value of some delivery order.""",


    'description': """
        Scheduler Script to Fix the Done PO with zero value of some delivery order
    """,

    'author': "OmniTechnical",

    'website': "https://www.omnitechnical.com",

    'category': 'Product',

    'version': '0.1',

    'depends': ['base',
                'stock',  
                'omni_goodheart_stock_operation'],
    'data': [
        'data/scheduler.xml',
    ],
    'installable': True,
}