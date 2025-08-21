#!/usr/bin/env python3

import json
import logging
import os
from typing import Dict, Generator, List, Optional, Tuple

import gradio as gr
import httpx
from yarl import URL

log = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Config Options
# -----------------------------------------------------------------------------

LLM_BASE_URL = URL(os.getenv("LLM_BASE_URL", "http://localhost:8080"))
GRADIO_PORT = int(os.getenv("GRADIO_PORT", "7860"))

# -----------------------------------------------------------------------------
# Model helpers (lazy)
# -----------------------------------------------------------------------------

LLM_MODELS_ENDPOINT = LLM_BASE_URL / "openai/v1/models"


def fetch_models() -> Tuple[List[str], Optional[str]]:
    """Fetches available model IDs from the LLM endpoint.

    Performs an HTTP GET request to the models endpoint to retrieve a list of
    all available models. It handles network errors and unexpected API
    responses gracefully by logging the error.

    Returns:
        Tuple[List[str], Optional[str]]: A tuple containing:
            - A list of model ID strings.
            - The ID of the default model (the first in the list), or None if
              no models are found or an error occurs.
    """
    try:
        r = httpx.get(str(LLM_MODELS_ENDPOINT), timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception:
        log.error(f"Failed to fetch models from {LLM_MODELS_ENDPOINT}", exc_info=True)
        return [], None

    choices = [model["id"] for model in data.get("data", []) if "id" in model]

    default = choices[0] if choices else None

    return choices, default


# -----------------------------------------------------------------------------
# Streaming
# -----------------------------------------------------------------------------

LLM_CHAT_COMPLETIONS_ENDPOINT = LLM_BASE_URL / "openai/v1/chat/completions"


def stream_chat(
    question: str,
    chat_history: List[Dict[str, str]],
    model_choice: Optional[str],
) -> Generator[str, None, None]:
    """
    Streams a chat response from an OpenAI-compatible chat completions endpoint.

    Args:
        question: The latest user question to send.
        chat_history: A list of previous messages in the conversation.
        model_choice: The specific model to use for the completion.

    Yields:
        str: A stream of response tokens from the model or an error message.
    """
    # 1. Check if a model was selected in the UI.
    if not model_choice:
        yield "⚠️ **Error:** Please select a model from the dropdown menu first."
        return

    messages = chat_history + [{"role": "user", "content": question}]

    # 2. The fallback to a default model is removed.
    payload = {
        "model": model_choice,
        "messages": messages,
        "stream": True,
    }

    try:
        with httpx.stream(
            "POST", str(LLM_CHAT_COMPLETIONS_ENDPOINT), json=payload, timeout=None
        ) as r:
            r.raise_for_status()
            for raw_chunk in r.iter_lines():
                if not raw_chunk.startswith("data: "):
                    continue

                data_str = raw_chunk[6:]
                if data_str.strip() == "[DONE]":
                    break

                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    token = delta.get("content")
                    if token:
                        yield token
                except (json.JSONDecodeError, IndexError, KeyError):
                    continue
    except httpx.HTTPStatusError as e:
        error_text = f"HTTP error occurred: {e.response.status_code}"
        log.error(f"{error_text} - {e.response.text}")
        yield f"⚠️ **Error:** {error_text}. Please check the logs for details."
    except Exception as e:
        log.error(f"An unexpected error occurred during streaming: {e}", exc_info=True)
        yield "⚠️ **Error:** An unexpected error occurred. Please check the logs."


# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------


def respond(
    message: str, chat_history: List[Dict[str, str]], model_choice: str
) -> Generator[Tuple[List[Dict[str, str]], str], None, None]:
    """Handles user input and streams the bot's response to the Gradio UI.

    This generator function is a Gradio callback that orchestrates the chat
    response. It takes the user's message, calls the `stream_chat` function,
    and continuously yields updates to the chatbot and input textbox components.

    Args:
        message: The user's input from the textbox.
        chat_history: The current conversation history from the chatbot component.
        model_choice: The model selected in the UI's dropdown.

    Yields:
        A tuple containing the updated chat history for the chatbot and an
        empty string to clear the user's input textbox.
    """
    bot_stream = stream_chat(message, chat_history, model_choice)

    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": ""})
    yield chat_history, ""

    buffer = ""
    for token in bot_stream:
        buffer += token
        chat_history[-1]["content"] = buffer
        yield chat_history, ""


def refresh_dropdown():
    """Fetches the model list and updates the Gradio dropdown component.

    This callback calls the `fetch_models` helper to get available models
    from the backend. It then returns a Gradio update object to populate the
    dropdown. If the backend is unreachable, it updates the dropdown to show
    an error state and disables it.

    Returns:
        A gr.update object that configures the dropdown component's choices,
        default value, and interactivity.
    """
    choices, default = fetch_models()
    if not choices:
        return gr.update(
            choices=["⚠️ backend unreachable"], value=None, interactive=False
        )
    return gr.update(choices=choices, value=default, interactive=True)


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------
with gr.Blocks(title="RAG-LLM Chatbot", theme="soft") as demo:
    gr.Markdown(
        """
        # RAG-LLM Chatbot
        _A simple frontend to demonstrate RAG-LLM queries._
        """
    )

    with gr.Row():
        model_sel = gr.Dropdown(label="Model", interactive=True, scale=5)
        refresh_btn = gr.Button("⟳", variant="secondary", scale=1)

    chatbot = gr.Chatbot(
        label="Conversation", height=500, show_copy_button=True, type="messages"
    )

    with gr.Row():
        msg = gr.Textbox(
            placeholder="Awaiting user input...",
            lines=1,
            autofocus=True,
            show_label=False,
            container=False,
        )
        send_btn = gr.Button("Send", variant="primary")

    clear_btn = gr.Button("Clear chat")

    # Events
    demo.load(refresh_dropdown, None, model_sel)
    refresh_btn.click(refresh_dropdown, None, model_sel)

    for trg in (msg.submit, send_btn.click):
        trg(respond, inputs=[msg, chatbot, model_sel], outputs=[chatbot, msg])

    clear_btn.click(lambda: ([], ""), None, [chatbot, msg], queue=False)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    demo.launch(server_name="0.0.0.0", server_port=GRADIO_PORT)
