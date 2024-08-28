import cv2 as cv
import mediapipe as mp
import serial
import time

arduino = serial.Serial("/dev/ttyACM0", 9600)  # Replace with your Arduino's port
time.sleep(2)

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 300)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 230)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

def count_fingers(landmarks):
    fingers = []
    
    # Thumb
    if landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x < landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for tip_id in [mp_hands.HandLandmark.INDEX_FINGER_TIP, 
                   mp_hands.HandLandmark.MIDDLE_FINGER_TIP, 
                   mp_hands.HandLandmark.RING_FINGER_TIP, 
                   mp_hands.HandLandmark.PINKY_TIP]:
        if landmarks.landmark[tip_id].y < landmarks.landmark[tip_id - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers.count(1)

previous_finger_count = -1

while True:
    success, frame = cap.read() 
    if success:
        RGB_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        result = hands.process(RGB_frame)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                finger_count = count_fingers(hand_landmarks)
                if finger_count != previous_finger_count:
                    print(f'Fingers detected: {finger_count}')
                    arduino.write(f'{finger_count}\n'.encode())
                    previous_finger_count = finger_count

                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv.imshow("Image Capture", frame)
        if cv.waitKey(1) == ord('q'):
            break

arduino.close()
cv.destroyAllWindows()
