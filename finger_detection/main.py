import cv2 as cv
import mediapipe as mp
import serial
import time

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
def detect_thumb_fold(pos_list):
    """Detects if the thumb is folded based on landmark positions."""
    if len(pos_list) >= 5:
        thumb_tip = pos_list[4][2]
        thumb_base = pos_list[3][2]
        thumb_tip_x = pos_list[4][1]
        thumb_base_x = pos_list[3][1]

        # Thumb fold thresholds
        fold_threshold_x = 20
        fold_threshold_y = 15

        # Check if the thumb is folded into the palm
        thumb_folded = (abs(thumb_tip_x - thumb_base_x) < fold_threshold_x) and (abs(thumb_tip - thumb_base) < fold_threshold_y)
        return thumb_folded
    return False
def count_fingers(landmarkList):
    fingers = []
    tipIds = [4, 8, 12, 16, 20]

    if len(landmarkList) != 0:        # Detect thumb folding
        thumb_folded = detect_thumb_fold(pos_list)

        # Thumb detection
        thumb_tip_y = pos_list[4][2]
        thumb_base_y = pos_list[3][2]
        thumb_tip_x = pos_list[4][1]
        thumb_base_x = pos_list[3][1]

        # Determine hand orientation
        hand_orientation = 'front' if thumb_tip_x < pos_list[8][1] else 'back'

        if thumb_folded:
            finger_count = 0  # Thumb is folded, don't count it
        else:
            # Count thumb based on hand orientation
            if hand_orientation == 'front':
                if thumb_tip_x < thumb_base_x:
                    fingers.append(1)  # Thumb extended
                else:
                    fingers.append(0)
            elif hand_orientation == 'back':
                if thumb_tip_x > thumb_base_x:
                    fingers.append(1)  # Thumb extended
                else:
                    fingers.append(0)

        # Count extended fingers
        for i in range(1, 5):
            if pos_list[tip_ids[i]][2] < pos_list[tip_ids[i] - 2][2]:
                fingers.append(1)  # Finger extended
            else:
                fingers.append(0)

        return fingers.count(1)
    return 0

while True:
        success, frame = cap.read()  # Capture a frame from the webcam
        if not success:
            print("Failed to capture image")
            break

        # Convert the image to RGB for MediaPipe processing
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        # Detect hand landmarks and count fingers
        if result.multi_hand_landmarks:
            pos_list = find_position(frame, result)
            finger_count = count_fingers(pos_list)

            # Draw hand landmarks on the frame
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Send data to Arduino only if the finger count changes
            if finger_count != previous_finger_count:
                print(f"Fingers Detected: {finger_count}")
                arduino.write(f"{finger_count}\n".encode())  # Send finger count to Arduino
                previous_finger_count = finger_count

        # Show the frame with hand landmarks drawn
        cv.imshow("Hand Detection", frame)

        # Exit the loop if 'q' is pressed
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv.destroyAllWindows()
arduino.close()

