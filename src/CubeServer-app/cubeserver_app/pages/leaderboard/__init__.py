
# @bp.route("/stats", defaults={"sel_div": "all"})
# @bp.route("/stats/<sel_div>")
# def leaderboard(sel_div: str = ""):
#     """Renders the leaderboard/stats"""
#     # Figure out which division is selected:
#     selected_division = None
#     if sel_div in [l.value for l in TeamLevel]:
#         selected_division = TeamLevel(sel_div)
#     # Fetch teams from database and populate a table:
#     team_objects = [
#         Team.decode(team)
#         for team in Team.collection.find(
#             {
#                 "status": {
#                     "$nin": [TeamStatus.UNAPPROVED.value, TeamStatus.INTERNAL.value]
#                 }
#             }
#             if selected_division is None
#             else {
#                 "status": {
#                     "$nin": [TeamStatus.UNAPPROVED.value, TeamStatus.INTERNAL.value]
#                 },
#                 "weight_class": selected_division.value,
#             }
#         )
#     ]
#     teams_table = LeaderboardTeamTable(team_objects)
#     # Render the template:
#     return render_template(
#         "leaderboard.html.jinja2",
#         teams_table=teams_table.__html__(),
#         divisions=[TeamLevel.JUNIOR_VARSITY, TeamLevel.VARSITY],
#         selected_division=selected_division,
#     )


# @bp.route("/team/<team_name>")
# def team_info(team_name: str = ""):
#     """A page showing team info & score tally"""
#     # Look-up the team:
#     team = Team.find_by_name(team_name)
#     if team is None:
#         return abort(400)
#     data_table = LeaderboardDataTable(DataPoint.find_by_team(team))
#     return render_template(
#         "team_info.html.jinja2", team=team, table=data_table.__html__()
#     )