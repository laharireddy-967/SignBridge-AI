import cv2
import mediapipe as mp
from gtts import gTTS
import speech_recognition as sr
from playsound import playsound
import threading
import os
import time

language="en"

translations={
"HELLO":"Hello",
"PEACE":"Thank you",
"ONE":"Please wait",
"FIST":"I agree",
"THUMBS UP":"Good job",
"CALL ME":"Call me",
"HELP":"Emergency! I need help"
}

display_text=""
sign_output=""
typed_text=""
typing_mode=False
sign_image=None

# ---------- TEXT TO SPEECH ----------
def speak(text):
    filename=f"voice_{time.time()}.mp3"
    tts=gTTS(text=text,lang=language)
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

# ---------- LOAD SIGN IMAGE ----------  
#def load_sign_image(word):
    global sign_image

    filename=word.lower().strip()
    img_path=os.path.join("signs",filename+".jpeg")

    if os.path.exists(img_path):
        sign_image=cv2.imread(img_path)
    else:
        sign_image=None
def load_sign_image(word):

    global sign_image

    filename = word.lower().strip()

    extensions = [".jpg", ".jpeg", ".png"]

    sign_image = None

    for ext in extensions:

        path = os.path.join("signs", filename + ext)

        if os.path.exists(path):

            sign_image = cv2.imread(path)

            print("Loaded:", path)

            break

    if sign_image is None:

        print("Image not found for:", filename)
# ---------- SPEECH TO TEXT ----------
def speech_to_text():
    global display_text,sign_output

    r=sr.Recognizer()

    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio=r.listen(source)

        text=r.recognize_google(audio)

        display_text=text.upper()
        sign_output=text.upper()

        load_sign_image(text)

    except:
        display_text="Speech not recognised"

# ---------- MEDIAPIPE ----------
mp_hands=mp.solutions.hands
hands=mp_hands.Hands(max_num_hands=1)
mp_draw=mp.solutions.drawing_utils

cap=cv2.VideoCapture(0)

current_gesture=""
stable_count=0
confirmed_gesture=""

while True:

    success,img=cap.read()
    if not success:
        break

    img=cv2.flip(img,1)
    imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    results=hands.process(imgRGB)

    gesture=""

    if results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(img,hand,mp_hands.HAND_CONNECTIONS)

            h,w,_=img.shape
            lm=[]

            for point in hand.landmark:
                lm.append((int(point.x*w),int(point.y*h)))

            tips=[8,12,16,20]
            fingers=[]

            for tip in tips:
                if lm[tip][1]<lm[tip-2][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            thumb_up=lm[4][1]<lm[3][1]
            pinky_up=lm[20][1]<lm[18][1]

            if thumb_up and fingers==[0,0,0,0]:
                gesture="THUMBS UP"

            elif thumb_up and pinky_up and fingers[0:3]==[0,0,0]:
                gesture="CALL ME"

            elif fingers==[1,1,1,1] and not thumb_up:
                gesture="HELLO"

            elif fingers==[1,1,0,0]:
                gesture="PEACE"

            elif fingers==[1,0,0,0]:
                gesture="ONE"

            elif not thumb_up and fingers==[0,0,0,0]:
                gesture="FIST"

            elif fingers==[1,0,1,0]:
                gesture="HELP"

    if gesture==current_gesture and gesture!="":
        stable_count+=1
    else:
        stable_count=0
        current_gesture=gesture

    if stable_count==6:

        confirmed_gesture=gesture

        if confirmed_gesture in translations:

            display_text=translations[confirmed_gesture]
            sign_output=confirmed_gesture

            load_sign_image(confirmed_gesture)

            threading.Thread(target=speak,args=(display_text,)).start()

    # ---------- UI ----------
    cv2.putText(img,"SignBridge AI",(20,40),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)

    cv2.putText(img,"T:Type  M:Speech  Q:Quit",(20,80),
                cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

    if sign_output!="":

        color=(0,0,255) if sign_output=="HELP" else (0,255,0)

        cv2.putText(img,"SIGN:",(40,200),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)

        cv2.putText(img,sign_output,(40,240),
                    cv2.FONT_HERSHEY_SIMPLEX,1.5,color,3)

    if display_text!="":

        cv2.putText(img,"MESSAGE:",(40,320),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)

        cv2.putText(img,display_text,(40,360),
                    cv2.FONT_HERSHEY_SIMPLEX,1.2,(255,255,0),3)

    if sign_image is not None:

        resized=cv2.resize(sign_image,(200,200))
        img[200:400,600:800]=resized

    if typing_mode:

        cv2.putText(img,"Typing: "+typed_text,(40,450),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)

    cv2.imshow("SignBridge AI",img)

    key=cv2.waitKey(1)&0xFF

    if key==ord('q'):
        break

    elif key==ord('m'):
        threading.Thread(target=speech_to_text).start()

    elif key==ord('t'):
        typing_mode=True
        typed_text=""

    elif typing_mode:

        if key==13:

            sign_output=typed_text.upper()
            display_text=typed_text.upper()

            load_sign_image(typed_text)

            typing_mode=False

        elif key==8:
            typed_text=typed_text[:-1]

        elif 32<=key<=126:
            typed_text+=chr(key)

cap.release()
cv2.destroyAllWindows()