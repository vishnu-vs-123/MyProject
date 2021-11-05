from odoo import api, fields, models
import datetime
from datetime import timedelta
from odoo.exceptions import Warning


class HotelAccommodation(models.Model):
    _name = "hotel.accommodation"
    _description = "accommodation details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'checkin desc'

    name = fields.Char(string='Order Reference', required=True, copy=False,
                       readonly=True, default='New')
    gust_id = fields.Many2one('res.partner', string='gust', tracking=True,
                              required=True)

    guest = fields.Integer(string='Number of guest')
    checkin = fields.Datetime(string='Check-In Date and Time',
                              states={'check-in': [('readonly', True)]})
    checkout = fields.Datetime(string='Check-Out Date and Time', readonly=True)
    checkout_date = fields.Date()

    bed = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('dormitory', 'Dormitory'),

    ], required=True)
    available = fields.Integer(string='Available Beds', default='10')
    facility = fields.Many2many('hotel.facility', string='facility')
    room = fields.Many2one('hotel.room', string='Room',
                           domain="[('room_available','=',True)]",
                           required=True)

    state = fields.Selection([('draft', 'Draft'), ('check-in', 'Check-In'),
                              ('check-out', 'Check-Out'), ('cancel', 'Cancel')],
                             default='draft', tracking=True)
    expected_days = fields.Integer(string='Expected Days', required=True)
    expected_date = fields.Date(string='Expected Date')
    gust_ids = fields.One2many('hotel.gust', 'accommodation_ids',
                               string='Gust')

    @api.model
    def create(self, val):
        if val.get('name', 'New') == 'New':
            val['name'] = self.env['ir.sequence'].next_by_code(
                'hotel.accommodation.sequence') or 'New'

        result = super(HotelAccommodation, self).create(val)
        return result

    @api.depends(' message_attachment_count')
    def action_check_in(self):
        self.state = 'check-in'
        self.checkin = datetime.datetime.today()
        self.room.room_available = False
        if self.message_attachment_count == 0:
            raise Warning("please add Address proof")
        count = len(self.gust_ids)
        if self.guest != count:
            raise Warning("guest must be same")

    def action_check_out(self):
        self.state = 'check-out'
        self.checkout = datetime.datetime.today()
        self.room.room_available = True
        self.checkout_date = self.checkout.date()

    def action_cancel(self):
        self.state = 'cancel'
        self.room.room_available = True

    @api.onchange('expected_days')
    def onchange_next_date(self):
        if self.checkin:
            self.expected_date = self.checkin + timedelta(
                days=self.expected_days)

    # def compute_expected_date(self):
    #     self.expected_date = self.checkin + timedelta(
    #         days=self.expected_days)


class HotelGust(models.Model):
    _name = "hotel.gust"
    _description = "gust details"
    gust_name = fields.Many2one('res.partner', string='Name', required=True)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),

    ], required=True)
    gust_age = fields.Integer(string='Age', required=True)
    accommodation_ids = fields.Many2one('hotel.accommodation',
                                        string='Accommodation')
