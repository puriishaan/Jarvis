import threading
import queue
import time
from jarvis import run_jarvis_once
from talking_robot import start_gui
from orgo_controller import send_prompt_to_computer
from talking_robot import speak_text
from hand_signal_detector import run_hand_gesture_detection_and_output

# Shared Queues
gpt_to_tts_q = queue.Queue()
gpt_to_orgo_q = queue.Queue()
hand_to_orgo_q = queue.Queue()

# ----- THREAD: Voice Input + GPT Handler -----
def jarvis_loop():
    while True:
        user_input, json_reply = run_jarvis_once()
        if json_reply:
            try:
                parsed = eval(json_reply)  # Trust only if prompt guarantees clean JSON
                if "text" in parsed:
                    gpt_to_tts_q.put(parsed["text"])
                if "instructions" in parsed and isinstance(parsed["instructions"], list):
                    for instruction in parsed["instructions"]:
                        gpt_to_orgo_q.put(instruction)
            except Exception as e:
                print("❌ Parsing error:", e)
        time.sleep(0.5)



# ----- THREAD: TTS Output -----
def tts_loop():
    while True:
        if not gpt_to_tts_q.empty():
            speak_text(gpt_to_tts_q.get())
        time.sleep(0.1)

# ----- THREAD: ORGO Controller Sender (for GPT) -----
def orgo_from_gpt_loop():
    while True:
        if not gpt_to_orgo_q.empty():
            send_prompt_to_computer(gpt_to_orgo_q.get())
        time.sleep(0.1)

# ----- THREAD: ORGO Controller Sender (for Hand Signals) -----
def orgo_from_hand_loop():
    while True:
        if not hand_to_orgo_q.empty():
            send_prompt_to_computer(hand_to_orgo_q.get())
        time.sleep(0.1)

if __name__ == '__main__':
    # Start threaded subsystems
    threading.Thread(target=jarvis_loop, daemon=True).start()
    threading.Thread(target=tts_loop, daemon=True).start()
    threading.Thread(target=orgo_from_gpt_loop, daemon=True).start()
    threading.Thread(target=orgo_from_hand_loop, daemon=True).start()
    threading.Thread(target=run_hand_gesture_detection_and_output, args=(hand_to_orgo_q,), daemon=True).start()

    # GUI must stay in the main thread
    start_gui()
