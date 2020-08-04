# -*- coding: utf-8 -*-
{
    'name': "seven_call_sheet",

    'summary': """
        Seven Eleven Call Sheet for Good Heart""",

    'description': """
        Long description of module's purpose
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup','sales_team','resource','sale','stock','account','product','partner_seven_extension','gh_receiving_advice', 'partner_credit_limit'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir.default.csv',
        'data/gh_sequence.xml',
        'wizard/collection_sheet_wizard.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}