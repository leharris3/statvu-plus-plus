# 1. Normalize all videos
# 2. Temporal grounding + verification for all videos
# 3. Append new data to statvu position data
# 4. Visualize and verify

import os
import moviepy.editor as mp


def normalize_video(file_path):
    try:
        # Set the target resolution and frame rate
        target_resolution = (1280, 720)
        target_fps = 25

        with mp.VideoFileClip(file_path) as video:
            # Resize the video to the target resolution
            resized_video = video.resize(
                height=target_resolution[1], width=target_resolution[0])

            # Set the frame rate to the target frame rate
            final_video = resized_video.set_fps(target_fps)

            # Generate a temporary file path for the final video
            temp_file_path = file_path + "_mod.mp4"

            # Write the final video to the temporary file path
            final_video.write_videofile(
                temp_file_path, codec="libx264", audio_codec="aac", fps=target_fps)

        # Close the original video file
        video.reader.close()

        # Delete the original file
        os.remove(file_path)

        # Rename the temporary file to the original file path
        os.rename(temp_file_path, file_path)

        print("Video conversion successful.")
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
