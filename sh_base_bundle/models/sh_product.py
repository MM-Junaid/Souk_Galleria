# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api


class ShProductTemplate(models.Model):
    _inherit = 'product.product'

    sh_bundle_product_ids = fields.One2many(
        'sh.product.bundle', 'sh_bundle_id', string="Bundle Line")
    sh_is_bundle = fields.Boolean('Is Bundled ?')
    sh_amount_total = fields.Monetary(
        string='Total', store=True, readonly=True, compute='_amount_all')
    # sh_product_qty = fields.Float()

    @api.depends('sh_bundle_product_ids.sh_price_subtotal', 'sh_bundle_product_ids.sh_qty')
    def _amount_all(self):
        amount_total = 0.0
        for order in self:
            if order.sh_bundle_product_ids:
                for line in order.sh_bundle_product_ids:
                    amount_total += line.sh_price_subtotal
                order.sh_amount_total = amount_total

    def compute_bundle_price(self):
        lst_price = 0.0
        if self.sh_bundle_product_ids:
            for bundle_product in self.sh_bundle_product_ids:
                lst_price += bundle_product.sh_price_subtotal
        self.lst_price = lst_price

    def compute_bundle_cost_price(self):
        standard_price = 0.0
        if self.sh_bundle_product_ids:
            for bundle_product in self.sh_bundle_product_ids:
                standard_price += (bundle_product.sh_cost_price * bundle_product.sh_qty)
        self.standard_price = standard_price


class Product(models.Model):
    _inherit = 'product.product'

    def compute_bundle_price(self):
        lst_price = 0.0
        if self.sh_bundle_product_ids:
            for bundle_product in self.sh_bundle_product_ids:
                lst_price += bundle_product.sh_price_subtotal
        self.lst_price = lst_price

    def compute_bundle_cost_price(self):
        standard_price = 0.0
        if self.sh_bundle_product_ids:
            for bundle_product in self.sh_bundle_product_ids:
                standard_price += (bundle_product.sh_cost_price * bundle_product.sh_qty)
        self.standard_price = standard_price


class ShBundleProduct(models.Model):
    _name = 'sh.product.bundle'
    _description = 'Bundle Products'

    sh_bundle_id = fields.Many2one('product.product', 'Bundle ID')
    sh_product_id = fields.Many2one(
        'product.product', 'Product', required=True)
    sh_qty = fields.Float("Quantity")
    sh_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    sh_price_unit = fields.Float('Unit Price')
    sh_cost_price = fields.Float(related="sh_product_id.standard_price")
    sh_price_subtotal = fields.Float('Sub Total', readonly=True, store=True)

    @api.onchange('sh_product_id')
    def _onchange_sh_product_id(self):
        if self.sh_product_id:
            self.sh_uom = self.sh_product_id.uom_id.id
            self.sh_qty = 1.0
            self.sh_price_unit = self.sh_product_id.list_price

    # @api.onchange('sh_qty')
    # def _onchange_sh_product_id(self):
    #     if self.sh_product_id:
    #         product_rec = self.env['product.product'].browse(self.sh_product_id.id)
    #         for rec in product_rec:
    #             rec.write({
    #                 'sh_product_qty': self.sh_qty
    #             })
    #         self.sh_uom = self.sh_product_id.uom_id.id

    @api.onchange('sh_qty', 'sh_price_unit')
    def get_price_subtotal(self):
        for rec in self:
            rec.sh_price_subtotal = rec.sh_price_unit * rec.sh_qty


class ShSaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(ShSaleOrderInherit, self).action_confirm()
        context = self._context.copy()
        hhhh = self.with_context(context)
        product_line_list = []
        delivery_line_list = []

        delivery_id = self.picking_ids
        ggg = delivery_id.move_ids_without_package
        delivery_record = self.env['stock.picking'].browse(delivery_id.id)

        order_line_product_ids = self.order_line
        for line_ids in order_line_product_ids:
            line_quantity = line_ids.product_uom_qty
            sale_order_line_product = self.env['product.product'].browse(line_ids.product_id.id)
            for sh_rec in sale_order_line_product:
                if sale_order_line_product.sh_is_bundle:
                    for b_line in sh_rec.sh_bundle_product_ids:
                        single_product = b_line.sh_product_id
                        # b_line_product = self.env['product.product'].browse(b_line.product_id.id)
                        for b_rec in single_product:
                            product_line_list.append(
                                {'id': b_rec.id, 'name': b_rec.name, 'sh_qty': b_line.sh_qty * line_ids.product_uom_qty}
                            )

        for record in delivery_id:
            for vals in product_line_list:
                delivery_order = record.write({
                    'move_ids_without_package':
                        [
                            (0, 0, {
                                'name': vals['name'],
                                'location_id': 8,
                                'location_dest_id': 5,
                                'product_id': vals['id'],
                                'product_uom': 1,
                                'product_uom_qty': vals['sh_qty'],
                            }),
                        ],
                })

            # movetest._action_confirm()
            # movetest._action_assign()
            # self.assertEqual(movetest.state, 'assigned')

        return res
