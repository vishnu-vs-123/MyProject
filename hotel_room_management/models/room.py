from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class HotelRoom(models.Model):
    _name = "hotel.room"
    _description = "room details"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Room Number', required=True)
    bed_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('dormitory', 'Dormitory'),

    ], required=True)
    available = fields.Integer(string='Available Beds')
    facility = fields.Many2many('hotel.facility', string='Facility',
                                required=True)
    # currency_id = fields.Many2one(
    #     'res.currency',
    #     string='Currency'
    #     )
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.user.company_id.
                                 id, index=1)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.
                                  currency_id.id,
                                  required=True)

    rent = fields.Monetary(string=" Rent", currency_field='currency_id')

    room_available = fields.Boolean(default=True)
    order_id = fields.Many2one('hotel.accommodation')
    room_description = fields.Text(string="description", default='Rent')
    room_uom_id = fields.Many2one('uom.uom', string='Unit of Measure',
                                  store=True)
