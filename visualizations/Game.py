import pandas as pd
from Event import Event
from Team import Team
from Constant import Constant


class Game:
    """A class for keeping info about the games"""

    def __init__(self, path_to_json, event_index):
        # self.events = None
        self.home_team = None
        self.guest_team = None
        self.event = None
        self.video_path = None
        self.path_to_json = path_to_json
        self.event_index = event_index

    def read_json(self):
        data_frame = pd.read_json(self.path_to_json)
        last_default_index = len(data_frame) - 1
        self.event_index = min(self.event_index, last_default_index)
        index = self.event_index

        print(Constant.MESSAGE + str(last_default_index))
        event = data_frame['events'][index]
        self.video_path = r"C:\Users\Levi\Desktop\statvu-plus\2016.NBA.Raw.Video.Replays\01.14.2016.LAL.at.GSW\01.14.2016.LAL.at.GSW.mp4"
        self.event = Event(event, self.video_path)
        self.home_team = Team(event['home']['teamid'])
        self.guest_team = Team(event['visitor']['teamid'])

    def start(self):
        self.event.show()
