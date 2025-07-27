import os
import openai
import json
import speech_recognition as sr
from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.environ["OPEN_AI_KEY"])

# History management
def load_history(filename="chat_history.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []

def save_history(history, filename="chat_history.json"):
    with open(filename, "w") as f:
        json.dump(history, f, indent=2)

chat_history = load_history()
if not chat_history:
    chat_history.append({
        "role": "system",
        "content": """You are an AI assistant that takes on the personality of JARVIS from Iron Man.

You are operating within Orgo, an application that allows users to interact with an Ubuntu desktop using only AI. Normally, users type prompts, but you will enhance this with a natural language layer.

Your Task:
When a user sends a prompt, you must:

1. Separate the prompt into two parts:
   - Conversational: What the user is saying casually or socially (e.g., greetings, comments).
   - System Instructions: What they actually want the system to do.

Example:
Input: "Hey, it’s such a lovely day! Please open Firefox."
- Conversational part: "Hey, it’s such a lovely day!"
- System instruction: "Please open Firefox."

You must always respond using this exact JSON structure — nothing more, nothing less:

{
  "text": "string",
  "apps": "string",
  "instructions": "string"
}

Output Rules:
- "text": Respond as JARVIS would — classy, formal, and efficient — only to the conversational portion.
- "apps": List all apps that were opened in this request (e.g., "firefox"). If no app is opened, use an empty string.
- "instructions": For all system commands, return them in this format:

computer.prompt("open Firefox")

These should be:
- Put in an array
- Concise (don’t ramble)
- If an app is already open, do not re-open it. Instead, say: "using the existing open app" in the instruction.

If there are multiple steps, give multiple computer.prompt("command") instructions

Do not respond with anything outside the JSON object above."""
    })

# Voice input handler
def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak now...")
        audio = r.listen(source, timeout=5)
    try:
        text = r.recognize_google(audio)
        print("🧑 You (spoken):", text)
        return text
    except sr.UnknownValueError:
        print("⚠️ Couldn't understand. Try again.")
        return None
    except sr.RequestError:
        print("❌ Speech recognition API error.")
        return None

# Run one JARVIS interaction
def run_jarvis_once():
    user_input = get_voice_input()
    if user_input is None:
        return None, None

    chat_history.append({"role": "user", "content": user_input})
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=chat_history
        )
        reply = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": reply})
        save_history(chat_history)
        return user_input, reply
    except Exception as e:
        print("❌ Error:", e)
        return user_input, None
