"""Tables for team-related things."""

from typing import List
from flask_table import Table, Col

from cubeserver_app.tables.columns import DropDownEnumCol, OptionsCol, TextEditCol
from cubeserver_common.models.team import Team
from cubeserver_common.models.user import UserActivation, UserLevel

__all__ = ["AdminUserTable"]


class AdminUserTable(Table):
    """Allows a group of Team objects to be displayed in an HTML table"""

    allow_sort = False  # Let's avoid flask-table's built-in sorting
    classes = ["table", "table-striped", "datatable", "display", "bg-dark"]
    thead_classes = ["thead-dark"]
    border = True

    name = TextEditCol("User Name", model_type="User")
    level = DropDownEnumCol("User Level", UserLevel, model_type="User")
    email = TextEditCol("Email", model_type="User")
    activated = DropDownEnumCol("Active?", UserActivation, model_type="User")
    verified = Col("Email verified?")

    id = OptionsCol("Options", model_type="User")

    def __init__(self, items: List[Team], **kwargs):
        """Initializes the table"""
        super().__init__(items, **kwargs)

    def sort_url(self, col_id, reverse=False):
        pass
        # return url_for(self._endpoint, sort=col_id,
        #               direction='desc' if reverse else 'asc')
