#omsairam omsairam omsairam
#omsairam omsairam omsairam
#omsairam omsairam omsairam


import json
import cv2
from homography import homo
from homography import homographyCalc
import numpy as  np
def get_data(file):
    with open(file) as json_file:
        data = json.load(json_file)
    return data
def modify_data(data,event, mstart, mend):
    data["events"] = [data["events"][event]]
    data["events"][0]["moments"] = data["events"][0]["moments"][mstart:mend]
    return data


def test_coords(i, moments):
    img = cv2.imread(i)
    cropped_img = img[0:100, 0:100]
    for frame in moments:
        for xy in frame:
            print(xy)
            cv2.circle(cropped_img, xy, 2, (255,0,0), 1)
            cv2.imshow("f", cropped_img)
            cv2.waitKey(1)

def run(game_vid, event_vid, pts):
    cap = cv2.VideoCapture(event_vid)
    ret, frame_src = cap.read()

    pts_src = np.array([[[0, 50], \
                         [0, 0], \
                         [100, 0], \
                         [100, 50]]])

    pts_dst = np.array([[[288, 136], \
                         [288, 619], \
                         [1248, 165], \
                      [1248, 139]]])
    print("in run",type(pts_dst))
    print(pts_src)

    h1 = homographyCalc([], frame_src, pts_src, pts_dst)

    cap = cv2.VideoCapture(game_vid)
    i = 0
    while 1:
        ret, frame = cap.read()

        if i == 0:
            h2 = homographyCalc(frame_src, frame, None, None)

        if frame is None:
            break
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        homo(frame, pts[i], h1, h2)
        i = i + 1



if __name__ == "__main__":
    d = get_data('0021500662.json')
    d = modify_data(d, 132, 230, 378)
    coords = []
    for moment in d["events"][0]["moments"]:
        frame_pts = []
        for p in moment[5]:
            frame_pts.append((p[2],p[3]))
        coords.append(frame_pts)
    run("Event_156.mp4", "Event_156.mp4",coords)









