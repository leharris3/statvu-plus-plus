import json
import cv2
from PIL import Image
import pytesseract
import sys
import re

ROIS = {
    "TNT": [860, 155, 605, 30],
    "ESPN": [828, 125, 578, 23],
    "FOX": [820, 183, 586, 38]
}


def map_fox(video_path):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    timestamps = {}
    roi_frame_index = 0

    width_start = ROIS["TNT"][0]
    width_offset = ROIS["TNT"][1]
    height_start = ROIS["TNT"][2]
    height_offset = ROIS["TNT"][3]

    capture = cv2.VideoCapture(video_path)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    for frame_index in range(total_frames):
        ret, frame = capture.read()
        if not ret:
            break
        frame_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Preprocessing
        roi = frame_image[height_start: height_start +
                          height_offset, width_start: width_start + width_offset]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        roi_blur = cv2.GaussianBlur(roi_gray, (5, 5), 0)
        _, roi_binary = cv2.threshold(roi_blur, 127, 255, cv2.THRESH_BINARY)
        roi_pil = Image.fromarray(roi_binary)

        # OCR
        custom_config = r'--oem 1 --psm 6'
        result = pytesseract.image_to_string(roi_pil, config=custom_config)

        quarter = None
        time_seconds = None

        text = result.split()
        try:
            quarter = re.sub(r'\D', '', text[0])[0]
            time_seconds = convert_time_to_seconds(text[1])
            # print(quarter, time_seconds)
        except:
            pass

        if quarter is not None and time_seconds is not None:
            key = str(quarter) + str(time_seconds)
            timestamps[key] = [int(frame_index)]

        # Save example frame.
        if frame_index == roi_frame_index:
            roi_pil.save('roi_frame.jpg')
        progress = (frame_index + 1) / total_frames
        print_progress(progress=progress)

    capture.release()
    print("\nProcessing completed.")
    return timestamps


# TODO: Incorrect data across entire video.
def map_espn(video_path):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    timestamps = {}
    roi_frame_index = 0

    width_start = ROIS["ESPN"][0]
    width_offset = ROIS["ESPN"][1]
    height_start = ROIS["ESPN"][2]
    height_offset = ROIS["ESPN"][3]

    capture = cv2.VideoCapture(video_path)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    for frame_index in range(total_frames):
        ret, frame = capture.read()
        if not ret:
            break
        frame_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Preprocessing
        roi = frame_image[height_start: height_start +
                          height_offset, width_start: width_start + width_offset]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        roi_blur = cv2.GaussianBlur(roi_gray, (5, 5), 0)
        _, roi_threshhold = cv2.threshold(
            roi_blur, 127, 255, cv2.THRESH_BINARY_INV)
        roi_pil = Image.fromarray(roi_threshhold)

        # OCR
        custom_config = r'--oem 1 --psm 6'
        result = pytesseract.image_to_string(roi_pil, config=custom_config)

        quarter = None
        time_seconds = None

        # Post-processing
        text = result.split()
        try:
            quarter_text = text[0].replace('I', '1').replace('i', '1')
            quarter = re.sub(r'\D', '', quarter_text[0])[0]
            time_seconds = convert_time_to_seconds(text[1])
            # print(quarter, time_seconds)
        except:
            pass

        if quarter is not None and time_seconds is not None:
            timestamps[int(frame_index)] = [quarter, time_seconds]

        if frame_index == roi_frame_index:
            roi_pil.save('roi_frame.jpg')

        progress = (frame_index + 1) / total_frames
        print_progress(progress=progress)

    capture.release()
    print("\nProcessing completed.")
    return timestamps


# TODO: Functional.
def map_tnt(video_path):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    timestamps = {}
    roi_frame_index = 0

    width_start = ROIS["TNT"][0]
    width_offset = ROIS["TNT"][1]
    height_start = ROIS["TNT"][2]
    height_offset = ROIS["TNT"][3]

    capture = cv2.VideoCapture(video_path)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    for frame_index in range(total_frames):
        ret, frame = capture.read()
        if not ret:
            break
        frame_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Preprocessing
        roi = frame_image[height_start: height_start +
                          height_offset, width_start: width_start + width_offset]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        roi_blur = cv2.GaussianBlur(roi_gray, (5, 5), 0)
        _, roi_binary = cv2.threshold(roi_blur, 127, 255, cv2.THRESH_BINARY)
        roi_pil = Image.fromarray(roi_binary)

        # OCR
        custom_config = r'--oem 1 --psm 6'
        result = pytesseract.image_to_string(roi_pil, config=custom_config)

        quarter = None
        time_seconds = None

        text = result.split()
        try:
            quarter = re.sub(r'\D', '', text[0])[0]
            time_seconds = convert_time_to_seconds(text[1])
            # print(quarter, time_seconds)
        except:
            pass

        if quarter is not None and time_seconds is not None:
            timestamps[int(frame_index)] = [quarter, time_seconds]

        # Save example frame.
        if frame_index == roi_frame_index:
            roi_pil.save('roi_frame.jpg')
        progress = (frame_index + 1) / total_frames
        print_progress(progress=progress)

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


def extract_time(video_path, network):
    in_path = video_path
    dot_index = in_path.rfind(".")
    out_path = in_path[: dot_index] + ".json"

    # Select network extraction technique.
    if network == "TNT":
        timestamps = map_tnt(in_path)
    elif network == "ESPN":
        timestamps = map_espn(in_path)
    elif network == "FOX":
        timestamps = map_fox(in_path)
    with open(out_path, 'w') as f:
        json.dump(timestamps, f)

    print("Result saved as", out_path)


extract_time(video_path=sys.argv[1], network=sys.argv[2])
