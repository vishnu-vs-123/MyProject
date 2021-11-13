from odoo import api, fields, models
from datetime import datetime


class HotelOrder(models.Model):
    _name = "hotel.order"

    room_no_id = fields.Many2one('hotel.room',
                                 domain="[('room_available','=',False)]",
                                 required=True)
    gust_name = fields.Char(string='gust')
    order_time = fields.Date(string='order time',
                             default=datetime.today(), readonly=True)

    category_ids = fields.Many2many('hotel.category', string='Category')
    item_ids = fields.Many2many('hotel.item', 'order_id', string='Item',
                                domain="[('category_ides','=', category_ids)]")

    order_list_ids = fields.One2many('hotel.list', 'list_id',
                                     string='order list')
    # accommodation_det_id = fields.Many2one('hotel.accommodation')

    total = fields.Float(string='Total', compute='_compute_total')

    @api.depends('order_list_ids', 'order_list_ids.sub_total')
    def _compute_total(self):
        for record in self:
            total_amt = 0
            for line in record.order_list_ids:
                total_amt += line.sub_total
            record['total'] = total_amt

    @api.onchange('room_no_id')
    def onchange_automatic_gust(self):
        for record in self:
            same_room = self.env['hotel.accommodation'].search(
                [('room_det', '=', record.room_no_id.name)])
            if same_room:
                record.gust_name = same_room.gust_id.name

    @api.onchange('category_ids')
    def onchange_category_ids(self):
        val = []
        for category in self.category_ids:
            val.append(category.name)
        self.item_ids = self.env['hotel.item'].search(
            [('category_ides.name', 'in', val)])


class HotelFoodItem(models.Model):
    _name = "hotel.item"

    image = fields.Image(attachment=True)
    name = fields.Char(string='Name')
    category_ides = fields.Many2one('hotel.category', string='Category')
    price = fields.Float()
    quantity_id = fields.Float(string='Quantity', default=1)
    descriptions = fields.Text(string='description')
    order_id = fields.Many2one('hotel.order',
                               string='orders')
    uom_id = fields.Many2one('uom.uom', string='uom')

    def action_add_to_list(self):
        lines = []
        order_obj = self.env.context.get('order')
        self.order_id = order_obj
        for line in self.order_id:
            val = {
                'item_name': self.name,
                'description': self.descriptions,
                'quantity': self.quantity_id,
                'unit_price': self.price,
                'sub_total': self.quantity_id * self.price,
                'unit_o_m': self.uom_id.name

            }
            lines.append((0, 0, val))
            self.order_id.order_list_ids = lines


class HotelOrderList(models.Model):
    _name = "hotel.list"
    item_name = fields.Char(string='Name')
    description = fields.Text(string='description')
    quantity = fields.Float(string='Quantity')
    unit_price = fields.Float(string='Unit Price')
    sub_total = fields.Float(string='Subtotal')
    unit_o_m = fields.Char(string="Uom")
    list_id = fields.Many2one('hotel.order',
                              string='orders')
