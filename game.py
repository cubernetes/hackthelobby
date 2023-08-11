#!/usr/bin/env python3

import sys
import random

import numpy as np
import cv2
from cv2 import VideoCapture

from utils import *

def get_42_img(
    img_path: str,
    margin_top: int,
    margin_bottom: int,
    margin_left: int,
    margin_right: int,
) -> np.ndarray:
    global img42_side_len

    img: np.ndarray = cv2.imread(img_path, 0)

    if len(img.shape) in [1, 2]:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    img = cv2.flip(img, 1)

    img_height, img_width = img.shape[:2]
    img = img[
        margin_top:img_height-margin_bottom,
        margin_left:img_width-margin_right,
    ]

    b_top, b_bottom, b_left, b_right = [10]*4
    img = cv2.copyMakeBorder(img, b_top, b_bottom, b_left, b_right, cv2.BORDER_CONSTANT, value=(0, 0, 0))

    img = cv2.resize(img, (img42_side_len, img42_side_len))

    return img

img42_side_len: int = 70
img42: np.ndarray = get_42_img(
    "./assets/img/42.png",
    margin_top    = 100 + 20,
    margin_bottom = 100 + 20,
    margin_left   = 100,
    margin_right  = 100,
)

def touches_42(x: int, y: int, img42_x: int, img42_y: int) -> bool:
    global collected_42

    return (
            img42_x <= x <= img42_x + img42_side_len
        and img42_y <= y <= img42_y + img42_side_len
    )

def add_directional_triangle(
    frame: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    rgb: tuple[int, int, int],
    side_len: int,
    stretch: float,
) -> tuple[int, int]:
    dir_vector: np.ndarray = np.array([
        x1 - x2, y1 - y2
    ]).astype(np.float64)

    # normalize
    dir_vector /= np.linalg.norm(dir_vector)

    triangle_height: float = side_len * (3**0.5) / 2
    half_base: float = side_len / 2

    perp_vector: np.ndarray = np.array([-dir_vector[1], dir_vector[0]])

    apex_vertex = (int(x1 + dir_vector[0] * triangle_height * 2/3 * stretch), int(y1 + dir_vector[1] * triangle_height * 2/3 * stretch))
    left_vertex = (int(x1 - perp_vector[0] * half_base - dir_vector[0] * triangle_height/3), 
       int(y1 - perp_vector[1] * half_base - dir_vector[1] * triangle_height/3))
    right_vertex = (int(x1 + perp_vector[0] * half_base - dir_vector[0] * triangle_height/3), 
       int(y1 + perp_vector[1] * half_base - dir_vector[1] * triangle_height/3))

    triangle: np.ndarray = np.array([apex_vertex, left_vertex, right_vertex])
    cv2.drawContours(frame, [triangle], 0, rgb, -1)

    return apex_vertex

def show_frame(frame: np.ndarray, to_stdout: bool=False) -> None:
    if to_stdout:
        sys.stdout.buffer.write(frame.tobytes())
    else:
        cv2.imshow("Image", frame)
        cv2.waitKey(1)

def main() -> int:
    start_sfx()

    capture: VideoCapture = cv2.VideoCapture(0)
    hands: mp.solutions.hands.Hands = mp_hands.Hands(max_num_hands=2)
    collected_42: bool = True
    img42_x: int = -img42_side_len - 1
    img42_y: int = -img42_side_len - 1
    no_fingers: int = 0
    score: int = 0

    i: int = 0
    while True:
        success: bool
        frame: np.ndarray
        success, frame = capture.read()
        if not success:
            continue

        if i > 30:
            if collected_42:
                collected_42 = False
                frame_height, frame_width = frame.shape[:2]
                img42_x = random.randint(0, frame_width - img42_side_len - 1)
                img42_y = random.randint(0, frame_height - img42_side_len - 1)
            frame[
                img42_y : img42_y+img42_side_len,
                img42_x : img42_x+img42_side_len,
            ] = img42

        finger_positions = list(get_finger_positions(frame, hands, add_landmarks=True))
        if finger_positions == []:
            no_fingers += 1
        else:
            no_fingers = 0
        if no_fingers > 70:
            return score

        for positions in finger_positions:
            index_knuckle_1_pos: tuple[int, int] = (-1, -1)
            for finger_id, finger_x, finger_y in positions:
                if finger_id == FingerType.INDEX_KNUCKLE_2:
                    index_knuckle_1_pos = (finger_x, finger_y)
                elif finger_id == FingerType.INDEX_TIP and index_knuckle_1_pos != (-1, -1):
                    apex_x, apex_y = add_directional_triangle(
                        frame,
                        finger_x,
                        finger_y,
                        *index_knuckle_1_pos,
                        (0, 0, 0,),
                        side_len=70,
                        stretch=2.0,
                    )
                    if not collected_42 and (
                           touches_42(apex_x, apex_y,     img42_x, img42_y)
                        or touches_42(finger_x, finger_y, img42_x, img42_y)
                    ):
                        collected_42 = True
                        i = 0
                        score += 42
                        collect_sfx()
        show_frame(frame, to_stdout=(not sys.stdout.isatty()))
        i += 1

if __name__ == '__main__':
    score: int = main()
    with open('./.score', 'w') as score_file:
        score_file.write(str(score))
    sys.exit(0)
