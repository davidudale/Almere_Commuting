# app.py

import streamlit as st
import pandas as pd
import os
from src.recommendation_engine import load_commuter_data, get_commuter_profile, generate_recommendations
from src.agent_simulation import run_crowding_simulation
from src.chatbot_logic import Chatbot

# --- Configuration ---
DATA_FILEPATH = os.path.join(os.path.dirname(__file__), 'data', 'commuter_data.csv')
DEFAULT_PT_CAPACITY = 10 # Adjust this for simulation sensitivity
NUM_SIM_STEPS = 5 # Number of simulation steps for crowding insights


# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "commuter_profile" not in st.session_state:
    st.session_state.commuter_profile = None
if "crowding_insights" not in st.session_state:
    st.session_state.crowding_insights = None
if "chatbot" not in st.session_state:
    # Safely get API key from Streamlit secrets
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    st.session_state.chatbot = Chatbot(gemini_api_key)

# --- Load Data ---
@st.cache_data
def get_commuter_df():
    """Loads commuter data and caches it."""
    return load_commuter_data(DATA_FILEPATH)

commuter_df = get_commuter_df()

# --- Streamlit UI ---
st.set_page_config(page_title="Commute AI Assistant", layout="centered")

st.title("🚶‍♂️🚌🚗 Commute AI Assistant")
st.markdown(
    """
    Hello! I'm your personalized commuting assistant.
    I can provide recommendations based on your behavioral profile and even give insights into public transport crowding.
    """
)

# --- Commuter Profile Selection ---
st.sidebar.header("Select Your Commuter Profile")
if not commuter_df.empty:
    commuter_ids = commuter_df['CommuterID'].tolist()
    selected_commuter_id = st.sidebar.selectbox(
        "Choose a Commuter ID to load their profile:",
        options=[None] + commuter_ids, # Add None option
        format_func=lambda x: "Select a profile..." if x is None else f"Commuter ID: {x}"
    )

    if selected_commuter_id and st.session_state.commuter_profile is None or \
       (selected_commuter_id and st.session_state.commuter_profile and st.session_state.commuter_profile['CommuterID'] != selected_commuter_id):
        st.session_state.commuter_profile = get_commuter_profile(selected_commuter_id, commuter_df)
        st.session_state.messages.append({"role": "assistant", "content": f"Profile for Commuter ID {selected_commuter_id} loaded. How can I help you with your commute today?"})
        # Run simulation for insights when a new profile is selected
        st.session_state.crowding_insights = run_crowding_simulation(commuter_df, pt_capacity=DEFAULT_PT_CAPACITY, num_sim_steps=NUM_SIM_STEPS)
        st.sidebar.success(f"Profile {selected_commuter_id} loaded and crowding simulation run!")
    elif selected_commuter_id is None and st.session_state.commuter_profile is not None:
        st.session_state.commuter_profile = None
        st.session_state.crowding_insights = None
        st.session_state.messages.append({"role": "assistant", "content": "Commuter profile cleared. Please select a profile to get personalized recommendations."})
        st.sidebar.info("No profile selected.")

    if st.session_state.commuter_profile:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Current Profile Details:")
        st.sidebar.write(f"**ID:** {st.session_state.commuter_profile.get('CommuterID', 'N/A')}")
        st.sidebar.write(f"**Usual Mode:** {st.session_state.commuter_profile.get('UsualCommuteMode', 'N/A')}")
        st.sidebar.write(f"**Attitude PT:** {st.session_state.commuter_profile.get('Attitude_PT_Score', 'N/A')}")
        st.sidebar.write(f"**PBC PT:** {st.session_state.commuter_profile.get('PBC_PT_Score', 'N/A')}")
        # Display crowding insights if available
        if st.session_state.crowding_insights:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Simulation Insights:")
            st.sidebar.write(f"Avg PT Crowding: {st.session_state.crowding_insights['average_pt_crowding']:.0%}")
            st.sidebar.write(f"Switches from PT: {st.session_state.crowding_insights['total_mode_switches_from_pt']}")
            st.sidebar.caption(f"(Simulated with PT capacity: {st.session_state.crowding_insights['simulated_pt_capacity']})")
else:
    st.error("Could not load commuter data. Please ensure 'data/commuter_data.csv' exists.")


# --- Chat Interface ---
st.subheader("Chat with the Assistant")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How can I help you with your commute?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_content = ""
            if st.session_state.commuter_profile:
                # First, try to get a personalized recommendation
                if "recommend" in prompt.lower() or "advice" in prompt.lower() or "suggest" in prompt.lower():
                    recommendations = generate_recommendations(
                        st.session_state.commuter_profile,
                        st.session_state.crowding_insights
                    )
                    response_content = "Here are some personalized recommendations based on your profile:\n\n" + \
                                       "\n".join([f"- {rec}" for rec in recommendations])
                else:
                    # If not explicitly asking for recommendations, use general chatbot
                    response_content = st.session_state.chatbot.get_chat_response(prompt)
            else:
                response_content = "Please select a commuter profile from the sidebar to get personalized recommendations."
                # Still allow general chat if no profile is selected
                if "profile" not in prompt.lower(): # Avoid infinite loop if user asks about profile
                     response_content = st.session_state.chatbot.get_chat_response(prompt)


            st.markdown(response_content)
            st.session_state.messages.append({"role": "assistant", "content": response_content})

