from odoo import api, fields, models


class HotelFacility(models.Model):
    _name = "hotel.category"

    name = fields.Char(string='category', required=True)
