import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
import requests
import os
import subprocess
from dotenv import load_dotenv
load_dotenv()


is_talking = threading.Event()

# Global GUI variables
root = None
canvas = None
face_item = None
robot_closed_img = None
robot_open_img = None

def start_gui():
    global root, canvas, face_item, robot_closed_img, robot_open_img

    root = tk.Tk()
    root.title("JARVIS")

    robot_closed = Image.open("jarvis_mouth_closed.png").resize((300, 300))
    robot_open = Image.open("jarvis_mouth_open.png").resize((300, 300))

    robot_closed_img = ImageTk.PhotoImage(robot_closed)
    robot_open_img = ImageTk.PhotoImage(robot_open)

    canvas = tk.Canvas(root, width=300, height=300)
    canvas.pack()
    face_item = canvas.create_image(0, 0, anchor='nw', image=robot_closed_img)

    root.mainloop()  # Starts the GUI (blocking)

def animate_mouth():
    while is_talking.is_set():
        canvas.itemconfig(face_item, image=robot_open_img)
        time.sleep(0.1)
        canvas.itemconfig(face_item, image=robot_closed_img)
        time.sleep(0.1)

def speak_text(text):
    def _run():
        is_talking.set()
        threading.Thread(target=animate_mouth).start()

        response = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers={
                "api-key": os.environ["MURF_KEY"]
            },
            json={
                "text": text,
                "voiceId": "en-US-Marcus"
            }
        )

        audio_url = response.json()['audioFile']
        audio_data = requests.get(audio_url)

        with open("output.wav", "wb") as f:
            f.write(audio_data.content)

        subprocess.run(["afplay", "output.wav"])
        is_talking.clear()

    threading.Thread(target=_run).start()
