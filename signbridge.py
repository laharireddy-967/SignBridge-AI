import cv2
import mediapipe as mp
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
import threading
import os
import time


# ==========================================================
# SETTINGS
# ==========================================================

language = "en"


# ==========================================================
# GESTURE → MESSAGE
# ==========================================================

translations = {
    "HELLO": "Hello! Nice to meet you",
    "PEACE": "Thank You",
    "ONE": "Please Wait",
    "FIST": "I Agree",
    "THUMBS UP": "All the Best",
    "CALL ME": "Call Me",
    "HELP": "Help"
}


# ==========================================================
# TEXT / VOICE → IMAGE NAME
# ==========================================================

def phrase_to_image(text):

    text = text.lower().strip()

    # Remove punctuation
    text = text.replace(".", "")
    text = text.replace(",", "")
    text = text.replace("!", "")
    text = text.replace("?", "")

    # Full phrases
    phrase_map = {

        "hello": "hello",
        "hello nice to meet you": "hello",

        "thank you": "thankyou",
        "thanks": "thankyou",

        "please wait": "pleasewait",

        "i agree": "agree",
        "agree": "agree",

        "good job": "goodjob",
        "goodjob": "goodjob",

        "all the best": "goodjob",

        "call me": "callme",
        "callme": "callme",

        "help": "help"
    }

    if text in phrase_map:
        return phrase_map[text]

    # Handle phrases where spaces may disappear
    text_without_spaces = text.replace(" ", "")

    fallback_map = {

        "hello": "hello",
        "thankyou": "thankyou",
        "thanks": "thankyou",

        "pleasewait": "pleasewait",

        "iagree": "agree",
        "agree": "agree",

        "goodjob": "goodjob",

        "allthebest": "goodjob",

        "callme": "callme",

        "help": "help"
    }

    if text_without_spaces in fallback_map:
        return fallback_map[text_without_spaces]

    return text_without_spaces


# ==========================================================
# SIGN IMAGE
# ==========================================================

sign_image = None


def load_sign_image(text):

    global sign_image

    image_name = phrase_to_image(text)

    extensions = [
        ".jpg",
        ".jpeg",
        ".png"
    ]

    sign_image = None

    for ext in extensions:

        image_path = os.path.join(
            "signs",
            image_name + ext
        )

        if os.path.exists(image_path):

            sign_image = cv2.imread(image_path)

            if sign_image is not None:

                sign_image = cv2.resize(
                    sign_image,
                    (500, 500)
                )

                print("Loaded sign image:", image_path)

            return

    print("No sign image found for:", text)
    print("Looking for:", image_name)


# ==========================================================
# TEXT TO SPEECH
# ==========================================================

def speak(text):

    try:

        filename = f"voice_{time.time()}.mp3"

        tts = gTTS(
            text=text,
            lang=language
        )

        tts.save(filename)

        playsound(filename)

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:

        print("Speech error:", e)


# ==========================================================
# SPEECH TO TEXT
# ==========================================================

def speech_to_text():

    global display_text
    global sign_output
    global sign_image
    global input_mode

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            print("\nListening...")
            print("Please speak now...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=6
            )

        text = recognizer.recognize_google(audio)

        print("You said:", text)

        # Show spoken message
        display_text = text.upper()

        # IMPORTANT:
        # Clear previous gesture name
        sign_output = ""

        # Tell program this came from speech
        input_mode = "speech"

        # Load corresponding sign image
        load_sign_image(text)

    except sr.WaitTimeoutError:

        print("No speech detected.")

    except sr.UnknownValueError:

        print("Could not understand the speech.")

    except sr.RequestError as e:

        print("Speech recognition service error:", e)

    except Exception as e:

        print("Microphone error:", e)


# ==========================================================
# MEDIAPIPE
# ==========================================================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils


# ==========================================================
# CAMERA
# ==========================================================

cap = cv2.VideoCapture(0)

cap.set(3, 960)
cap.set(4, 720)


# ==========================================================
# VARIABLES
# ==========================================================

current_gesture = ""

stable_count = 0

display_text = ""

sign_output = ""

typed_text = ""

typing_mode = False

input_mode = ""


# ==========================================================
# MAIN LOOP
# ==========================================================

