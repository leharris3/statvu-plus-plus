import os
import subprocess


class Video:

    def __init__(self, title: str, network: str) -> None:
        self.path_to_unprocessed_video = f"unprocessed-videos/{title}.{network}.mp4"
        self.path_to_processed_video = f"statvu-plus-plus/{title}.{network}/{title}.{network}.mp4"
        self.abs_path_to_processed_video = os.path.abspath(
            self.path_to_processed_video)

    def normalize(self) -> bool:
        self.normalize_video()
        return True

    def normalize_video(self):
        file_path = self.path_to_processed_video
        try:
            directory = os.path.dirname(file_path)
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(directory, f"{file_name}_converted.mp4")
            command = [
                "ffmpeg",
                "-i", file_path,
                "-vf", "scale=1280:720",
                "-r", "25",
                "-c:v", "libx264",
                "-crf", "23",
                "-preset", "slow",
                "-c:a", "aac",
                "-b:a", "0",
                "-tune", "animation",
                "-loglevel", "info",
                output_file
            ]
            subprocess.run(command)
            os.remove(file_path)
            os.rename(output_file, file_path)
        except Exception as e:
            print(f"Video conversion failed: {str(e)}")
