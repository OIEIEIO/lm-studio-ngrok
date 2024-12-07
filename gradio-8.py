import gradio as gr
import requests
import json
import pickle
import os

# Configuration
CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "BASE_URL": "http://127.0.0.1:1234/v1",
            "DEFAULT_MODEL_ID": "Qwen2.5-Coder-14B-Instruct-GGUF",
            "AVAILABLE_MODELS": ["Qwen2.5-Coder-14B-Instruct-GGUF"]
        }
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

config = load_config()
BASE_URL = config["BASE_URL"]
DEFAULT_MODEL_ID = config["DEFAULT_MODEL_ID"]
AVAILABLE_MODELS = config.get("AVAILABLE_MODELS", [DEFAULT_MODEL_ID])

# Global conversation history
conversation_history = []

# Chat function
def chat_with_model(user_message, selected_model):
    global conversation_history
    url = f"{BASE_URL}/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": user_message})
    payload = {
        "model": selected_model,
        "messages": conversation_history
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            assistant_message = response_data["choices"][0]["message"]["content"]
            conversation_history.append({"role": "assistant", "content": assistant_message})
            return format_conversation(conversation_history)
        else:
            return f"Error {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {e}"

# Clear conversation
def clear_conversation():
    global conversation_history
    conversation_history = []
    return "Conversation cleared."

# Save conversation with feedback
def save_conversation(file_format):
    global conversation_history
    file_name = f"conversation.{file_format}"
    try:
        if file_format == "pkl":
            with open(file_name, "wb") as file:
                pickle.dump(conversation_history, file)
        elif file_format == "json":
            with open(file_name, "w") as file:
                json.dump(conversation_history, file, indent=4)
        elif file_format == "txt":
            with open(file_name, "w") as file:
                for msg in conversation_history:
                    file.write(f"{msg['role']}: {msg['content']}\n")
        return f"Conversation saved as {file_name}."
    except Exception as e:
        return f"Failed to save conversation: {e}"

# Format conversation for Markdown display
def format_conversation(history):
    formatted = ""
    for msg in history:
        role = "**User:**" if msg["role"] == "user" else "**Assistant:**"
        formatted += f"{role} {msg['content']}\n\n"
    return formatted

# Layout for Gradio UI
with gr.Blocks() as app:
    with gr.Tab("Chat"):
        gr.Markdown("# Chat with Qwen Model")
        conversation_display = gr.Markdown(label="Conversation History")  # Updated to use Markdown
        user_message = gr.Textbox(label="Your Message", placeholder="Type your message here...")
        model_selector = gr.Dropdown(choices=AVAILABLE_MODELS, value=DEFAULT_MODEL_ID, label="Select Model")
        with gr.Row():
            submit_button = gr.Button("Submit")
            clear_button = gr.Button("Clear Conversation")
            save_pkl_button = gr.Button("Save as PKL")
            save_json_button = gr.Button("Save as JSON")
            save_txt_button = gr.Button("Save as TXT")
        
        # Link functions
        submit_button.click(chat_with_model, [user_message, model_selector], conversation_display)
        clear_button.click(clear_conversation, [], conversation_display)
        save_pkl_button.click(lambda: save_conversation("pkl"), inputs=[], outputs=conversation_display)
        save_json_button.click(lambda: save_conversation("json"), inputs=[], outputs=conversation_display)
        save_txt_button.click(lambda: save_conversation("txt"), inputs=[], outputs=conversation_display)

    with gr.Tab("Tools"):
        gr.Markdown("# System Tools")
        gr.Markdown("Perform system checks or interact with external APIs.")
        tool_output = gr.Textbox(label="Tool Output", lines=10, interactive=False)
        with gr.Row():
            tool_button_1 = gr.Button("Check System Time")
            tool_button_2 = gr.Button("Get Disk Space")
        
        # Placeholder tool functions
        tool_button_1.click(lambda: "System time: Not implemented yet", [], tool_output)
        tool_button_2.click(lambda: "Disk space: Not implemented yet", [], tool_output)

    with gr.Tab("Settings"):
        gr.Markdown("# Settings")
        gr.Markdown("Configure application settings here.")
        with gr.Row():
            theme_toggle = gr.Button("Toggle Theme (Dark/Light)")

# Launch the app
if __name__ == "__main__":
    app.launch()
