import cv2
import mediapipe as mp
from gtts import gTTS
from playsound import playsound
import threading
import os
import time

# ---------- SPEAK FUNCTION ----------
def speak(text):
    filename = "voice.mp3"
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

# ---------- MEDIAPIPE ----------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# ---------- CAMERA ----------
cap = cv2.VideoCapture(0)
cap.set(3, 960)
cap.set(4, 720)

last_spoken = ""
last_time = 0

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    gesture = ""
    sentence = ""

    # --- Small Clean Header ---
    cv2.rectangle(img, (0, 0), (960, 45), (40, 40, 40), -1)
    cv2.putText(img, "SignBridge AI",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2)

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

            h, w, _ = img.shape
            lm = []

            for point in hand.landmark:
                lm.append((int(point.x * w), int(point.y * h)))

            tips = [8, 12, 16, 20]
            fingers = []

            for tip in tips:
                if lm[tip][1] < lm[tip - 2][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            thumb_up = lm[4][1] < lm[3][1]
            pinky_up = lm[20][1] < lm[18][1]

            # ---- Gesture Logic ----
            if thumb_up and fingers == [0, 0, 0, 0]:
                gesture = "Thumbs Up"
                sentence = "all the best bunny"

            elif thumb_up and pinky_up and fingers[0:3] == [0, 0, 0]:
                gesture = "Call Me"
                sentence = "Call Me vishnu"

            elif fingers == [1, 1, 1, 1] and thumb_up:
                gesture = "Hello"
                sentence = "Hello vishnu, nice to meet you"

            elif fingers == [1, 1, 0, 0]:
                gesture = "Peace"
                sentence = "Thank You vishnu"

            elif fingers == [1, 0, 0, 0]:
                gesture = "One"
                sentence = "Please Wait bunny"

            elif not thumb_up and fingers == [0, 0, 0, 0]:
                gesture = "Fist"
                sentence = "I Agree bunny"

            # ---- Smaller Display Box ----
            if gesture != "":
                cv2.rectangle(img, (300, 260), (660, 330), (50, 50, 50), -1)

                cv2.putText(img, gesture,
                            (330, 305),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1.1,
                            (220, 220, 220),
                            2)

            # ---- Speech Control ----
            if sentence != "" and (sentence != last_spoken or time.time() - last_time > 3):
                threading.Thread(target=speak, args=(sentence,)).start()
                last_spoken = sentence
                last_time = time.time()

    else:
        last_spoken = ""

    cv2.imshow("SignBridge AI", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()