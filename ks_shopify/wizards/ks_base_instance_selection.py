import logging
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class KsShopifyPrepareToExport(models.TransientModel):
    _name = 'ks.shopify.instance.selection'
    _description = 'Select Instance for sync operations'

    ks_instance_ids = fields.Many2many('ks.shopify.connector.instance', string="Instance Ids", required=True,
                                   help=_("Connector Instance reference"),
                                   domain="[('ks_instance_state', '=', 'active')]")

    def ks_execute(self):
        model_name = self.env.context.get("active_model")
        record = self.env[model_name].browse(self.env.context.get("active_ids"))
        to_push = self.env.context.get("push_to_shopify")
        to_pull = self.env.context.get("pull_from_shopify")
        if to_push:
            self.env[model_name].ks_manage_shopify_direct_syncing(record, self.ks_instance_ids, push=to_push)
        if to_pull:
            self.env[model_name].ks_manage_shopify_direct_syncing(record, self.ks_instance_ids, pull=to_pull)

