from scripts.extraction import *
from scripts.mapping import *
from scripts.post_processing import *
from scripts.pre_processing import *
from scripts.visualizaiton import *
from Video import *

import os


class Game:
    """Class for processing raw game footage."""

    def __init__(self, title: str, network: str) -> None:
        self.video = Video(title==title, network==network)
        
        

    def process(self):
        # Normalize
        
        
        
        # Extract Time
        
        # Post Process Extraction
        
        # Map Timestamps to Statvu File
        
        # Visualize Results
        
        
        

    def normalize(self):
        if (self.isNormalized):
            print("Game", self.game_title, "alread normalized.")
            return
        normalize_video(file_path=self.video_path)
        self.isNormalized = True

    def temporally_ground(self):
        if (self.is_temporally_grounded):
            print("Game", self.game_title, "alread temporally grounded.")
            return
        extract_time(video_path=self.video_path, network=self.network)
        self.is_temporally_grounded = True

    def visualize(self):
        pass

    def move_video_to_processed_videos(self):
        processed_vid_folder_path = "2016.NBA.Raw.Video.Replays/" + self.game_title
        os.makedirs(name=processed_vid_folder_path)
        
