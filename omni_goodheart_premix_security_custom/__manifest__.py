{
    'name': "Good Heart Premix",
    'summary': "Premix Security Modifications",
    'description': """Long description""",
    'author': "OmniTechnical",
    'license': "AGPL-3",
    'website': "http://www.example.com",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'depends': ['base','mrp', 'stock','quality_mrp'],
    'data': [#'views/views.xml',
    'views/Omni_premix_custom.xml',
	'views/production_work_order_form_extend.xml',
	'data/premixdata.xml',
    'data/menu_item_roles.xml',
    'data/custom_menu.xml',
    'views/sales_invoice.xml',
    'views/stock_new_dr_field.xml'],
    # 'demo': ['demo.xml'],
}
