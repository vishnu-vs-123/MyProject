# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Hotel Management',
    'version': '14.0.1.0.0',
    'summary': 'Hotel Room Management software',
    'sequence': 10,
    'description': """Hotel Room Management """,
    'category': '',
    'website': 'https://www.odoo.com/page/billing',
    'depends': ['base', 'mail', 'sale'],
    'data': ['security/ir.model.access.csv',
             'views/room.xml', 'views/sequence.xml', 'views/order_food.xml',
             'security/security.xml', 'views/sale_order.xml'],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
