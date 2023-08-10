#!/usr/bin/env python3

import sys
# import time
from typing import NoReturn

import cv2
import numpy as np
import mediapipe as mp

def main() -> NoReturn:
    cap = cv2.VideoCapture(0)
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=.5,
        min_tracking_confidence=.5,
    )
    mpDraw = mp.solutions.drawing_utils
    # pTime = 0
    # cTime = 0

    img = cv2.imread("42.png", 0)
    if len(img.shape) == 2 or img.shape[2] == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = cv2.flip(img, 1)

    height, width, _ = img.shape
    margin = 100
    top_margin = margin + 20
    bottom_margin = margin + 20
    left_margin = margin
    right_margin = margin
    img = img[top_margin:height-bottom_margin, left_margin:width-right_margin]

    side_length = min(640, 480) // 3
    overlay_resized = cv2.resize(img, (side_length, side_length))
    print(repr(overlay_resized))
    input()
    sys.exit()

    while True:
        success, frame = cap.read()
        if not success:
            continue

        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        h, w, c = frame.shape

        img_x, img_y = 10, 10
        frame[img_y:img_y+side_length, img_x:img_x+side_length] = overlay_resized

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                visited_7 = False
                for id, lm in enumerate(handLms.landmark):
                    cx = int(lm.x * w)
                    cy = int(lm.y * h)
                    # 7 one-before-index, 8 index, 4 thumb, 0 base
                    if id == 7:
                        one_before_index_x = cx
                        one_before_index_y = cy
                        visited_7 = True
                    if id == 8:
                        pass
                        # open('/dev/pts/1', 'w').write(
                        #     f'{id}, {cx}, {cy}\n'
                        # )

                        if visited_7:
                            dir_vector = np.array([cx - one_before_index_x, cy - one_before_index_y])
                            dir_vector = dir_vector.astype(np.float64)
                            dir_vector /= np.linalg.norm(dir_vector)

                            s = 100
                            h = s * (3**0.5) / 2
                            half_base = s / 2

                            perp_vector = np.array([-dir_vector[1], dir_vector[0]])

                            pt1 = (int(cx + dir_vector[0] * h * 2/3), int(cy + dir_vector[1] * h * 2/3))
                            pt2 = (int(cx - perp_vector[0] * half_base - dir_vector[0] * h/3), 
                               int(cy - perp_vector[1] * half_base - dir_vector[1] * h/3))
                            pt3 = (int(cx + perp_vector[0] * half_base - dir_vector[0] * h/3), 
                               int(cy + perp_vector[1] * half_base - dir_vector[1] * h/3))

                            triangle_cnt = np.array([pt1, pt2, pt3])
                            cv2.drawContours(frame, [triangle_cnt], 0, (0,0,0), -1)
                        else:
                            cv2.circle(frame, (cx, cy), 40, (0, 0, 0), cv2.FILLED)
                mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

        # cTime = time.time()
        # fps = 1 / (cTime - pTime)
        # pTime = cTime

        # cv2.putText(frame, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        sys.stdout.buffer.write(frame.tobytes())
        # cv2.imshow("Image", frame)
        # cv2.waitKey(1)


if __name__ == '__main__':
    main()
