#Collecting different hand signal data to later train the model 

import cv2
import mediapipe as mp
import csv
import time

mp_hands = mp.solutions.hands #Using the google mediapipe library to give references to different parts of the hand
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

label = input("Enter label for this gesture: ")  # e.g. thumbs_up
output_file = open(f"{label}.csv", mode="w", newline="")
csv_writer = csv.writer(output_file)

print("Starting data collection. Press 's' to save frame, 'q' to quit.")
while True:
    ret, frame = cap.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            # Press 's' to save the frame's data
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                csv_writer.writerow(landmarks + [label])
                print("Saved frame.")
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    cv2.imshow("Collect", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

output_file.close()
cap.release()
cv2.destroyAllWindows()
