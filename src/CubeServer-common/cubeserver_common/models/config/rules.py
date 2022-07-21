"""Models the game rules

See app.models.team for more information regarding the game aspect"""

from cubeserver_common.models import PyMongoModel


class Rules(PyMongoModel):
    """Defines the exact rules for a game.

    There will be a separate Rules object for JV and Varsity teams
    """

    collection = PyMongoModel.mongo.db.get_collection('teams')

    def __init__(self, max_strikes: int, min_points: int, daily_pings: int):
        super().__init__()
        self.max_strikes = max_strikes
        self.min_points = min_points
        self.daily_pings = daily_pings
