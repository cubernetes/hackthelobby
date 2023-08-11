#!/usr/bin/env python3

import sys
import random
from enum import Enum
from typing import NoReturn, Generator
from types import ModuleType
from subprocess import Popen

import numpy as np
import mediapipe as mp
import cv2
from cv2 import VideoCapture

class FingerType(Enum):
    BASE             = 0
    BASE_RIGHT       = 1
    THUMB_BASE       = 2
    THUMB_KNUCKLE_1  = 3
    THUMB_TIP        = 4
    INDEX_BASE       = 5
    INDEX_KNUCKLE_1  = 6
    INDEX_KNUCKLE_2  = 7
    INDEX_TIP        = 8
    MIDDLE_BASE      = 9
    MIDDLE_KNUCKLE_1 = 10
    MIDDLE_KNUCKLE_2 = 11
    MIDDLE_TIP       = 12
    RING_BASE        = 13
    RING_KNUCKLE_1   = 14
    RING_KNUCKLE_2   = 15
    RING_TIP         = 16
    PINKY_BASE       = 17
    PINKY_KNUCKLE_1  = 18
    PINKY_KNUCKLE_2  = 19
    PINKY_TIP        = 20

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

mp_hands = mp.solutions.hands
mp_draw: ModuleType = mp.solutions.drawing_utils

img42_side_len = 70
img42: np.ndarray = get_42_img(
    "./42.png",
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
    dir_vector = np.array([
        x1 - x2, y1 - y2
    ]).astype(np.float64)

    # normalize
    dir_vector /= np.linalg.norm(dir_vector)

    triangle_height = side_len * (3**0.5) / 2
    half_base = side_len / 2

    perp_vector = np.array([-dir_vector[1], dir_vector[0]])

    apex_vertex = (int(x1 + dir_vector[0] * triangle_height * 2/3 * stretch), int(y1 + dir_vector[1] * triangle_height * 2/3 * stretch))
    left_vertex = (int(x1 - perp_vector[0] * half_base - dir_vector[0] * triangle_height/3), 
       int(y1 - perp_vector[1] * half_base - dir_vector[1] * triangle_height/3))
    right_vertex = (int(x1 + perp_vector[0] * half_base - dir_vector[0] * triangle_height/3), 
       int(y1 + perp_vector[1] * half_base - dir_vector[1] * triangle_height/3))

    triangle = np.array([apex_vertex, left_vertex, right_vertex])
    cv2.drawContours(frame, [triangle], 0, rgb, -1)

    return apex_vertex

def get_finger_positions(
    frame: np.ndarray,
    hands: mp.solutions.hands.Hands,
    add_landmarks: bool,
) -> Generator[list[tuple[int, int, int]], None, None]:
    height, width = frame.shape[:2]

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            positions = []
            for id, lm in enumerate(hand_landmarks.landmark):
                x = int(lm.x * width)
                y = int(lm.y * height)
                positions.append((FingerType(id), x, y))
            yield positions
            if add_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

def show_frame(frame: np.ndarray, to_stdout: bool=False) -> None:
    if to_stdout:
        sys.stdout.buffer.write(frame.tobytes())
    else:
        cv2.imshow("Image", frame)
        cv2.waitKey(1)

def collect_sfx() -> None:
    Popen(['paplay', './sfx/collect.mp3'])

def main() -> NoReturn:
    Popen(['paplay', './sfx/start.mp3'])

    capture: VideoCapture = cv2.VideoCapture(0)
    hands = mp_hands.Hands(max_num_hands=2)
    collected_42 = True
    img42_x = -img42_side_len - 1
    img42_y = -img42_side_len - 1

    i = 0
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

        for positions in get_finger_positions(frame, hands, add_landmarks=True):
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
                    if not collected_42 and touches_42(apex_x, apex_y, img42_x, img42_y):
                        collected_42 = True
                        i = 0
                        collect_sfx()
        show_frame(frame, to_stdout=True)
        i += 1

if __name__ == '__main__':
    main()
