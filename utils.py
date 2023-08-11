from enum import Enum
from subprocess import Popen
from typing import Generator
from types import ModuleType

import numpy as np
import mediapipe as mp
import cv2
from cv2 import VideoCapture

mp_hands = mp.solutions.hands
mp_draw: ModuleType = mp.solutions.drawing_utils

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


def collect_sfx() -> None:
    Popen(['paplay', './assets/sfx/collect.mp3'])

def start_sfx() -> None:
    Popen(['paplay', './assets/sfx/start.mp3'])

def show_matrix() -> None:
    Popen(['tmatrix'])

def found_hands() -> bool:
    capture: VideoCapture = cv2.VideoCapture(0)
    hands = mp_hands.Hands(max_num_hands=1)
    success, frame = capture.read()
    if not success:
        return False

    return list(get_finger_positions(frame, hands)) != []

def get_finger_positions(
    frame: np.ndarray,
    hands: mp.solutions.hands.Hands,
    add_landmarks: bool=False,
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
