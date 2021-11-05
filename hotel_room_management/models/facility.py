from odoo import api, fields, models


class HotelFacility(models.Model):
    _name = "hotel.facility"

    name = fields.Char(string='facility', required=True)
