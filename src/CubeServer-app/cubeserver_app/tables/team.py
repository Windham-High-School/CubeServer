"""Tables for team-related things."""

from typing import List
from flask_table import Table, Col

from cubeserver_common.models.team import Team, TeamLevel, TeamStatus
from cubeserver_app.tables.columns import DropDownEnumCol, EnumCol, OptionsCol

__all__ = ['AdminTeamTable', 'LeaderboardTeamTable']

class AdminTeamTable(Table):
    """Allows a group of Team objects to be displayed in an HTML table"""

    allow_sort = False  # Let's avoid flask-table's built-in sorting
    classes = ["table", "table-striped", "datatable", "display", "bg-dark"]
    thead_classes = ["thead-dark"]
    border = True

    name            = Col('Team Name')
    #_id             = Col('Identifier')
    weight_class    = DropDownEnumCol('Division', TeamLevel,
                                      exclude_option=TeamLevel.PSYCHO_KILLER)
                                      # ^^ (Hide the easter egg) ^^
    status          = DropDownEnumCol('Status', TeamStatus)
    members_str     = Col('Members')  # TODO: Perhaps employ a nested table to list members of a group
    score           = Col('Score')
    secret          = Col('Secret')
    id              = OptionsCol('Options')

    def __init__(self, items: List[Team], **kwargs):
        """Initializes the table"""
        super().__init__(items, **kwargs)

    def sort_url(self, col_id, reverse=False):
        pass
        #return url_for(self._endpoint, sort=col_id,
        #               direction='desc' if reverse else 'asc')

class LeaderboardTeamTable(Table):
    """Allows a group of Team objects to be displayed in an HTML table"""

    allow_sort = False  # Let's avoid flask-table's built-in sorting
    classes = ["table", "table-striped", "datatable", "display", "leaderboardtable"]
    thead_classes = ["thead-dark"]
    border = True

    name            = Col('Team Name')
    #_id             = Col('Identifier')
    members_names_str = Col('Members')
    weight_class    = EnumCol('Division')
    score           = Col('Score')
    status          = EnumCol('Status')

    def __init__(self, items: List[Team], **kwargs):
        """Initializes the table"""
        super().__init__(items, **kwargs)

    def sort_url(self, col_id, reverse=False):
        pass
        #return url_for(self._endpoint, sort=col_id,
        #               direction='desc' if reverse else 'asc')
