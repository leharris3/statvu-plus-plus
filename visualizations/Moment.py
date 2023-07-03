from visualizations.Ball import Ball
from visualizations.Player import Player


class Moment:
    """A class for keeping info about the moments"""

    def __init__(self, moment):
        self.quarter = moment[0]
        self.game_clock = moment[2]
        self.shot_clock = moment[3]

        ball = moment[5][0]
        players = moment[5][1:]  # Hardcoded position for players in json

        self.ball = Ball(ball)
        self.players = [Player(player) for player in players]
        self.frame_number = moment[6]
