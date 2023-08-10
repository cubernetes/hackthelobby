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

    while True:
        success, frame = cap.read()
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                visited_7 = False
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = frame.shape
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


        if not success:
            continue
        sys.stdout.buffer.write(frame.tobytes())
        # cv2.imshow("Image", frame)
        # cv2.waitKey(1)


if __name__ == '__main__':
    main()
