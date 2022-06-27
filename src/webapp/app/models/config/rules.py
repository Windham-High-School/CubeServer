"""Models the game rules"""

from model.pymongo_model import SimpleModel

from app import mongo


class Rules(SimpleModel):
    """Defines the exact rules for a game.
    
    There will be a separate Rules object for JV and Varsity teams
    """

    collection = mongo.db.rulesets

    def __init__(self, max_strikes: int, min_points: int, daily_pings: int):
        super().__init__()
        self.max_strikes = max_strikes
        self.min_points = min_points
        self.daily_pings = daily_pings
