# This Streamlit web application leverages OpenAI's Large Language Models (LLMs) to generate threat models for given applications using the STRIDE methodology. Cyber security professionals can provide application descriptions and key details, such as the application type, authentication methods, and whether the application is internet-facing or processes sensitive data. Upon submission, the LLM generates a threat model based on the provided details.

# The app layout includes input fields for the application details, a submit button, and a sidebar with helpful information, such as how to use the app, an example application description, and FAQs. Users can generate a threat list and/or attack tree visualisations for their applications. The app also includes options to download the generated threat model and attack tree as Markdown files.

# Features:
# - Application description input field
# - Selectable application type, authentication methods, internet-facing status, sensitive data level, and privileged access management status
# - Generate threat model and attack tree based on user input
# - Display generated threat model and attack tree in the app
# - Download threat model and attack tree as Markdown files
# - Sidebar with helpful information, such as how to use the app, example application description, and FAQs
# - Interactive attack tree visualization using Mermaid.js (experimental)
# - Support for GPT-3 and GPT-4 models (provided the user has access to GPT-4 API)

import streamlit as st
import streamlit.components.v1 as components
from langchain import PromptTemplate
from langchain.llms import OpenAI

import os

# Define the GPT prompt templates
threat_model_template = """
    Act as a cyber security expert with more than 20 years experience of using the STRIDE threat modelling methodology to produce comprehensive threat models for a wide range of applications. Your task is to use the application description provided to you to produce a list of specific threats for the application. Your analysis should provide a credible scenario in which each threat could occur in the context of the application. It is very important that your responses are tailored to reflect the details you are given.

    In addition to the description, you will be provided with the following key details about the application that you will need to consider when producing your threat model:
    - The type of application
    - The methods used to authenticate users to the application
    - Whether or not the application is internet-facing
    - Whether or not the application processes sensitive data
    - Whether or not the application uses privileged access management to protect privileged accounts

    Below is the application description and key details:
    APPLICATION TYPE: {app_type}
    AUTHENTICATION METHODS: {authentication}
    INTERNET FACING: {internet_facing}
    SENSITIVE DATA: {sensitive_data}
    PRIVILEGED ACCESS MANAGEMENT: {pam}
    APPLICATION DESCRIPTION: {app_input}

    Your output should be in the form of a markdown table with the following columns:
    - Column A: Threat Type
    - Column B: Scenario
    - Column C: Potential Impact
    
    Below the table you should add a new section and then make some suggestions to the user on how they can improve the application description to enable you to produce a more comprehensive threat model.

    YOUR RESPONSE:
"""

attack_tree_template = """
    Act as a cyber security expert with more than 20 years experience of creating attack trees to communicate the likely routes by which systems and applications will be attacked by adversaries. Your task is to use the application description provided to you to generate an attack tree for the application. Your analysis should be based on credible attack types that could occur given the context of the application. It is very important that your responses are tailored to reflect the details you are given.

    In addition to the description, you will be provided with the following key details about the application that you will need to consider when producing the attack tree:
    - The type of application
    - The methods used to authenticate users to the application
    - Whether or not the application is internet-facing
    - Whether or not the application processes sensitive data
    - Whether or not the application uses privileged access management to protect privileged accounts

    Below is the application description and key details:
    APPLICATION TYPE: {app_type}
    AUTHENTICATION METHODS: {authentication}
    INTERNET FACING: {internet_facing}
    SENSITIVE DATA: {sensitive_data}
    PRIVILEGED ACCESS MANAGEMENT: {pam}
    APPLICATION DESCRIPTION: {app_input}

    Your output should be in the form of an attack tree that is presented as a Mermaid diagram.

    IMPORTANT: It is critical that the Mermaid diagram code does not contain round brackets. If you include these characters, the diagram will not render correctly for the user.
    
    Below the attack tree you should add a new section and then make some suggestions to the user on how they can improve the application description to enable you to produce a more comprehensive and accurate attack tree.

    YOUR RESPONSE:
"""

# Create a PromptTemplate objects with the specified input variables
threat_model_prompt = PromptTemplate(
    input_variables=["app_type", "authentication", "internet_facing", "sensitive_data", "pam", "app_input"],
    template=threat_model_template,
)

attack_tree_prompt = PromptTemplate(
    input_variables=["app_type", "authentication", "internet_facing", "sensitive_data", "pam", "app_input"],
    template=attack_tree_template,
)

# Function to load LLM (Language Model) with given API key and model name
def load_LLM(api_key, model_name):
    os.environ['OPENAI_API_KEY'] = api_key
    llm = OpenAI(temperature=0.7, model_name=model_name, max_tokens=1000)
    return llm

