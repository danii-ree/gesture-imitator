import cv2 as cv
import mediapipe as mp
import serial
import time

arduino = serial.Serial("COM3", 9600)  # Replace with your Arduino's port
time.sleep(2)

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 300)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 230)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

def findPosition(img, handNo = 0, draw = True) :
    PosList = []
    if result.multi_hand_landmarks :
        myHand = result.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            PosList.append([id, cx, cy])
                
        if draw :
            cv2.circle(img, (cx,cy), 10, (255,255,255), cv2.FILLED)
            
        return PosList

def count_fingers(landmarkList):
    fingers = []
    tipIds = [4, 8, 12, 16, 20]

    if len(landmarkList) != 0:
       # Thumb detection
       if landmarkList[tipIds[0]][1] > landmarkList[tipIds[0] - 1][1]:
           fingers.append(1)
       else:
           fingers.append(0)
      
       # 4 Fingers
       for id in range (1, 5):
            if landmarkList[tipIds[id]][2] < landmarkList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

       total_fingers = fingers.count(1)
       print(total_fingers)
       # arduino.write(f'{total_fingers}\n'.encode())

previous_finger_count = -1

while True:
    success, frame = cap.read() 
    if success:
        RGB_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        result = hands.process(RGB_frame)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                lmList = findPosition(frame, draw=False)
                count_fingers(lmList)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv.imshow("Image Capture", frame)
        if cv.waitKey(1) == ord('q'):
            break

#arduino.close()
cv.destroyAllWindows()
