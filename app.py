import os

import streamlit as st
from openai import OpenAIError

from agent import SchedulingAgent
from evaluator import evaluate_transcript
from run_loop import SCENARIOS, run_simulation
from tools import AppointmentScheduler


def get_setting(name, default=None):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except FileNotFoundError:
        return os.getenv(name, default)


st.set_page_config(
    page_title="Apointment Scheduling Assistant",
    page_icon="🗓️",
    layout="centered",
)
st.title("Apointment Scheduling Assistant")
st.caption(
    "Interactive POC using sample appointment data. Do not enter real or "
    "sensitive medical information; this assistant is not a substitute for "
    "professional medical care."
)

api_key = get_setting("OPENAI_API_KEY")
if not api_key:
    st.error(
        "OpenAI API key is not configured. Add OPENAI_API_KEY to your local "
        ".env file or to the app's Streamlit Secrets."
    )
    st.stop()

model_name = get_setting("OPENAI_MODEL", "gpt-4o-mini")

if st.sidebar.button("Start new conversation"):
    st.session_state.pop("assistant", None)
    st.session_state.pop("chat_history", None)
    st.rerun()

if "assistant" not in st.session_state:
    scheduler = AppointmentScheduler()
    st.session_state.assistant = SchedulingAgent(
        api_key=api_key,
        model_name=model_name,
        scheduler=scheduler,
    )
    st.session_state.chat_history = []

st.sidebar.caption(
    "Each browser session has its own conversation and sample booking schedule."
)
st.sidebar.caption(f"Model: {model_name}")

st.subheader("Watch the automated scenarios")
st.caption(
    "The patient simulator and assistant will converse automatically. "
    "This runs all three scenarios and makes OpenAI API calls."
)

if st.button("Run all scenarios", type="primary"):
    for scenario in SCENARIOS:
        with st.expander(scenario["name"], expanded=True):
            conversation = st.container()
            status = st.empty()

            def show_message(role, content):
                if role == "system":
                    status.info(content)
                    return
                speaker = "Patient" if role == "user" else "Assistant"
                with conversation.chat_message(speaker):
                    st.markdown(f"**{speaker}**")
                    st.markdown(content)

            try:
                transcript = run_simulation(
                    scenario,
                    on_message=show_message,
                    sleep_seconds=1,
                    scheduler=AppointmentScheduler(),
                )
                result = evaluate_transcript(
                    transcript,
                    scenario["success_criteria"],
                    api_key=api_key,
                    model_name=model_name,
                )
            except OpenAIError as error:
                st.error(f"The OpenAI request failed: {error}")
                break
            else:
                if result["passed"]:
                    status.success(f"Passed: {result['reason']}")
                else:
                    status.error(f"Failed: {result['reason']}")

st.divider()
st.subheader("Chat with the assistant")
st.caption("Or use the chat below to try the scheduling assistant yourself.")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message the scheduling assistant"):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = st.session_state.assistant.chat(prompt)
            except OpenAIError as error:
                st.error(f"The OpenAI request failed: {error}")
            else:
                st.markdown(reply)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": reply}
                )
