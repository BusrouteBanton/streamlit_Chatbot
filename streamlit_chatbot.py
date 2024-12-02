import streamlit as st
import openai
import pandas as pd
import os

# Streamlit app title
st.title("Talk to Me Nice - CSV Assistant")

# Set up OpenAI API key securely
openai.api_key = st.secrets["openai"]["api_key"]

# Default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I assist you today?"}
    ]

# Upload CSV
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    try:
        # Read CSV into a DataFrame
        df = pd.read_csv(uploaded_file)
        st.session_state["df"] = df
        st.write("CSV file uploaded successfully! Here's a preview:")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error reading the CSV file: {e}")
        st.stop()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I assist you today?"}
    ]
    st.experimental_rerun()

# React to user input
if prompt := st.chat_input("Ask a question about the CSV content or anything else:"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare context for GPT
    csv_preview = st.session_state.get("df", pd.DataFrame()).head(5).to_dict()  # Preview of the CSV for context
    csv_summary = (
        f"The user has uploaded a CSV file with the following columns: {', '.join(st.session_state['df'].columns)}."
        if "df" in st.session_state
        else "No CSV file is uploaded."
    )

    assistant_context = (
        f"Here is a preview of the CSV data: {csv_preview}. "
        if "df" in st.session_state
        else ""
    )

    # Generate response with OpenAI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": "system", "content": csv_summary + assistant_context},
                    *[
                      {"role": m["role"], "content": m["content"]}
                      for m in st.session_state.messages
                     ],
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
