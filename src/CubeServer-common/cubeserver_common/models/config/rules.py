"""Models the game rules

See app.models.team for more information regarding the game aspect"""

from cubeserver_common.models import PyMongoModel
from cubeserver_common.models.team import Team
from cubeserver_common.models.datapoint import DataPoint


class Rules(PyMongoModel):
    """Defines the exact rules for a game.

    There will be a separate Rules object for JV and Varsity teams
    """

    collection = PyMongoModel.mongo.db.get_collection('rules')


    def __init__(
        self,
        max_strikes: int = 10,
        min_points: int = 0,
        daily_pings: int = 0,
        selected: bool = True
    ):
        super().__init__()
        self.max_strikes = max_strikes
        self.min_points = min_points
        self.daily_pings = daily_pings
        self.selected = selected

    def post_data(self, team: Team, datapoint: DataPoint) -> bool:
        """This is executed whenever a team sends in some data
        If this returns true, it sends an OK response to the client"""
        # TODO: Implement rules
        team.health.reward()  # Just give 'em a point for trying.
        team.save()
        # Now log the data:
        datapoint.save()
        return True

    @staticmethod
    def retrieve_instance() -> PyMongoModel:
        """Retrieves the current ruleset"""
        return Rules.find_one({'selected': True})
