"""Tables for team-related things."""

from typing import List
from flask_table import Table, Col

from cubeserver_common.models.beaconmessage import BeaconMessage
from cubeserver_app.tables.columns import EnumCol, PreCol, DateTimeCol

__all__ = ['BeaconMessageTable']

class BeaconMessageTable(Table):
    """Allows a group of BeaconMessage objects to be displayed in an HTML table"""

    allow_sort = False  # Let's avoid flask-table's built-in sorting
    classes = ["table", "table-striped", "datatable", "display", "bg-dark", "beacontable"]
    thead_classes = ["thead-dark"]
    border = True

    send_at             = DateTimeCol('Scheduled Time')
    str_status          = Col('Status')
    division            = EnumCol('Division')
    destination         = EnumCol('Output')
    intensity           = Col('Intensity')

    full_message_bytes_p= PreCol('Full Message')

    message_encoding    = EnumCol('Encoding')

    additional_headers  = Col('Additional Headers')

    checksum            = Col('Checksum')

    misfire_grace       = Col('Misfire Grace Time')

    def __init__(self, items: List[BeaconMessage], **kwargs):
        """Initializes the table"""
        super().__init__(items, **kwargs)

    def sort_url(self, col_id, reverse=False):
        pass
        #return url_for(self._endpoint, sort=col_id,
        #               direction='desc' if reverse else 'asc')
