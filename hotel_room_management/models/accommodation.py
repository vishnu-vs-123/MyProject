from odoo import api, fields, models
import datetime
from datetime import date
# from datetime import datetime
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
    checkin_date = fields.Date()
    checkout_date = fields.Date()
    # current_date = fields.Date(string='current_date', default=datetime.today(),
    #                            readonly=True)

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
    room_det = fields.Integer(related='room.name')

    state = fields.Selection([('draft', 'Draft'), ('check-in', 'Check-In'),
                              ('check-out', 'Check-Out'), ('cancel', 'Cancel')],
                             default='draft', tracking=True)
    expected_days = fields.Integer(string='Expected Days', required=True)
    expected_date = fields.Date(string='Expected Date')
    gust_ids = fields.One2many('hotel.gust', 'accommodation_ids',
                               string='Gust')

    payment_ids = fields.One2many('hotel.payment', 'payment_list_id')
    total = fields.Float(string='Total', compute='_compute_total')

    @api.depends('payment_ids', 'payment_ids.sub_totals')
    def _compute_total(self):
        for record in self:
            total_amt = 0
            for line in record.payment_ids:
                total_amt += line.sub_totals
            record['total'] = total_amt

    # @api.onchange('payment_id')
    # def onchange_gust(self):
    #     for rec in self:
    #         lines = [(5, 0, 0)]
    #         for line in self.payment_id.order_list_ids:
    #             val = {
    #                 'item_names': line.item_name,
    #                 # 'description': self.descriptions,
    #                 # 'quantity': self.quantity_id,
    #                 # 'unit_price': self.price,
    #                 # 'sub_total': self.quantity_id * self.price,
    #                 # 'unit_o_m': self.uom_id.name
    #
    #             }
    #             lines.append((0, 0, val))
    #         rec.payment_det_ids = lines

    # def rent_calculate(self):
    #     rent = self.env['hotel.room'].rent
    #     self.checkin_date = self.checkin.date()
    #     f_date = date(self.checkin_date)
    #     l_date = date(self.current_date)
    #     delta = l_date - f_date
    #     print(delta.days)

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
        order_det = self.env['hotel.order'].search(
            [('room_no_id.name', '=', self.room.name), ('gust_name', '=',
                                                        self.gust_id.name)])
        print(order_det)
        lines = [(5, 0, 0)]
        for line in order_det.order_list_ids:
            val = {
                'item_names': line.item_name,
                'desc': line.description,
                'quantities': line.quantity,
                'unit_prices': line.unit_price,
                'sub_totals': line.sub_total,
                'unit_o_ms': line.unit_o_m

            }
            lines.append((0, 0, val))
            self.payment_ids = lines

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


class HotelPaymentList(models.Model):
    _name = "hotel.payment"
    item_names = fields.Char(string='Name')
    desc = fields.Text(string='description')
    quantities = fields.Float(string='Quantity')
    unit_prices = fields.Float(string='Unit Price')
    sub_totals = fields.Float(string='Subtotal')
    unit_o_ms = fields.Char(string="Uom")
    payment_list_id = fields.Many2one('hotel.accommodation',
                                      string='orders')
