"""Tables for team-related things."""

from typing import List
from flask_table import Table, Col

from cubeserver_common.models.mail import Message
from cubeserver_app.tables.columns import PreCol

__all__ = ["AdminEmailTable"]


class AdminEmailTable(Table):
    """Allows a group of Message objects to be displayed in an HTML table"""

    allow_sort = False  # Let's avoid flask-table's built-in sorting
    classes = ["table", "table-striped", "datatable", "display", "bg-dark"]
    thead_classes = ["thead-dark"]
    border = True

    sent_at = Col("Time")
    sender_str = Col("From")
    recipients = Col("Recipient(s)")
    subject = Col("Subject")
    message = PreCol("Message")

    def sort_url(self, col_id, reverse=False):
        pass
