# -*- coding: utf-8 -*-
{
    'name': "Goodheart Cash and Check Voucher",

    'summary': """
        Cash and Check Voucher.""",

    'description': """
        Shoot to print Cash and Check Voucher
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','sale','purchase','account_check_printing'],

    # always loaded
    'data': [
        'reports/check_voucher.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}