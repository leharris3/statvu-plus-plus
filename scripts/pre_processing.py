import os
import moviepy.editor as mp
import subprocess

NORMAL_WIDTH = 1280
NORMAL_HEIGHT = 720
NORMAL_FPS = 25


def normalize_video(file_path):
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
            "-preset", "medium",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            output_file
        ]
        subprocess.run(command)
        os.remove(file_path)
        os.rename(output_file, file_path)
    except Exception as e:
        print(f"Video conversion failed: {str(e)}")


def process_directory(directory):
    # Iterate over all files and directories in the given path
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            # Check if the file is an MP4 video
            if file.lower().endswith(".mp4"):
                normalize_video(file_path)
