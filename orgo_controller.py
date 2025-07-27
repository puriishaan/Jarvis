from orgo import Computer
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch required keys
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
orgo_api_key = os.environ.get("ORGO_API_KEY")
project_id = os.environ.get("PROJECT_ID")

# Setting Anthropic key for orgo client 
os.environ["ANTHROPIC_API_KEY"] = anthropic_key

# Initialize Orgo computer client
computer = Computer(
    project_id=project_id,
    api_key=orgo_api_key
)

def send_prompt_to_computer(prompt: str):
    try:
        print(f"[ORGO] Executing: {prompt}")
        
        if prompt.startswith("computer.prompt"):
            # Extract command from: computer.prompt("...")
            start = prompt.find("(") + 1
            end = prompt.rfind(")")
            command = eval(prompt[start:end])  # Assumes this is a clean string literal
            computer.prompt(command)
        
        elif prompt.startswith("computer.screenshot"):
            computer.screenshot()

        else:
            print(f"[ORGO] Unknown instruction format: {prompt}")

    except Exception as e:
        print(f"[ORGO ERROR] Failed to execute prompt: {e}")
