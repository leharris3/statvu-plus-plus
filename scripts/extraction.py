import cv2
from PIL import Image
import pytesseract
import sys
import os

# MARK: Change to your local path to tessract.exe
PATH_TO_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
PRINT_FRAME_OFFSET = 100
BREAK_POINT = 300
QUARTER_CONFIG = r'--oem 3 --psm 8 -c tessedit_char_whitelist=1234'
CLOCK_CONFIG = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.:'
TRIM_VIDEO_BITRATE = 1000000
TIMESTAMPS = {}

# TODO: FOX, CSN, TSN
ROIS = {
    "TNT_QUARTER": [866, 12, 608, 22],
    "TNT_CLOCK": [955, 60, 610, 21],
    "ESP_QUARTER": [835, 13, 578, 21],
    "ESP_CLOCK": [885, 59, 578, 21],
    "FOX_QUARTER": [820, 183, 586, 38],
    "FOX_CLOCK": [820, 183, 586, 38],
    "CSN_QUARTER": [1005, 129, 623, 28],
    "CSN_CLOCK": [1005, 129, 623, 28],
    "TSN_QUARTER": [978, 157, 620, 23],
    "TSN_CLOCK": [978, 157, 620, 23]
}


def extract_timestamps_plus_trim(video_path: str, network: str):
    """Extract timestamps from video. Removes frames w/o entries."""
    pytesseract.pytesseract.tesseract_cmd = PATH_TO_TESSERACT
    QUARTER, CLOCK = f"{network}_QUARTER", f"{network}_CLOCK"
    step = 25
    try:
        q_width_start, q_width_offset, q_height_start, q_height_offset = ROIS[QUARTER]
        clk_width_start, clk_width_offset, clk_height_start, clk_height_offset = ROIS[CLOCK]
    except:
        print(f"Invalid network: {network}!")
        return

    capture = cv2.VideoCapture(video_path)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    quarter, time_seconds = None, None
    new_frame_index = 0
    first_timestamp_spotted = False

    output_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    output_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_fps = capture.get(cv2.CAP_PROP_FPS)
    output_fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_path = f"{video_path.strip('.mp4')}_trim.mp4"
    video_writer = cv2.VideoWriter(
        output_path, output_fourcc, output_fps, (output_width, output_height))

    for frame_index in range(total_frames):
        ret, frame = capture.read()
        q_roi = frame[q_height_start: q_height_start + q_height_offset,
                      q_width_start: q_width_start + q_width_offset]
        clk_roi = frame[clk_height_start: clk_height_start + clk_height_offset,
                        clk_width_start: clk_width_start + clk_width_offset]
        if not ret:
            break
        if new_frame_index == BREAK_POINT:
            break
        if ((frame_index % step) != 0):
            try:
                if (quarter is not None and time_seconds is not None):
                    TIMESTAMPS[int(new_frame_index)] = [
                        int(quarter), time_seconds]
                    video_writer.write(frame)
                    new_frame_index += 1
                    # print(quarter, time_seconds)
            except:
                pass
        else:
            # Quarter.
            roi_pil = Image.fromarray(q_roi)
            q_result = pytesseract.image_to_string(
                roi_pil, config=QUARTER_CONFIG)

            # Clock Time.
            roi_pil = Image.fromarray(clk_roi)
            clk_result = pytesseract.image_to_string(
                roi_pil, config=CLOCK_CONFIG)
            try:
                quarter = q_result[0]
                time_seconds = convert_time_to_seconds(clk_result)
                if quarter is not None and time_seconds is not None:
                    TIMESTAMPS[new_frame_index] = [int(quarter), time_seconds]
                    video_writer.write(frame)
                    # print(quarter, time_seconds)
                    new_frame_index += 1
                    if not first_timestamp_spotted:
                        first_timestamp_spotted = True
                        step = 5
            except:
                pass
        if ((frame_index % PRINT_FRAME_OFFSET) == 0):
            progress = (frame_index + 1) / total_frames
            print_progress(progress=progress)

    # Release the VideoWriter and capture objects
    video_writer.release()
    capture.release()
    os.remove(video_path)
    os.rename(output_path, video_path)

    print("\nProcessing completed.")
    return TIMESTAMPS


def convert_time_to_seconds(time_str):
    if ':' in time_str:
        time_parts = time_str.split(':')
        minutes = int(time_parts[0])
        seconds = float(time_parts[1])
    elif '.' in time_str:
        seconds = float(time_str)
        minutes = 0
    else:
        raise ValueError("Invalid time format")
    return minutes * 60 + seconds


def print_progress(progress):
    progress_bar = "[" + "#" * \
        int(progress * 20) + " " * (20 - int(progress * 20)) + "]"
    sys.stdout.write("\r{} {:.2f}%".format(progress_bar, progress * 100))
    sys.stdout.flush()


def save_frames_as_video(frames, output_path, fps=25, bitrate=TRIM_VIDEO_BITRATE):
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps,
                          (width, height), isColor=True)
    out.set(cv2.CAP_PROP_BITRATE, bitrate)
    for frame in frames:
        out.write(frame)
    out.release()
    print(f"Video saved successfully at: {output_path}")
