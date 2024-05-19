import streamlit as st
from streamlit import session_state as ss

# import modules
from openai_backend import *

# intialize agent
if 'initialized' not in st.session_state:
    agent = Assistant()
    print(agent.assistant.id)
    print(agent.thread.id)

# Streamlit app configuration
st.set_page_config(
    page_title = "AeroCertChatBot",
    page_icon  = "✈️",
)

# variables
if "chat_history" not in ss:
    ss.chat_history = []

st.title( "🛫:blue[Aerospace Certification] :red[Chatbot]" )

# Display chat messages from history on app rerun
for message in ss.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask anything about aerospace certification!"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to app chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    # send message to chat bot
    agent.add_user_prompt("user", prompt)


# Display assistant response in chat message container
with st.chat_message("assistant"):
    # Empty container to display the assistant's reply
    assistant_reply_box = st.empty()
    
    # A blank string to store the assistant's reply
    assistant_reply = ""
    
    # create the agent run
    assistant_reply = agent.stream_response(assistant_reply_box, assistant_reply)
    print(assistant_reply)

    # Once the stream is over, update chat history
    ss.chat_history.append({"role": "assistant",
                                          "content": assistant_reply})