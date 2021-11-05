from odoo import api, fields, models


class HotelRoom(models.Model):
    _name = "hotel.room"
    _description = "room details"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Integer(string='Room Number', required=True)
    bed = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('dormitory', 'Dormitory'),

    ], required=True)
    available = fields.Integer(string='Available Beds')
    facility = fields.Many2many('hotel.facility', string='facility',
                                required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True)
    rent = fields.Monetary(string='Rent')

    room_available = fields.Boolean(default=True)
