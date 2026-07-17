# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """
    The pre-init-hook will be executed before the module is installed.
    """
    _logger.info("Pre-init-hook of account_invoice_en16931")
    _logger.info("Create column invoice_type_code in table account_move")
    env.cr.execute(
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS invoice_type_code VARCHAR;
    """
    )


def post_init_hook(env):
    """
    The post-init-hook will be executed after the module is installed.
    """
    _logger.info("Post-init-hook of account_invoice_en16931")
    _logger.info("Compute value for column invoice_type_code in table account_move")
    env.cr.execute(
        """
        UPDATE account_move
        SET invoice_type_code = '381'
        WHERE move_type IN ('in_refund', 'out_refund');
    """
    )
    env.cr.execute(
        """
        UPDATE account_move
        SET invoice_type_code = '380'
        WHERE move_type IN (
            'out_invoice', 'out_receipt', 'in_invoice', 'in_receipt'
        );
    """
    )
