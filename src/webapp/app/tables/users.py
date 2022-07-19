"""Tables for team-related things."""

from typing import List
from flask_table import Table, Col

from app.models.team import Team
from app.tables.columns import DropDownEnumCol, OptionsCol
from app.models.user import UserActivation, UserLevel

__all__ = ['AdminUserTable']

class AdminUserTable(Table):
    """Allows a group of Team objects to be displayed in an HTML table"""

    allow_sort = False  # Let's avoid flask-table's built-in sorting
    classes = ["table", "table-striped", "datatable", "display", "bg-dark"]
    thead_classes = ["thead-dark"]
    border = True

    name            = Col('User Name')
    level           = DropDownEnumCol('User Level', UserLevel, model_type='User')
    email           = Col('Email')
    activated       = DropDownEnumCol('Active?', UserActivation, model_type='User')

    id              = OptionsCol('Options', model_type='User')


    def __init__(self, items: List[Team], **kwargs):
        """Initializes the table"""
        super().__init__(items, **kwargs)

    def sort_url(self, col_id, reverse=False):
        pass
        #return url_for(self._endpoint, sort=col_id,
        #               direction='desc' if reverse else 'asc')
