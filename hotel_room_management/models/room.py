from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


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
    order_id = fields.Many2one('hotel.accommodation')

    # def compute_rent(self):
    #     for record in self:
    #         period_days = relativedelta(self.order_id.checkout,
    #                                     self.order_id.checkin).days
    #     print(period_days)
    #     self.rent = 500 * period_days

    # def _get_number_of_days(self, checkin, checkout):
    #
    #     DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    #     from_dt = datetime.datetime.strptime(checkin, DATETIME_FORMAT)
    #     to_dt = datetime.datetime.strptime(checkout, DATETIME_FORMAT)
    #     timedelta = to_dt - from_dt
    #     diff_day = timedelta.days + float(timedelta.seconds) / 86400
    #     return diff_day
