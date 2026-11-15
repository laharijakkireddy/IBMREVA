"""app.py - the Streamlit screen. Run with:  streamlit run app.py"""

import streamlit as st

from orchestrator import MODEL_NAME, ask_agent, create_chat

st.set_page_config(page_title="Campus Career Companion", page_icon="🎓", layout="wide")

DEMO_PROFILE = (
    "I know Python and Excel and a little SQL. I am a 3rd year student. "
    "I can study 5 hours per week."
)
DEMO_JOB = (
    "Data Analyst Intern: needs Python, SQL, Excel, Data Visualisation "
    "(Power BI or Tableau), Statistics and good communication skills."
)

# Streamlit re-runs this file on every click, so we keep things in session_state.
if "chat" not in st.session_state:
    st.session_state.chat = None
    st.session_state.messages = []  # each: {"role", "text", "tools"}
    st.session_state.profile = ""
    st.session_state.job = ""


def send(text: str):
    """Send text to the agent and store both sides in the history."""
    st.session_state.messages.append({"role": "user", "text": text, "tools": []})
    try:
        if st.session_state.chat is None:
            st.session_state.chat = create_chat()
        answer, tools = ask_agent(st.session_state.chat, text)
    except Exception as exc:  # show a friendly message, not a stack trace
        answer, tools = f"Sorry Junior, my brain had a problem: {type(exc).__name__}: {str(exc)[:200]}", []
    st.session_state.messages.append({"role": "assistant", "text": answer, "tools": tools})


def fill_demo():
    st.session_state.profile = DEMO_PROFILE
    st.session_state.job = DEMO_JOB


with st.sidebar:
    st.header("🎓 Your details")
    st.caption(f"Brain: `{MODEL_NAME}`")
    st.button("Auto-fill demo scenario", on_click=fill_demo)
    profile = st.text_area("Your skills & weekly hours", key="profile", height=140)
    job = st.text_area("Job description", key="job", height=140)
    if st.button("🚀 Generate my 2-week plan", type="primary"):
        if profile.strip() and job.strip():
            with st.spinner("Senior is thinking and using tools..."):
                send(f"My profile:\n{profile}\n\nTarget job description:\n{job}\n\n"
                     "Please analyse the gap and build my plan.")
        else:
            st.warning("Please fill both boxes first.")
    if st.button("Start over"):
        st.session_state.chat = None
        st.session_state.messages = []
        st.rerun()

st.title("🎓 Campus Career Companion")
st.caption("Your friendly placement senior, powered by an AI agent with tools.")

if not st.session_state.messages:
    st.info("Fill the sidebar and click **Generate my 2-week plan**, or just chat below.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["tools"]:
            with st.expander(f"🔧 Agent used {len(msg['tools'])} tool call(s) (click to see)"):
                for call in msg["tools"]:
                    st.code(f"{call['tool']}({call['args']})", language="python")
        st.markdown(msg["text"])

if prompt := st.chat_input("Ask your senior... (try asking about biryani!)"):
    with st.spinner("Senior is thinking..."):
        send(prompt)
    st.rerun()
