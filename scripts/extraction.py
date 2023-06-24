import cv2
from PIL import Image
import pytesseract
import sys
import re

# MARK: Change to your local path to tessract.e
PATH_TO_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
STEP = 5
ROI_FRAME_INDEX = 100
BREAK_POINT = -1  # Full length video by default.

ROIS = {
    "TNT": [860, 155, 605, 30],
    "ESP_QUARTER": [835, 13, 578, 21],
    "ESP_CLOCK": [885, 59, 578, 21],
    "FOX": [820, 183, 586, 38],
    "CSN": [1005, 129, 623, 28],
    "TSN": [978, 157, 620, 23]
}


def extract_timestamps(video_path: str, network: str) -> bool:
    pytesseract.pytesseract.tesseract_cmd = PATH_TO_TESSERACT
    timestamps = {}

    QUARTER = f"{network}_QUARTER"
    CLOCK = f"{network}_CLOCK"
    try:
        q_width_start, q_width_offset, q_height_start, q_height_offset = ROIS[QUARTER]
        clk_width_start, clk_width_offset, clk_height_start, clk_height_offset = ROIS[CLOCK]
    except:
        print(f"Invalid network: {network}!")
        return []

    capture = cv2.VideoCapture(video_path)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    quarter = None
    time_seconds = None

    quarter_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=1234'
    clock_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.:'

    for frame_index in range(total_frames):
        ret, frame = capture.read()
        if not ret:
            break

        if frame_index % STEP != 0:
            try:
                if quarter is not None and time_seconds is not None:
                    timestamps[int(frame_index)] = [int(quarter), time_seconds]
                    # print(quarter, time_seconds)
            except:
                pass
            continue

        if frame_index % ROI_FRAME_INDEX == 0:
            progress = (frame_index + 1) / total_frames
            print_progress(progress=progress)

        if frame_index == BREAK_POINT:
            break

        q_roi = frame[q_height_start: q_height_start + q_height_offset,
                      q_width_start: q_width_start + q_width_offset]
        clk_roi = frame[clk_height_start: clk_height_start + clk_height_offset,
                        clk_width_start: clk_width_start + clk_width_offset]

        # Quarter.
        roi_pil = Image.fromarray(q_roi)
        q_result = pytesseract.image_to_string(roi_pil, config=quarter_config)

        # Clock Time.
        roi_pil = Image.fromarray(clk_roi)
        clk_result = pytesseract.image_to_string(roi_pil, config=clock_config)

        try:
            quarter = q_result[0]
            time_seconds = convert_time_to_seconds(clk_result)
            if quarter is not None and time_seconds is not None:
                timestamps[int(frame_index)] = [int(quarter), time_seconds]
            # print("quarter: ", quarter, "time: ", time_seconds)
        except:
            pass

    capture.release()
    print("\nProcessing completed.")
    return timestamps


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
