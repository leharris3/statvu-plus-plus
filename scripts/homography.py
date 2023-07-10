#omsairam omsairam omsairam

import cv2
from utils import mouse_handler
from utils import get_four_points
import numpy as np

def homographyCalc(src, im_dst, pts1, pts2):
    if src == []:
        pts_src = pts1
        pts_dst = pts2
    else:
        # Four corners of the source image
        pts_src = get_four_points(src)
        pts_src = np.array([[[pts_src[0][0], pts_src[0][1]], \
                             [pts_src[1][0], pts_src[1][1]], \
                             [pts_src[2][0], pts_src[2][1]], \
                             [pts_src[3][0], pts_src[3][1]]]])
        #only works when outside the else block
        pts_dst = get_four_points(im_dst)
        pts_dst = np.array([[[pts_dst[0][0], pts_dst[0][1]], \
                             [pts_dst[1][0], pts_dst[1][1]], \
                             [pts_dst[2][0], pts_dst[2][1]], \
                             [pts_dst[3][0], pts_dst[3][1]]]])
    print("in homo", type(pts_dst))
    print(pts_src)





    # Read destination image.

    #im_dst = cv2.imread('omsaiSoccerDest.jpeg')


    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination based on homography
    #im_out = cv2.warpPerspective(src, h, (im_dst.shape[1], im_dst.shape[0]))

    #cv2.imwrite('image_ortho_test_book.png', im_out)
    # bottom_pts = np.float32(bottom_pts).reshape(-1,1,2)


    return h #,  im_out

def homo(im_dst, points, h1, h2):
    print(" \nNEW BATCH:")
    print(points)
    for i in points:
        print("PTS[i]: ", i)
        pts = np.array([[float(i[0]), float(i[1])]])
        pts = np.float32(pts).reshape(-1, 1, 2)

        pts_homo = cv2.perspectiveTransform(pts, h1)
        #pts_homo = cv2.perspectiveTransform(pts_homo1, h2)
        print(pts_homo)
        img = cv2.circle(im_dst, (int(pts_homo[0][0][0]), int(pts_homo[0][0][1])), 20, (255, 0, 0), 20)
    cv2.imshow("g",img)
    cv2.waitKey(1)
    return img

def run(game_vid, event_vid, pts):
    cap = cv2.VideoCapture(event_vid)
    ret, frame_src = cap.read()
    cap = cv2.VideoCapture(game_vid)
    i = 0
    while 1:
        ret, frame = cap.read()

        if i == 0:
            h = homographyCalc(frame_src, frame)
            pts = get_four_points(frame_src)
            pts = [(pts[0][0], pts[0][1])]
        if frame is None:
            break
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        homo(frame, frame_src, pts, h)
        i = i + 1


#run("vid.mov","Event_156.mp4", [(0,0)])


