from odoo import api, fields, models
from datetime import datetime


class HotelOrder(models.Model):
    _name = "hotel.order"

    name = fields.Char(string='Order Reference', required=True, copy=False,
                       readonly=True, default='New')
    room_no_id = fields.Many2one('hotel.room',
                                 domain="[('room_available','=',False)]",
                                 required=True)
    gust_name = fields.Char(string='Guest')
    order_time = fields.Date(string='Order Time',
                             default=datetime.today(), readonly=True)

    category_ids = fields.Many2many('hotel.category', string='Category')
    item_ids = fields.Many2many('hotel.item', 'order_id', string='Item',
                                domain="[('category_ides','=', category_ids)]")

    order_list_ids = fields.One2many('hotel.list', 'list_id',
                                     string='order list')

    total = fields.Float(string='Total', compute='_compute_total')

    @api.model
    def create(self, val):
        if val.get('name', 'New') == 'New':
            val['name'] = self.env['ir.sequence'].next_by_code(
                'hotel.order.sequence') or 'New'
        result = super(HotelOrder, self).create(val)
        return result

    @api.depends('order_list_ids', 'order_list_ids.sub_total')
    def _compute_total(self):
        for record in self:
            total_amt = 0
            for line in record.order_list_ids:
                total_amt += line.sub_total
            record['total'] = total_amt

    @api.onchange('room_no_id')
    def _onchange_room_no_id(self):
        values = self.env['hotel.accommodation'].search(
            [('state', '=', 'check-in'), ('room.name', '=', self.room_no_id.name
                                          )])
        for record in values:
            self.gust_name = record.gust_id.name

    @api.onchange('category_ids')
    def _onchange_category_ids(self):
        val = []
        for category in self.category_ids:
            val.append(category.name)
        self.item_ids = self.env['hotel.item'].search(
            [('category_ides.name', 'in', val)])


class HotelFoodItem(models.Model):
    _name = "hotel.item"
    image = fields.Image(attachment=True)
    name = fields.Char(string='Name', readonly=True)
    category_ides = fields.Many2one('hotel.category', string='Category',
                                    readonly=True)
    price = fields.Float(readonly=True)
    quantity_id = fields.Float(string='Quantity', default=1)
    descriptions = fields.Text(string='Description', readonly=True)
    order_id = fields.Many2one('hotel.order',
                               string='orders')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)

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
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity')
    unit_price = fields.Float(string='Unit Price')
    sub_total = fields.Float(string='Subtotal')
    unit_o_m = fields.Char(string="Uom")
    list_id = fields.Many2one('hotel.order',
                              string='orders')
