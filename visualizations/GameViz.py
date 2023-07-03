import pandas as pd
from visualizations.Event import Event
from visualizations.Team import Team
from visualizations.Constant import Constant


class GameViz:
    """A class for keeping info about the games"""

    def __init__(self, path_to_json: str, path_to_video: str, game_title: str):
        self.home_team = None
        self.guest_team = None
        self.event = None
        self.path_to_video = path_to_video
        self.path_to_json = path_to_json
        self.game_title = game_title

    def visualize_event(self, event_index):
        data_frame = pd.read_json(self.path_to_json)
        last_default_index = len(data_frame) - 1
        self.event_index = min(event_index, last_default_index)
        index = self.event_index
        print(Constant.MESSAGE + str(last_default_index))
        event = data_frame['events'][index]
        self.event = Event(event, self.path_to_video,
                           event_index, self.game_title)
        self.home_team = Team(event['home']['teamid'])
        self.guest_team = Team(event['visitor']['teamid'])
        self.event.show()
