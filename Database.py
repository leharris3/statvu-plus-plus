from Game import *
import os
import shutil


class Database:

    # Format: MM.DD.YYYY.HOM.at.AWY.NET

    def __init__(self) -> None:
        self.path_to_unprocessed_videos = 'unprocessed-videos'

    def process_all_videos(self):
        path = self.path_to_unprocessed_videos
        for file_name in os.listdir(path):
            if os.path.isfile(os.path.join(path, file_name)):
                parts = file_name.split('.')
            title = '.'.join(parts[:-2])
            network = parts[-2]
            game = Game(title=title, network=network)
            if not game.process():
                print("Error processing game:", game.title)
