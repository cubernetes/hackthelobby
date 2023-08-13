#!/usr/bin/env python3

import sys
import random

from time import sleep
import numpy as np
import cv2
import requests

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

    img_height, img_width = img.shape[:2]
    img = img[
        margin_top:img_height-margin_bottom,
        margin_left:img_width-margin_right,
    ]

    b_top, b_bottom, b_left, b_right = [10]*4
    img = cv2.copyMakeBorder(img, b_top, b_bottom, b_left, b_right, cv2.BORDER_CONSTANT, value=(0, 0, 0))

    img = cv2.resize(img, (img42_side_len, img42_side_len))

    return img

img42_side_len: int = 100
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
    norm = np.linalg.norm(dir_vector)
    dir_vector /= (norm or 1)

    # TODO: Fix type issue
    side_len *= norm / 15
    # stretch /= (norm/30)

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
        cv2.namedWindow("Image", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Image", frame)
        cv2.waitKey(1)

def collect_vfx() -> None:
    requests.post('http://10.11.250.225:8080/api/v1/composition/layers/2/clips/5/connect')
    sleep(1)
    requests.post('http://10.11.250.225:8080/api/v1/composition/layers/2/clips/7/connect')

def die_vfx() -> None:
    requests.post('http://10.11.250.225:8080/api/v1/composition/layers/2/clips/6/connect')
    sleep(3)
    requests.post('http://10.11.250.225:8080/api/v1/composition/layers/2/clips/7/connect')

def green() -> None:
    threading.Thread(target=collect_vfx).start()

def die() -> None:
    threading.Thread(target=die_vfx).start()

def main() -> int:
    music = start_game_sfx()

    capture: cv2.VideoCapture = cv2.VideoCapture(0)
    hands: mp.solutions.hands.Hands = mp_hands.Hands(max_num_hands=1)
    collected_42: bool = True
    noise_42img: int = 5
    img42_x: int = -img42_side_len - 1 - noise_42img
    img42_y: int = -img42_side_len - 1 - noise_42img
    no_fingers: int = 0
    score: int = 0
    finger_x: int = -1
    finger_y: int = -1
    no_collect_ratio = 0
    no_finger_ratio = 0
    timer = 200

    i: int = 0
    while True:
        success: bool
        frame: np.ndarray
        success, frame = capture.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        ratio = max(no_finger_ratio, no_collect_ratio)
        frame = cv2.addWeighted(frame, 1 - ratio, np.ones(frame.shape, dtype=frame.dtype), ratio, 0)
        if i > 30:
            if collected_42:
                collected_42 = False
                frame_height, frame_width = frame.shape[:2]
                img42_x = random.randint(0, frame_width - img42_side_len - 1 - noise_42img)
                img42_y = random.randint(0, frame_height - img42_side_len - 1 - noise_42img)
                while ((finger_x - img42_x) ** 2 + (finger_y - img42_y) ** 2) ** .5 < 200:
                    img42_x = random.randint(0, frame_width - img42_side_len - 1 - noise_42img)
                    img42_y = random.randint(0, frame_height - img42_side_len - 1 - noise_42img)
            rand_noise_y = random.randint(0, noise_42img)
            rand_noise_x = random.randint(0, noise_42img)
            frame[
                img42_y + rand_noise_y : img42_y + img42_side_len + rand_noise_y,
                img42_x + rand_noise_x : img42_x + img42_side_len + rand_noise_x,
            ] = img42
            no_collect_ratio = min(i, timer) / timer

        finger_positions = list(get_finger_positions(frame, hands, add_landmarks=True))
        if finger_positions == []:
            no_fingers += 1
            no_finger_ratio = min(no_fingers, 255) / 255
        else:
            no_fingers = 0

        if ratio > 0.99:
            if music:
                music.kill()
            lost_sfx()
            die()
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
                        if score == 4200 / 4: # that's 25 collects
                            initiate_rick()
                        timer = 60 + (timer - 60) * .9
                        collect_sfx()
                        green()
        show_frame(frame, to_stdout=(not sys.stdout.isatty()))
        i += 1

if __name__ == '__main__':
    save_score(main())
