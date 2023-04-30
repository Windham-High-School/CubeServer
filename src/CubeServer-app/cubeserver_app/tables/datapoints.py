"""Tables for data-related stuff."""

from typing import List
from flask_table import Table, Col

from cubeserver_common.models.datapoint import DataPoint, DataClass
from cubeserver_app.tables.columns import OptionsCol, EnumCol, TextEditCol, FloatCol

__all__ = ['AdminDataTable', 'LeaderboardDataTable']

class AdminDataTable(Table):
    """Allows a group of DataPoint objects to be displayed in an HTML table"""

    allow_sort = False  # Let's avoid flask-table's built-in sorting
    classes = ["table", "table-striped", "datatable", "display", "bg-dark", "datapoints-table"]
    thead_classes = ["thead-dark"]
    border = True

    moment            = Col('Datetime')
    team_str          = Col('Team')
    category          = EnumCol('Category')
    value_with_unit   = Col('Value')
    rawscore          = TextEditCol('Raw Point Value', model_type="DataPoint")
    score             = FloatCol('Score')
    id                = OptionsCol('Options', model_type="DataPoint")

    def __init__(self, items: List[DataPoint], **kwargs):
        """Initializes the table"""
        super().__init__(items, **kwargs)

    def sort_url(self, col_id, reverse=False):
        pass
        #return url_for(self._endpoint, sort=col_id,
        #               direction='desc' if reverse else 'asc')


class LeaderboardDataTable(Table):
    """Allows a group of DataPoint objects to be displayed in an HTML table"""

    allow_sort = False  # Let's avoid flask-table's built-in sorting
    classes = ["table", "table-striped", "datatable", "display", "datapoints-table"]
    thead_classes = ["thead-dark"]
    border = True

    moment            = Col('Datetime')
    category          = EnumCol('Category')
    value_with_unit   = Col('Value')
    rawscore          = Col('Point Value')
    score             = Col('Score')

    def __init__(self, items: List[DataPoint], **kwargs):
        """Initializes the table"""
        super().__init__(items, **kwargs)

    def sort_url(self, col_id, reverse=False):
        pass
        #return url_for(self._endpoint, sort=col_id,
        #               direction='desc' if reverse else 'asc')