while True:

    success, img = cap.read()

    if not success:
        print("Could not access camera.")
        break

    img = cv2.flip(img, 1)

    imgRGB = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(imgRGB)

    gesture = ""


    # ======================================================
    # GESTURE DETECTION
    # ======================================================

    if results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                img,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            h, w, _ = img.shape

            lm = []

            for point in hand.landmark:

                lm.append(
                    (
                        int(point.x * w),
                        int(point.y * h)
                    )
                )


            # ------------------------------------------------
            # FINGER DETECTION
            # ------------------------------------------------

            tips = [8, 12, 16, 20]

            fingers = []

            for tip in tips:

                if lm[tip][1] < lm[tip - 2][1]:

                    fingers.append(1)

                else:

                    fingers.append(0)


            # ------------------------------------------------
            # THUMB / PINKY
            # ------------------------------------------------

            thumb_up = lm[4][1] < lm[3][1]

            pinky_up = lm[20][1] < lm[18][1]


            # =================================================
            # GESTURE RULES
            # =================================================

            if thumb_up and fingers == [0, 0, 0, 0]:

                gesture = "THUMBS UP"


            elif (
                thumb_up
                and pinky_up
                and fingers[0:3] == [0, 0, 0]
            ):

                gesture = "CALL ME"


            elif fingers == [1, 1, 1, 1] and not thumb_up:

                gesture = "HELLO"


            elif fingers == [1, 1, 0, 0]:

                gesture = "PEACE"


            elif fingers == [1, 0, 0, 0]:

                gesture = "ONE"


            elif not thumb_up and fingers == [0, 0, 0, 0]:

                gesture = "FIST"


            elif fingers == [1, 0, 1, 0]:

                gesture = "HELP"


    # ======================================================
    # STABILITY FILTER
    # ======================================================

    if gesture == current_gesture and gesture != "":

        stable_count += 1

    else:

        stable_count = 0

        current_gesture = gesture


    # ======================================================
    # CONFIRM GESTURE
    # ======================================================

    if stable_count == 6:

        if gesture in translations:

            message = translations[gesture]

            display_text = message.upper()

            sign_output = gesture

            # IMPORTANT:
            # This tells the program that camera
            # is the current input.
            input_mode = "gesture"

            # Load corresponding sign image
            load_sign_image(message)

            # Speak message
            threading.Thread(
                target=speak,
                args=(message,),
                daemon=True
            ).start()


    # ======================================================
    # UI
    # ======================================================

    cv2.putText(
        img,
        "SignBridge AI",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 255),
        2
    )


    cv2.putText(
        img,
        "T: Type    M: Speech    Q: Quit",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )


    # ======================================================
    # SHOW GESTURE NAME ONLY FOR CAMERA INPUT
    # ======================================================

    if input_mode == "gesture" and sign_output != "":

        color = (
            (0, 0, 255)
            if sign_output == "HELP"
            else (0, 255, 0)
        )


        cv2.putText(
            img,
            "GESTURE:",
            (40, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )


        cv2.putText(
            img,
            sign_output,
            (40, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.3,
            color,
            3
        )


    # ======================================================
    # MESSAGE
    # ======================================================

    if display_text != "":

        cv2.putText(
            img,
            "MESSAGE:",
            (40, 320),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )


        cv2.putText(
            img,
            display_text,
            (40, 360),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (255, 255, 0),
            3
        )


    # ======================================================
    # TYPING DISPLAY
    # ======================================================

    if typing_mode:

        cv2.putText(
            img,
            "Typing: " + typed_text,
            (40, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )


    # ======================================================
    # CAMERA WINDOW
    # ======================================================

    cv2.imshow(
        "SignBridge AI",
        img
    )


    # ======================================================
    # SIGN IMAGE WINDOW
    # ======================================================

    if sign_image is not None:

        cv2.imshow(
            "Sign Image",
            sign_image
        )


    # ======================================================
    # KEYBOARD
    # ======================================================

    key = cv2.waitKey(1) & 0xFF


    # ------------------------------------------------------
    # QUIT
    # ------------------------------------------------------

    if key == ord('q'):

        break


    # ------------------------------------------------------
    # SPEECH
    # ------------------------------------------------------

    elif key == ord('m'):

        threading.Thread(
            target=speech_to_text,
            daemon=True
        ).start()


    # ------------------------------------------------------
    # TYPING
    # ------------------------------------------------------

    elif key == ord('t'):

        typing_mode = True

        typed_text = ""

        # Clear previous gesture
        sign_output = ""

        input_mode = "text"


    # ------------------------------------------------------
    # ENTER TYPED MESSAGE
    # ------------------------------------------------------

    elif typing_mode:

        if key == 13:

            if typed_text.strip() != "":

                display_text = typed_text.upper()

                # Clear previous gesture name
                sign_output = ""

                # Text input mode
                input_mode = "text"

                # Find sign image
                load_sign_image(typed_text)

            typing_mode = False


        # BACKSPACE
        elif key == 8:

            typed_text = typed_text[:-1]


        # NORMAL CHARACTERS
        elif 32 <= key <= 126:

            typed_text += chr(key)


# ==========================================================
# CLOSE EVERYTHING
# ==========================================================

cap.release()

cv2.destroyAllWindows()