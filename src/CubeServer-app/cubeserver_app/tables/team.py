"""Tables for team-related things."""

from typing import List
from flask_table import Table, Col

from cubeserver_common.models.team import Team, TeamLevel, TeamStatus
from cubeserver_app.tables.columns import CustomLinkCol, DropDownEnumCol, EnumCol, OptionsCol, TeamNameCol, AdminTeamNameCol, ManualScoring, ScoreDeltaCol, TextEditCol

__all__ = ['AdminTeamTable', 'LeaderboardTeamTable']

class AdminTeamTable(Table):
    """Allows a group of Team objects to be displayed in an HTML table"""

    allow_sort = False  # Let's avoid flask-table's built-in sorting
    classes = ["table", "table-striped", "datatable", "display", "bg-dark"]
    thead_classes = ["thead-dark"]
    border = True

    name_secondary  = AdminTeamNameCol('Team Name')
    #_id             = Col('Identifier')
    weight_class    = DropDownEnumCol('Division', TeamLevel,
                                      exclude_option=TeamLevel.PSYCHO_KILLER)
    status          = DropDownEnumCol('Status', TeamStatus)
    members_str     = Col('Members')  # TODO: Perhaps employ a nested table to list members of a group
    score           = Col('Score')
    secret          = Col('Secret')
    id              = OptionsCol('Options')
    id_2            = ManualScoring('Manual Scoring')
    all_verified    = Col('Emails Verified?')

    custom_link     = CustomLinkCol('Secret Link', a_classes="btn btn-info")
    name            = TextEditCol('Edit Name')

    emails_sent     = Col('Daily Emails Sent')
    link_emails     = CustomLinkCol('See Emails Sent', link_text="View Sent Emails", a_classes="btn btn-info")

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

    name            = TeamNameCol('Team Name')
    score           = Col('Score')
    score_delta     = ScoreDeltaCol('Score Delta')

    #_id             = Col('Identifier')
    members_names_str = Col('Members')
    weight_class    = EnumCol('Division')
    status          = EnumCol('Status')

    def __init__(self, items: List[Team], **kwargs):
        """Initializes the table"""
        super().__init__(items, **kwargs)

    def sort_url(self, col_id, reverse=False):
        pass
        #return url_for(self._endpoint, sort=col_id,
        #               direction='desc' if reverse else 'asc')
