from visualizations.Constant import Constant
from visualizations.Moment import Moment
from visualizations.Team import Team
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Circle, Rectangle, Arc
import cv2
import numpy as np
import imageio
from moviepy.editor import *
import os
import subprocess
from pathlib import Path
import moviepy


class Event:
    """A class for handling and showing events"""

    def __init__(self, event, video_path, event_index, game_title):
        moments = event['moments']
        self.moments = [Moment(moment) for moment in moments]
        home_players = event['home']['players']
        guest_players = event['visitor']['players']
        players = home_players + guest_players
        player_ids = [player['playerid'] for player in players]
        player_names = [" ".join([player['firstname'],
                                  player['lastname']]) for player in players]
        player_jerseys = [player['jersey'] for player in players]
        values = list(zip(player_names, player_jerseys))
        # Example: 101108: ['Chris Paul', '3']
        self.player_ids_dict = dict(zip(player_ids, values))

        self.video_path = video_path
        self.event_index = event_index
        self.game_title = game_title

    def combine_videos_side_by_side(self, video1_path, video2_path, output_path):
        output_path = f"visualizations/examples/{self.game_title}.{self.event_index}.mp4"
        video1 = VideoFileClip(video1_path)
        video2 = VideoFileClip(video2_path)
        video2 = video2.resize(height=720)
        combined_video = clips_array([[video1, video2]])
        combined_video.write_videofile(
            output_path, codec="libx264", fps=25)

    def save_frames_as_video(self, frames, output_path, fps=25):
        height, width, _ = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()
        print(f"Video saved successfully at: {output_path}")

    def display_frame_from_video(self, frame_number):
        video = cv2.VideoCapture(self.video_path)
        if not video.isOpened():
            print(f"Video at {self.video_path} could not be opened.")
            return
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        if int(frame_number) >= frame_count:
            print(f"Frame {frame_number} out of range.")
            return
        video.set(cv2.CAP_PROP_POS_FRAMES, int(frame_number))
        ret, frame = video.read()
        if not ret:
            print(f"Null ret for frame {frame_number}.")
            return
        # cv2.imshow("Frame", frame)
        return frame

    def update_radius(self, i, player_circles, ball_circle, annotations, clock_info, video_frames):
        # print(f"Updating radius of {i}.")
        moment = self.moments[i]

        # Display corrosponding frame number.
        frame_number = moment.frame_number
        if (frame_number != -1):
            video_frames.append(self.display_frame_from_video(
                frame_number=frame_number))

        for j, circle in enumerate(player_circles):
            if not moment.shot_clock:
                moment.shot_clock = 0.0
            circle.center = moment.players[j].x, moment.players[j].y
            annotations[j].set_position(circle.center)
            clock_test = 'Quarter {:d}\n {:02d}:{:02d}\n {:03.1f}'.format(
                moment.quarter,
                int(moment.game_clock) % 3600 // 60,
                int(moment.game_clock) % 60,
                moment.shot_clock)
            clock_info.set_text(clock_test)
            ball_circle.center = moment.ball.x, moment.ball.y
            ball_circle.radius = moment.ball.radius / Constant.NORMALIZATION_COEF

        # print("Update radius finished for {i}.")
        return player_circles, ball_circle

    def show(self):
        # Leave some space for inbound passes
        ax = plt.axes(xlim=(Constant.X_MIN,
                            Constant.X_MAX),
                      ylim=(Constant.Y_MIN,
                            Constant.Y_MAX))
        ax.axis('off')
        fig = plt.gcf()
        ax.grid(False)  # Remove grid
        start_moment = self.moments[0]
        player_dict = self.player_ids_dict

        clock_info = ax.annotate('', xy=[Constant.X_CENTER, Constant.Y_CENTER],
                                 color='black', horizontalalignment='center',
                                 verticalalignment='center')

        annotations = [ax.annotate(self.player_ids_dict[player.id][1], xy=[0, 0], color='w',
                                   horizontalalignment='center',
                                   verticalalignment='center', fontweight='bold')
                       for player in start_moment.players]

        # Prepare table
        sorted_players = sorted(start_moment.players,
                                key=lambda player: player.team.id)

        home_player = sorted_players[0]
        guest_player = sorted_players[5]
        column_labels = tuple([home_player.team.name, guest_player.team.name])
        column_colours = tuple(
            [home_player.team.color, guest_player.team.color])
        cell_colours = [column_colours for _ in range(5)]

        home_players = [' #'.join(
            [player_dict[player.id][0], player_dict[player.id][1]]) for player in sorted_players[:5]]
        guest_players = [' #'.join(
            [player_dict[player.id][0], player_dict[player.id][1]]) for player in sorted_players[5:]]
        players_data = list(zip(home_players, guest_players))

        table = plt.table(cellText=players_data,
                          colLabels=column_labels,
                          colColours=column_colours,
                          colWidths=[Constant.COL_WIDTH, Constant.COL_WIDTH],
                          loc='bottom',
                          cellColours=cell_colours,
                          fontsize=Constant.FONTSIZE,
                          cellLoc='center')
        table.scale(1, Constant.SCALE)
        # print(table.properties().keys())
        table_cells = table.properties()['children']
        for cell in table_cells:
            cell._text.set_color('white')

        player_circles = [plt.Circle((0, 0), Constant.PLAYER_CIRCLE_SIZE, color=player.color)
                          for player in start_moment.players]
        ball_circle = plt.Circle((0, 0), Constant.PLAYER_CIRCLE_SIZE,
                                 color=start_moment.ball.color)
        for circle in player_circles:
            ax.add_patch(circle)
        ax.add_patch(ball_circle)

        video_frames = []
        anim = animation.FuncAnimation(
            fig, self.update_radius,
            fargs=(player_circles, ball_circle,
                   annotations, clock_info, video_frames),
            frames=len(self.moments), interval=Constant.INTERVAL,
            repeat=False)
        court = plt.imread("visualizations\court.png")
        plt.imshow(court, zorder=0, extent=[Constant.X_MIN, Constant.X_MAX - Constant.DIFF,
                                            Constant.Y_MAX, Constant.Y_MIN])

        anim.save(filename="anim.mp4", fps=25)
        plt.close()

        self.save_frames_as_video(
            frames=video_frames, output_path="frames.mp4")
        self.combine_videos_side_by_side(
            video1_path="frames.mp4", video2_path="anim.mp4", output_path=f"visualizations/viz.mp4")
        os.remove(path="anim.mp4")
        os.remove("frames.mp4")
