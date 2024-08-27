import cv2 as cv
import mediapipe as mp
import serial
import time
import sys

arduino = serial.Serial("COM3", 9600) # replace COM3 with the path to your arduino
time.sleep(2)

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 600)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 500)

mp_hands = mp.solutions.hands
hand = mp_hands.Hands()

mp_drawing  = mp.solutions.drawing_utils

def count_fingers(landmarks):
    fingers = []
    
    if landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x < landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for tip_id in [mp_hands.HandLandmark.INDEX_FINGER_TIP, 
                   mp_hands.HandLandmark.MIDDLE_FINGER_TIP, 
                   mp_hands.HandLandmark.RING_FINGER_TIP, 
                   mp_hands.HandLandmark.PINKY_TIP]:
        if landmarks.landmark[tip_id].y < landmarks.landmark[tip_id - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers.count(1)

while True:
    success, frame = cap.read() 
    if success:
        RGB_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        result = hand.process(frame)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                #print(hand_landmarks)
                fingerCount = count_fingers(hand_landmarks)
                print(f'Fingers detected: {fingerCount}')
                arduino.write(f'{fingerCount}\n'.encode())
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        cv.imshow("Image Capture", frame)
        if cv.waitKey(1) == ord('q'):
            break

arduino.close()
cv.destroyAllWindows()
