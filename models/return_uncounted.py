# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from openerp.exceptions import ValidationError
import datetime
import pytz
from decimal import Decimal

class ReturnUncounted(models.Model):
    _name = 'return.uncounted'
    _inherit = ['mail.thread']

    name = fields.Char(copy=False, string='Referencia')
    purchase_order = fields.Many2one('purchase.order', 'Contrato de compra')
    return_tons = fields.Float('Toneladas a regresar')
    datetime = fields.Datetime('Fecha')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Hecho'),
    ], default='draft')

  
    @api.constrains('return_tons')
    def _have_tons(self):
        tons_uncounted = self.env['truck.reception'].search([('contract_id', '=', self.purchase_order.name), ('state', '=', 'done')])
        calculate_tons = 0
        for tons in tons_uncounted:
            total_tons = tons.raw_kilos - tons.clean_kilos
            calculate_tons += total_tons
        if self.return_tons > calculate_tons:
                raise ValidationError("Estas tratando de regresar más toneldas de las que tiene descontadas.")


    @api.onchange('purchase_order')
    def _onchange_date(self):
        local = pytz.timezone("America/Chihuahua")
        utc = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
        local_hr = local.localize(utc, is_dst=None)
        self.datetime = local_hr

    @api.model
    def create(self, vals):
        vals['state'] = 'done'
        vals['name'] = self.env['ir.sequence'].next_by_code('return.uncounted.code')
        res = super(ReturnUncounted, self).create(vals)
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    return_uncounted_tons = fields.Char(compute="_return_uncounted_tons")

    @api.multi
    def return_uncounted_tree(self):
        tree_res = self.env['ir.model.data'].get_object_reference('return_uncounted', 'return_uncounted_list')
        tree_id = tree_res and tree_res[1] or False
        form_res = self.env['ir.model.data'].get_object_reference('return_uncounted', 'return_uncounted_form_view')
        form_id = form_res and form_res[1] or False

        return{
            'type'          :   'ir.actions.act_window',
            'view_type'     :   'form', #Tampilan pada tabel pop-up
            'view_mode'     :   'tree,form', # Menampilkan bagian yang di pop up, tree = menampilkan tabel tree nya utk product
            'res_model'     :   'return.uncounted', #Menampilkan tabel yang akan di show di pop-up screen
            'target'        :   'new', # Untuk menjadikan tampilan prduct yang dipilih menjadi pop-up table tampilan baru, jika dikosongin maka tidak muncul pop-up namun muncul halaman baru.
            'views'         :   [(tree_id, 'tree'),(form_id, 'form')],
            'domain'        :   [('purchase_order.id','=', self.id)] #Filter id barang yang ditampilkan
            }

    @api.multi
    def _return_uncounted_tons(self):
        tons = 0
        for itr in self.env['return.uncounted'].search([('purchase_order.id','=', self.id)]):
            tons += itr['return_tons']
        tons = tons
        self.return_uncounted_tons = str(round(tons,2)) + 'tn'