# Set Streamlit page configurations
st.set_page_config(page_title="STRIDE GPT", page_icon=":shield:", layout="wide", initial_sidebar_state="expanded")
st.header("STRIDE GPT🛡️")

st.markdown("""
    **S**poofing 🕶 **T**ampering 🛠️ **R**epudiation 🤷 **I**nformation Disclosure 📢 **D**enial of Service 🛑 **E**levation of Privilege 🤴
    """)

# Function to get user input for the application description
def get_input():
    input_text = st.text_area(label="Describe the application to be modelled", placeholder="Enter your application details...", height=150, key="app_input", help="Please provide a detailed description of the application, including the purpose of the application, the technologies used, and any other relevant information.")
    return input_text

# Function to render Mermaid diagram
def mermaid(code: str, height: int = 500) -> None:
    components.html(
        f"""
        <pre class="mermaid" style="height: {height}px;">
            {code}
        </pre>

        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        """,
        height=height,
    )

# Function to extract Mermaid code from LLM output
def extract_mermaid_code(llm_output: str) -> str:
    start_marker = "```mermaid"
    end_marker = "```"
    start_index = llm_output.find(start_marker)

    if start_index == -1:
        return ""

    start_index += len(start_marker)
    end_index = llm_output.find(end_marker, start_index)

    if end_index == -1:
        return ""

    return llm_output[start_index:end_index].strip()

# Get application description from the user
app_input = get_input()

# Create two columns layout for input fields
col1, col2 = st.columns(2)

# Create input fields for app_type, sensitive_data and pam
with col1:
    app_type = st.selectbox(
        label="Select the application type", 
        options=["Web application", "Mobile application", "Desktop application", "Cloud application", "IoT application", "Other"], 
        key="app_type"
        )

    sensitive_data = st.selectbox(
        label="What is the highest sensitivity level of the data processed by the application?",
        options=["Top Secret", "Secret", "Confidential", "Restricted", "Unclassified", "None"],
        key="sensitive_data"
        )
    
    pam = st.selectbox(
        label="Are privileged accounts stored in a Privileged Access Management (PAM) solution?",
        options=["Yes", "No"],
        key="pam"
    )

# Create input fields for internet_facing and authentication
with col2:
    internet_facing = st.selectbox(
        label="Is the application internet-facing?", 
        options=["Yes", "No"], 
        key="internet_facing"
        )
    
    authentication = st.multiselect(
        'What authentication methods are supported by the application?',
        ['SSO', 'MFA', 'OAUTH2', 'Basic', 'None'],
        key="authentication"
    )

# Add instructions on how to use the app to the sidebar
st.sidebar.header("How to use STRIDE GPT")

with st.sidebar:
    st.markdown("""
    1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) and chosen model below 🔑
    2. Provide details of the application that you would like to threat model  📝
    3. Generate a threat list and/or attack tree for your application 🚀
    """)

    # Add OpenAI API key input field to the sidebar
    openai_api_key = st.text_input("Enter your OpenAI API key:", type="password", help="You can find your OpenAI API key on the [OpenAI dashboard](https://platform.openai.com/account/api-keys).")

    # Add model selection input field to the sidebar
    selected_model = st.selectbox("Select the model you would like to use:", ["text-davinci-003", "gpt-3.5-turbo", "gpt-4"], key="selected_model", help="You must have been given access to the [GPT-4 API](https://openai.com/waitlist/gpt-4-api) by OpenAI in order to use it.")

    st.markdown("""---""")

# Add "About" section to the sidebar
st.sidebar.header("About")

with st.sidebar:
    st.markdown("Welcome to STRIDE GPT, an AI-powered tool designed to help teams produce better threat models for their applications.")
    st.markdown("Threat modelling is a key activity in the software development lifecycle, but is often overlooked or poorly executed. STRIDE GPT aims to help teams produce more comprehensive threat models by leveraging the power of OpenAI's GPT models to generate a threat list and/or attack tree for an application based on the details provided.")
    st.markdown("Created by [Matt Adams](https://www.linkedin.com/in/matthewrwadams/).")
    st.markdown("""---""")


# Add "Example Application Description" section to the sidebar
st.sidebar.header("Example Application Description")

with st.sidebar:
    st.markdown("Below is an example application description that you can use to test STRIDE GPT:")
    st.markdown("> A web application that allows users to create, store, and share personal notes. The application is built using the React frontend framework and a Node.js backend with a MongoDB database. Users can sign up for an account and log in using OAuth2 with Google or Facebook. The notes are encrypted at rest and are only accessible by the user who created them. The application also supports real-time collaboration on notes with other users.")
    st.markdown("""---""")

# Add "FAQs" section to the sidebar
st.sidebar.header("FAQs")

