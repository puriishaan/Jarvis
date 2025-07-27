#detects hand signal when called. Note imshow cannot be run in a function therefore camera not visible.

def run_hand_gesture_detection_and_output(output_queue):
    import cv2
    import mediapipe as mp
    import numpy as np
    import joblib

    clf = joblib.load("hand_gesture_model.pkl")
    le = joblib.load("label_encoder.pkl")

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    last_label = None
    cooldown = 20
    counter = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.extend([lm.x, lm.y, lm.z])

                if len(landmarks) == 63:
                    input_data = np.array(landmarks).reshape(1, -1)
                    probabilities = clf.predict_proba(input_data)[0]
                    predicted_index = np.argmax(probabilities)
                    predicted_label = le.inverse_transform([predicted_index])[0]
                    confidence = probabilities[predicted_index]

                    # 🧠 Only send command if label changed + cooldown passed
                    if confidence > 0.85 and predicted_label != last_label and counter == 0:
                        print(f"[HAND] Gesture Detected: {predicted_label} ({confidence:.2f})")
                        last_label = predicted_label
                        counter = cooldown

                        # 🖐️ Map hand gesture to ORGO command
                        gesture_to_command = {
                            "single_click": 'computer.prompt("single_click")',
                            "double_click": 'computer.prompt("double_click")',
                            "left_swipe": 'computer.prompt("swipe left")',
                            "right_swipe": 'computer.prompt("swipe right")',
                            "screenshot": 'computer.screenshot()'
                        }

                        if predicted_label in gesture_to_command:
                            output_queue.put(gesture_to_command[predicted_label])

                    if counter > 0:
                        counter -= 1

      #  cv2.imshow("Hand Gesture Recognition", frame)
       # if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

    cap.release()
    cv2.destroyAllWindows()
