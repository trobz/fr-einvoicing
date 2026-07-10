# Copyright 2026 Trobz (https://www.trobz.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)

# All the fields below are "store=True, compute=..." (or related+store) fields
# whose value depends on data that only exists once the eInvoicing workflow
# has actually run at least once: fr.directory.line / fr.einvoicing.flow /
# fr.einvoicing.event records, or a partner directory sync via the annuaire
# API. None of that exists right after installing the module, so the "real"
# computed value for any pre-existing account.move/res.partner record is
# NULL/False anyway - same as leaving the column empty.
#
# On a database with a large account_move/res_partner table, letting Odoo's
# _auto_init() compute (and, for tracked fields like fr_directory_line_id,
# prepare mail.thread tracking for) these fields on every existing record
# during install loads the whole recordset into the registry cache at once
# and can exhaust the worker's memory (MemoryError), aborting the install.
#
# Pre-creating the columns here (empty) makes Odoo skip that mass
# computation: Field.update_db() only schedules a field for recomputation
# when its column does not exist yet in the database.
_ACCOUNT_MOVE_COLUMNS = [
    ("fr_directory_line_id", "int4"),
    ("fr_directory_line_identifier", "varchar"),
    ("company_fr_directory_line_id", "int4"),
    ("fr_einvoicing_flow_state", "varchar"),
    ("fr_einvoicing_flow_submitted_at", "timestamp"),
    ("fr_einvoicing_last_event_id", "int4"),
    ("fr_einvoicing_last_event_decoration", "varchar"),
    ("fr_einvoicing_show_readable_invoice_button", "bool"),
    ("fr_einvoicing_required", "bool"),
]

_RES_PARTNER_COLUMNS = [
    ("fr_directory_name", "varchar"),
    ("fr_directory_entity_type", "varchar"),
    ("fr_directory_closed", "bool"),
    ("fr_directory_last_sync_date", "date"),
]


def _create_missing_columns(cr, table, columns):
    for name, column_type in columns:
        if not column_exists(cr, table, name):
            create_column(cr, table, name, column_type)
            _logger.info(
                "Created empty column %s.%s to skip its mass computation on install",
                table,
                name,
            )


def pre_init_hook(env):
    """Pre-create the stored compute columns added by this module on
    account.move and res.partner, so that installing it on a database with a
    lot of existing invoices/partners doesn't trigger an expensive (and
    potentially memory-exhausting) recomputation of these fields for every
    existing record. See the comment above for why this is safe."""
    _create_missing_columns(env.cr, "account_move", _ACCOUNT_MOVE_COLUMNS)
    _create_missing_columns(env.cr, "res_partner", _RES_PARTNER_COLUMNS)