with st.sidebar:
    st.markdown("""
    ### **What is STRIDE?**
    STRIDE is a threat modeling methodology that helps to identify and categorise potential security risks in software applications. It stands for **S**poofing, **T**ampering, **R**epudiation, **I**nformation Disclosure, **D**enial of Service, and **E**levation of Privilege.
    """)
    st.markdown("""
    ### **How does STRIDE GPT work?**
    When you enter an application description and other relevant details, the tool will use a GPT-3 model to generate a threat model for your application. The model uses the application description and details to generate a list of potential threats and then categorises each threat according to the STRIDE methodology.
    """)
    st.markdown("""
    ### **Do you store the application details provided?**
    No, STRIDE GPT does not store your application description or other details. All entered data is deleted after you close the browser tab.
    """)
    st.markdown("""
    ### **Why does it take so long to generate a threat model?**
    If you are using a free OpenAI API key, it will take a while to generate a threat model. This is because the free API key has strict rate limits. To speed up the process, you can use a paid API key.
    """)
    st.markdown("""
    ### **Are the threat models 100% accurate?**
    No, the threat models are not 100% accurate. STRIDE GPT uses GPT Large Language Models (LLMs) to generate its output. The GPT models are powerful, but they sometimes makes mistakes and are prone to 'hallucinations' (generating irrelevant or inaccurate content). Please use the output only as a starting point for identifying and addressing potential security risks in your applications.
    """)
    st.markdown("""
    ### **How can I improve the accuracy of the threat models?**
    You can improve the accuracy of the threat models by providing a detailed description of the application and selecting the correct application type, authentication methods, and other relevant details. The more information you provide, the more accurate the threat models will be.
    """)

st.markdown("""---""") 

# Create a collapsible section for Threat Modelling
with st.expander("Threat Model", expanded=False):
    # Create a submit button for Threat Modelling
    threat_model_submit_button = st.button(label="Generate Threat Model")

    # If the Generate Threat Model button is clicked and the user has provided an application description
    if threat_model_submit_button and app_input:
        # Load the Language Model with the provided API key
        llm = load_LLM(openai_api_key, selected_model)

        # Format the prompt with the user-provided details
        prompt_with_details = threat_model_prompt.format(app_type=app_type, authentication=authentication, internet_facing=internet_facing, sensitive_data=sensitive_data, pam=pam, app_input=app_input)

        # Show a spinner while generating the threat model
        with st.spinner("Analysing potential threats..."):
            model_output = llm(prompt_with_details)

        # Display the generated threat model
        st.write(model_output)

        # Add a button to allow the user to download the output as a Markdown file
        st.download_button(
        label="Download Output",
        data=model_output,
        file_name="stride_gpt_threat_model.md",
        mime="text/markdown",
        )

    # If the submit button is clicked and the user has not provided an application description
    if threat_model_submit_button and not app_input:
        st.error("Please enter your application details before submitting.")

# Create a collapsible section for Attack Tree
with st.expander("Attack Tree", expanded=False):

    # Create a submit button for Attack Tree
    attack_tree_submit_button = st.button(label="Generate Attack Tree")

    # If the Generate Attack Tree button is clicked and the user has provided an application description
    if attack_tree_submit_button and app_input:
        if selected_model == "text-davinci-003":
            st.warning("The 'text-davinci-003' model produces less reliable outputs for attack trees. Please select either 'gpt-3.5-turbo' or 'gpt-4' for better results.")
        else:
            # Load the Language Model with the provided API key
            llm = load_LLM(openai_api_key, selected_model)

            # Format the prompt with the user-provided details
            prompt_with_details = attack_tree_prompt.format(app_type=app_type, authentication=authentication, internet_facing=internet_facing, sensitive_data=sensitive_data, pam=pam, app_input=app_input)

            # Show a spinner while generating the attack tree
            with st.spinner("Generating attack tree..."):
                model_output = llm(prompt_with_details)

            # Display the generated attack tree
            st.write(model_output)

            # Add a button to allow the user to download the output as a Markdown file
            st.download_button(
            label="Download Attack Tree",
            data=model_output,
            file_name="stride_gpt_attack_tree.md",
            mime="text/markdown",
            )

            # Extract the Mermaid code from the LLM output
            mermaid_code = extract_mermaid_code(model_output)

            st.markdown("""
            ### Attack Tree Visualisation
            """)

            # Inform the user that the Mermaid visualisation feature is experimental
            st.info("Please note that this feature is experimental. To view the attack tree in detail and/or edit the diagram visit [Mermaid Live](https://mermaid.live) and paste the generated Mermaid code into the editor.")

            # Visualise the attack tree using the Mermaid custom component
            mermaid(mermaid_code)

    # If the submit button is clicked and the user has not provided an application description
    if threat_model_submit_button and not app_input:
        st.error("Please enter your application details before submitting.")
