import click
from datetime import datetime
import logging
from bson.objectid import ObjectId


def register_commands(app):
    from cubeserver_common.models.config.rules import RegularOccurrence, Rules
    from cubeserver_common.models.datapoint import DataPoint, DataClass
    from cubeserver_common.models.team import Team, TeamLevel

    @app.cli.command("more-stuff")
    def more_stuff():
        existing_datapoint = DataPoint.find_one(
            {
                "team_reference": ObjectId("655b83885c957af8e85632d3"),
                "category": "temperature",
                "scoring_key": "2023-11-20 22:57:00->2023-11-20 23:03:00",
            }
        )
        existing_datapoint2 = DataPoint.find_one(
            {
                "team_reference": existing_datapoint.team_reference,
                "category": existing_datapoint.category.value,
                "scoring_key": existing_datapoint.scoring_key,
            }
        )
        print("!!", existing_datapoint)
        if existing_datapoint:
            print("!! XX", existing_datapoint.team_reference)
            print("!!", existing_datapoint.id == existing_datapoint2.id)
            print("!!", existing_datapoint == existing_datapoint2)

    @app.cli.command("test-stuff")
    def test_stuff():
        team = Team.find_by_name("CubeServer-reference-1")

        point = DataPoint(
            team_identifier=team.id,
            category=DataClass.TEMPERATURE,
            value=32,
            is_reference=(team.weight_class == TeamLevel.REFERENCE),
        )

        logging.debug(f"DataPoint object: {point}")
        logging.info("Posting data")
        if Rules.retrieve_instance().post_data(point):
            print("!! SUCCESS", point.scoring_key)

    @app.cli.command("test-window-matching")
    def test_window_matching():
        ro = RegularOccurrence(
            offsets=[0, 360, 720, 1080, 1440, 1800, 2160, 2520, 2880, 3240],
            tolerance=120,
        )
        for i in range(1, 60):
            dt = datetime(
                year=2023,
                month=11,
                day=20,
                hour=21,
                minute=i,
                second=23,
                microsecond=32,
            )

            result = ro.get_match_window(dt)
            if result:
                print("!!", i, "--".join([str(x) for x in result]))
            else:
                print("!!", i, result)
