import cv2
import json
import matplotlib.pyplot as plt
import sys
import os

FRAME_WIDTH_OUT = 1280
FRAME_HEIGHT_OUT = 720
FPS_OUT = 25


def read_json(file_path):
    with open(file_path) as file:
        return json.load(file)


def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def visualize(video_path):

    file_path = os.path.splitext(video_path)[0]
    json_path = file_path + '.json'
    output_path = file_path + '_viz.mp4'
    json_data = read_json(json_path)

    # Open the video file
    video = cv2.VideoCapture(video_path)

    # Create a VideoWriter object to save the processed frames
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, FPS_OUT,
                          (FRAME_WIDTH_OUT, FRAME_HEIGHT_OUT))

    # Get total frames and calculate progress step
    total_frames = len(json_data.items())

    # Set the step size to read every 5th frame
    step_size = 25
    # Iterate through the JSON data with a step size of 5
    for i, (frame_number, data) in enumerate(json_data.items()):
        # Read the corresponding video frame only if it's a multiple of 5
        if i % step_size == 0:
            # Read the frame at the specified frame number
            video.set(cv2.CAP_PROP_POS_FRAMES, int(frame_number))
            ret, frame = video.read()

            if not ret:
                break

            # Extract the quarter number and seconds remaining from the data
            quarter = data[0]
            seconds_remaining = data[1]

            # Convert seconds to MM:SS format
            time_str = format_time(seconds_remaining)

            # Create a text overlay with quarter and time remaining
            text_overlay = f"Quarter: {quarter} -- Time Remaining: {time_str}"

            # Display the frame with the text overlay
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.putText(frame, text_overlay, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            out.write(frame)

        # Update progress bar
        progress = (i + 1) / total_frames
        sys.stdout.write('\r')
        sys.stdout.write(
            f"Processing frames: [{'=' * int(30 * progress):<30}] {round((progress * 100), 2)}%")
        sys.stdout.flush()

    # Release the video capture and writer objects
    video.release()
    out.release()

    # Show completion message
    sys.stdout.write('\n')
    print("Video processing complete!")
