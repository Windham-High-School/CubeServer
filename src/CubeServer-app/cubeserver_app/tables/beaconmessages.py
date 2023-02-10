"""Tables for team-related things."""

from typing import List
from flask_table import Table, Col, DatetimeCol

from cubeserver_common.models.team import Team
from cubeserver_app.tables.columns import EnumCol, PreCol

__all__ = ['BeaconMessageTable']

class BeaconMessageTable(Table):
    """Allows a group of BeaconMessage objects to be displayed in an HTML table"""

    allow_sort = False  # Let's avoid flask-table's built-in sorting
    classes = ["table", "table-striped", "datatable", "display", "bg-dark"]
    thead_classes = ["thead-dark"]
    border = True

    send_at             = DatetimeCol('Scheduled Time')
    past                = Col('Transmitted Yet?')
    division            = EnumCol('Division')
    destination         = EnumCol('Output')
    intensity           = Col('Intensity')

    message             = PreCol('Message')
    message_encoding    = EnumCol('Encoding')

    additional_headers  = Col('Additional Headers')

    prefix      = PreCol('Packet Prefix')
    suffix      = PreCol('Packet Suffix')
    checksum    = Col('Checksum')

    def __init__(self, items: List[Team], **kwargs):
        """Initializes the table"""
        super().__init__(items, **kwargs)

    def sort_url(self, col_id, reverse=False):
        pass
        #return url_for(self._endpoint, sort=col_id,
        #               direction='desc' if reverse else 'asc')
