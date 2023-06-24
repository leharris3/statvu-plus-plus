from scripts.extraction import *
from Video import *
from Data import *

import os
import shutil
import py7zr
from typing import Dict, Any, List, Union

FRAME_WIDTH_OUT = 1280
FRAME_HEIGHT_OUT = 720
FPS_OUT = 25


class Game:
    """Class for processing raw game footage."""

    def __init__(self, title: str, network: str) -> None:
        self.title = title
        self.network = network
        self.video = Video(title=title, network=network)
        self.data = Data(title=title, network=network)
        self.path_to_game_dir = f"statvu-plus-plus/{title}.{network}"

    def process(self):
        # 1. Move + create new folder
        print(f"Creating game folder for game: {self.title}")
        # self.createNewGameFolder()

        # 2. Normalize
        print(f"Normalizing video for game: {self.title}")
        # self.video.normalize()

        # 3. Extract Time
        print(f"Extracting timestamps for game: {self.title}")
        self.extract_time()

        # 4. Post Process Extraction
        print(f"Post-processing results for game: {self.title}.")
        self.data.post_process()

        # 5. Visualize data-mapping. (For Now)
        print("Generating visualization.")
        self.visualize_timestamp_extraction()
        exit()

        # 6. Map Timestamps to Statvu File
        print("Mapping timestamps to statvu data.")
        self.map_timestamps_to_statvu()
        out_path: str = f"{self.path_to_game_dir}/mapped.json"
        os.remove(self.data.path_to_timestamps)
        os.remove(self.data.path_to_processed_data_unzipped)
        os.rename(out_path, self.data.path_to_processed_data_unzipped)

        # 7. Visualize Results
        print("All processing complete.")
        return True

    def createNewGameFolder(self) -> bool:

        # 1. Create new game dir
        new_processed_folder = f"statvu-plus-plus/{self.title}.{self.network}"
        os.mkdir(new_processed_folder)

        # 2. Copy old data to new data path
        old_data_path = self.data.path_to_unprocessed_data
        new_data_path = self.data.path_to_processed_data_zipped
        shutil.copy(old_data_path, new_data_path)

        # 3. Unzip data
        zip_file_path = self.data.path_to_processed_data_zipped
        with py7zr.SevenZipFile(zip_file_path, mode='r') as archive:
            archive.extractall(path=self.path_to_game_dir)
        os.remove(zip_file_path)

        # 4. Move video
        old_video_path = self.video.path_to_unprocessed_video
        new_video_path = self.video.path_to_processed_video
        shutil.copy(old_video_path, new_video_path)

        # 5. Rename .json file
        files = os.listdir(self.path_to_game_dir)
        new_file_name = f"{self.title}.{self.network}.json"
        for file_name in files:
            if file_name.endswith(".json"):
                old_path = os.path.join(
                    self.path_to_game_dir, file_name)
                new_path = os.path.join(
                    self.path_to_game_dir, new_file_name)
                os.rename(old_path, new_path)
                break

        return True

    def extract_time(self) -> bool:
        video_path = self.video.path_to_processed_video
        timestamps = extract_timestamps(
            video_path=video_path, network=self.network)
        with open(f"{self.path_to_game_dir}/timestamps.json", 'w') as f:
            json.dump(timestamps, f)
        return True

    def visualize_timestamp_extraction(self):

        def read_json(file_path):
            with open(file_path) as file:
                return json.load(file)

        def format_time(seconds):
            minutes = int(seconds // 60)
            seconds = seconds % 60
            return f"{minutes:02d}:{seconds:02f}"

        json_path = self.data.path_to_timestamps
        output_path = self.path_to_game_dir + '/timestamps_viz.mp4'
        json_data = read_json(json_path)
        video = cv2.VideoCapture(self.video.path_to_processed_video)

        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cropped_height = 200  # Height of the cropped region
        cropped_y = frame_height - cropped_height  # Y-coordinate to start cropping from

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, FPS_OUT,
                              (frame_width, cropped_height))

        total_frames = len(json_data.items())
        step_size = 1

        for i, (frame_number, data) in enumerate(json_data.items()):
            if i % step_size == 0:
                video.set(cv2.CAP_PROP_POS_FRAMES, int(frame_number))
                ret, frame = video.read()
                if not ret:
                    break
                quarter = data[0]
                seconds_remaining = data[1]
                time_str = format_time(seconds_remaining)
                text_overlay = f"Quarter: {quarter} -- Time Remaining: {time_str}"
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Crop the frame
                frame = frame[cropped_y:, :, :]

                cv2.putText(frame, text_overlay, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                out.write(frame)

            progress = (i + 1) / total_frames
            if (i % 100 == 0):
                sys.stdout.write('\r')
                sys.stdout.write(
                    f"Processing frames: [{'=' * int(30 * progress):<30}] {round((progress * 100), 2)}%")
                sys.stdout.flush()

        video.release()
        out.release()
        sys.stdout.write('\n')
        print("Video processing complete!")

    def map_timestamps_to_statvu(self) -> bool:
        timestamp_data_path: str = self.data.path_to_timestamps
        timestamp_data_raw = open(timestamp_data_path)
        statvu_data_path: str = self.data.path_to_processed_data_unzipped
        statvu_data_raw = open(statvu_data_path)
        statvu_data: Dict[str, Any] = json.load(statvu_data_raw)
        timestamp_data: Dict[str, Union[int, List[Union[int, float]]]] = json.load(
            timestamp_data_raw)
        statvu_data["video_path"] = statvu_data_path.strip('.json') + '.mp4'
        for event in statvu_data['events']:
            for moment in event['moments']:
                quarter: str = str(moment[0])
                time: int = moment[2]
                key_exact: str = quarter + " " + str(time)
                key_one = quarter + " " + str(time - .01)
                key_two = quarter + " " + str(time - .02)
                key_three = quarter + " " + str(time - .03)
                key_four = quarter + " " + str(time + .01)
                key_five = quarter + " " + str(time + .02)
                key_six = quarter + " " + str(time + .03)
                if key_exact in timestamp_data:
                    moment.append(timestamp_data[key_exact])
                elif key_one in timestamp_data:
                    moment.append(timestamp_data[key_one])
                elif key_two in timestamp_data:
                    moment.append(timestamp_data[key_two])
                elif key_three in timestamp_data:
                    moment.append(timestamp_data[key_three])
                elif key_four in timestamp_data:
                    moment.append(timestamp_data[key_four])
                elif key_five in timestamp_data:
                    moment.append(timestamp_data[key_five])
                elif key_six in timestamp_data:
                    moment.append(timestamp_data[key_six])
                else:
                    moment.append(-1)
        out_path: str = f"{self.path_to_game_dir}/mapped.json"
        with open(out_path, 'w') as f:
            json.dump(statvu_data, f)
        return True
