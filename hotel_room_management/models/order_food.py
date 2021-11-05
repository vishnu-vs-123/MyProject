from odoo import api, fields, models
from datetime import datetime


class HotelOrder(models.Model):
    _name = "hotel.order"

    room_id = fields.Many2one('hotel.room',
                              domain="[('room_available','=',False)]",
                              required=True)
    # nam = fields.Integer(related='room_id.name')
    gust = fields.Char(string='gust')
    order_time = fields.Date(string='order time',
                             default=datetime.today(), readonly=True)

    category_ide = fields.Many2many('hotel.category', string='Category')
    item_ide = fields.Many2many('hotel.item', 'order_ide', string='Item',
                                domain="[('category_ides','=', category_ide)]")
    order_list_ide = fields.One2many('hotel.list', 'list_ide',
                                     string='order list')

    # @api.onchange('room_id')
    # def automatic_gust(self):
    #     get_gust = self.env['hotel.accommodation'].search(
    #         [('room', '=', self.room_id)])
    #     if get_gust:
    #         self.gust = get_gust.gust_id


class HotelFoodItem(models.Model):
    _name = "hotel.item"

    image = fields.Image(string='Image', attachment=True)
    name = fields.Char(string='Name')
    category_ides = fields.Many2many('hotel.category', string='Category')
    price = fields.Float()
    quantity_id = fields.Integer(string='Quantity')

    order_ide = fields.Many2one('hotel.order',
                                string='orders')

    def action_add_to_list(self):
        print("button is clicked")


class HotelOrderList(models.Model):
    _name = "hotel.list"
    name = fields.Char(string='Name')
    description = fields.Text(string='description')
    quantity = fields.Integer(string='Quantity')
    unit_price = fields.Float(string='Unit Price')
    sub_total = fields.Float(string='Subtotal')
    list_ide = fields.Many2one('hotel.order',
                               string='orders')
