activate pip
pip install openai

import streamlit as st
import openai

# Ask for OpenAI/ChatGPT key
openai_key = st.text_input("Please enter your OpenAI key", type="password")
openai.api_key = openai_key

# Ask for a description of a software application
software_description = st.text_area("Please enter a description of the software application")

if st.button('Submit'):
    if openai_key and software_description:
        # Use the Chat model from GPT-3
        response = openai.ChatCompletion.create(
            model="text-davinci-002",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI developed by OpenAI. Please analyze the following software description and provide potential security risks according to STRIDE and MITRE ATT&CK® framework."
                },
                {
                    "role": "user",
                    "content": software_description
                }
            ]
        )

        # Display the model's response
        st.write(response['choices'][0]['message']['content'])
    else:
        st.write("Please fill in all the fields.")
