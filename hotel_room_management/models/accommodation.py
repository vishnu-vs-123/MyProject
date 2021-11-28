from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError


class HotelAccommodation(models.Model):
    _name = "hotel.accommodation"
    _description = "accommodation details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'checkin desc'

    name = fields.Char(string='Order Reference', required=True, copy=False,
                       readonly=True, default='New')
    gust_id = fields.Many2one('res.partner', string='Guest', tracking=True,
                              required=True)

    guest = fields.Integer(string='Number of Guest',
                           states={'check-in': [('readonly', True)],
                                   'check-out': [('readonly', True)]},
                           )
    checkin = fields.Datetime(string='Check-In ', readonly=True,
                              help="CheckIn Date and Time of the gust.",
                              default=lambda self: fields.datetime.now())
    checkout = fields.Datetime(string='Check-Out ', readonly=True,
                               help="CheckOut Date and Time of the gust.")
    checkout_date = fields.Date(string="checkout")
    days_difference = fields.Integer(store=True, default=1)

    bed = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('dormitory', 'Dormitory'),

    ], required=True,
        states={'check-in': [('readonly', True)],
                'check-out': [('readonly', True)]},
        readonly=False,

    )
    available = fields.Integer(string='Available Beds',
                               related='room.available')
    facility = fields.Many2many('hotel.facility', string='Facility',
                                states={'check-in': [('readonly', True)],
                                        'check-out': [('readonly', True)]}
                                )
    room = fields.Many2one('hotel.room', string='Room',
                           required=True,
                           domain="[('room_available', '=', True), "
                                  "('bed_type', '=', bed)]",
                           states={'check-in': [('readonly', True)],
                                   'check-out': [('readonly', True)]},
                           )

    state = fields.Selection([('draft', 'Draft'), ('check-in', 'Check-In'),
                              ('check-out', 'Check-Out'), ('cancel', 'Cancel')],
                             default='draft', tracking=True)
    expected_days = fields.Integer(string='Expected Days', required=True,
                                   states={'check-in': [('readonly', True)],
                                           'check-out': [('readonly', True)]},
                                   default=1)
    expected_date = fields.Date(string='Expected Date',
                                compute='compute_date', store=True)

    gust_ids = fields.One2many('hotel.gust', 'accommodation_ids',
                               string='Gust')

    payment_ids = fields.One2many('hotel.payment', 'payment_list_id')
    total = fields.Float(string='Total', compute='_compute_total')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency')
    room_rent = fields.Monetary(string='rent', related='room.rent')

    @api.onchange('bed')
    def onchange_bed(self):
        self.room = False
        print(self.room_rent)

    @api.depends('payment_ids', 'payment_ids.sub_totals')
    def _compute_total(self):
        for record in self:
            total_amt = 0
            for line in record.payment_ids:
                total_amt += line.sub_totals
            record['total'] = total_amt

    # @api.depends('checkin')
    # def compute_no_of_days(self):
    #     date = fields.Date.to_date(self.checkin)
    #     for record in self:
    #         record.days_difference = relativedelta(fields.Date.context_today
    #                                                (record), date).days
    #     print(self.days_difference)

    @api.model
    def create(self, val):
        count = len(val.get('gust_ids'))
        if val.get('name', 'New') == 'New':
            val['name'] = self.env['ir.sequence'].next_by_code(
                'hotel.accommodation.sequence') or 'New'
        if val.get('guest') != count:
            raise ValidationError("Please provide all guest details")

        result = super(HotelAccommodation, self).create(val)
        return result

    @api.depends('checkin', 'expected_days')
    def compute_date(self):
        for rec in self:
            if rec.checkin:
                rec.expected_date = rec.checkin + timedelta(
                    days=rec.expected_days)
                same_room = self.env['hotel.room'].search(
                    [('name', '=', self.room.id)])

    # @api.depends('room')
    # def _compute_rent(self):
    #     same = self.env['hotel.room'].search([])
    #     for rec in same:
    #         if rec.name == self.room.id:
    #             self.room_rent = rec.rent
    #     print(self.room_rent, rec.rent)

    @api.depends('message_attachment_count')
    def action_check_in(self):
        self.state = 'check-in'
        self.room.room_available = False
        if self.message_attachment_count != self.guest:
            raise ValidationError("Please attach your documents")
        if not self.checkin:
            self.checkin = fields.Date.context_today(self)

    def action_check_out(self):
        self.state = 'check-out'
        self.checkout = fields.Date.context_today(self)
        self.room.room_available = True
        self.checkout_date = self.checkout.date()

        order_details = self.env['hotel.order'].search(
            [('accommodation_id', '=', self.id)])
        lines = [(5, 0, 0)]
        for line in order_details.order_list_ids:
            val = {
                'item_names': line.item_name,
                'desc': line.description,
                'quantities': line.quantity,
                'unit_prices': line.unit_price,
                'sub_totals': line.sub_total,
                'payment_uom_id': line.order_list_uom_id.id
            }
            lines.append((0, 0, val))
            self.payment_ids = lines

        date = fields.Date.to_date(self.checkin)
        for record in self:
            record.days_difference = relativedelta(fields.Date.context_today
                                                   (record), date).days
            if record.days_difference == 0:
                record.days_difference = 1

        room_details = self.env['hotel.room'].search(
            [('name', '=', self.room.name)])
        line_data = []
        for values in room_details:
            val = {

                'desc': values.room_description,
                'quantities': self.days_difference,
                'unit_prices': self.room_rent,
                'sub_totals': self.room_rent * self.days_difference,
                'payment_uom_id': values.room_uom_id.id

            }
            line_data.append((0, 0, val))
            self.payment_ids = line_data
        invoice_lines = []
        for value in self.payment_ids:
            val = {
                'name': value.desc,
                'quantity': value.quantities,
                'product_uom_id': value.payment_uom_id.id,
                'price_unit': value.unit_prices
            }
            invoice_lines.append((0, 0, val))

        rslt = self.env['account.move'].create({
            'partner_id': self.gust_id,
            'move_type': 'out_invoice',
            'l10n_in_gst_treatment': 'consumer',
            'invoice_line_ids': invoice_lines

        })
        rslt.action_post()

    def action_cancel(self):
        self.state = 'cancel'
        self.room.room_available = True


class HotelGust(models.Model):
    _name = "hotel.gust"
    _description = "gust details"
    gust_name = fields.Char(string='Name', required=True)

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
    desc = fields.Text(string='Description')
    quantities = fields.Integer(string='Quantity')
    unit_prices = fields.Float(string='Unit Price')
    sub_totals = fields.Float(string='Subtotal')
    payment_uom_id = fields.Many2one('uom.uom', string="UoM")
    payment_list_id = fields.Many2one('hotel.accommodation',
                                      string='orders')
