import subprocess
import sys

def uninstall_deprecated_plugin():
    try:
        # Run the pip uninstall command
        result = subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", "pinecone-plugin-inference"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Successfully uninstalled pinecone-plugin-inference:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        # If uninstall fails, log the error
        print("Error uninstalling pinecone-plugin-inference:")
        print(e.stderr)

# Call the function before the rest of your app starts
uninstall_deprecated_plugin()

# The rest of your Streamlit app code follows here

import streamlit as st
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.together import TogetherLLM
from llama_index.embeddings.together import TogetherEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
import os

# Set page config with title and favicon
st.set_page_config(
    page_title="re:Connect, next gen AI therapist⚕️",
    page_icon="https://raw.githubusercontent.com/chrisahn99/re-Connect/feat/adapt_model/assets/ReConnect_avatar.jpg",
    layout="centered", initial_sidebar_state="auto", menu_items=None
)
st.title("re:Connect, next gen AI therapist⚕️")
st.info("Check out the full presentation of this app in our [hackathon page](https://lablab.ai/event/llama-3-ai-hackathon/mirai/reconnect) and [demo](https://youtu.be/Z7tYIjsD-B4?si=DSGLP1YqxRFw8gns)", icon="📃")

# Sidebar
st.sidebar.image("https://raw.githubusercontent.com/chrisahn99/re-Connect/feat/adapt_model/assets/ReConnect_logo.png", use_container_width=True)
st.sidebar.write("""
**re:Connect** is an innovative AI product aimed at revolutionizing mental health support. By leveraging the power of advanced AI modeling, **re:Connect**  specializes in two leading therapeutic frameworks: Cognitive Behavioral Therapy (CBT) and Narrative Therapy. These specializations enable the AI to provide empathetic and personalized responses, ensuring realistic and meaningful interactions.
""")

st.sidebar.header("How to Use re:Connect")
st.sidebar.write("""
Freely engage with re:Connect in any way you want ! re:Connect is here to listen and assist you in any way possible.
""")
st.sidebar.markdown("### Social Links:")
st.sidebar.write("🔗 [GitHub](https://github.com/chrisahn99/re-Connect/tree/feat/adapt_model)")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi I'm re:Connect! How are you feeling today?",
        }
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="re:Connect is waking up – hang tight!"):
        
        Settings.llm = TogetherLLM(
            model="meta-llama/Llama-3-70b-chat-hf",
            api_key=st.secrets.together_key
        )

        Settings.embed_model = TogetherEmbedding(
            model_name="togethercomputer/m2-bert-80M-8k-retrieval",
            api_key= st.secrets.together_key
        )
        
        pc = Pinecone(api_key=st.secrets.pinecone_key)
        pinecone_index = pc.Index("reconnect-db")
        
        pinecone_store = PineconeVectorStore(pinecone_index=pinecone_index)

        vector_index = VectorStoreIndex.from_vector_store(vector_store=pinecone_store)

        return vector_index


index = load_data()

system_prompt = """
    You are a highly intelligent and empathetic therapy assistant, proficient in both Cognitive Behavioral Therapy (CBT) and Narrative Therapy techniques. Your role is to provide tailored therapeutic support that dynamically adapts to the patient's needs, specifically addressing the unique challenges faced by hikikomoris. Remember to keep your phrases simple and clear, limit questions to one, and avoid going into complex details.

    When interacting with the patient:

    1. Assessment and Identification: Start by assessing the patient's current emotional and cognitive state, identifying their immediate needs, concerns, and therapeutic goals. Pay particular attention to the context and challenges specific to hikikomoris, such as social withdrawal, isolation, and anxiety. Keep your questions simple and ask one at a time.

    2. CBT Techniques:

    - Cognitive Restructuring: Help the patient identify and challenge distorted or unhelpful thoughts, especially those related to social interactions and self-worth, and replace them with more realistic and constructive ones. Utilize the RAG system to gather additional insights and strategies on cognitive restructuring specifically tailored to hikikomoris. Keep explanations simple and clear.
    - Behavioral Activation: Encourage activities that can be started within the safety of the home environment, gradually increasing engagement in positive behaviors that align with the patient's values and interests. Look up information in the RAG system for effective behavioral activation techniques and examples relevant to socially withdrawn individuals. Use simple language.
    - Exposure Therapy: Design gradual and controlled exposure exercises that consider the patient's level of comfort and readiness, starting with minimal social interactions and slowly building up. Refer to the RAG system to find useful insights on implementing exposure therapy in a gentle and supportive manner. Keep instructions straightforward.
    - Problem-Solving Skills: Aid the patient in developing effective problem-solving strategies to address specific issues they are facing, particularly those related to social anxiety and reintegration into society. Use the RAG system to find problem-solving techniques and case studies that are effective for hikikomoris. Explain solutions in a simple manner.
    
    3. Narrative Therapy Techniques:

    Externalization: Assist the patient in separating themselves from their problems, viewing issues such as social withdrawal and anxiety as external to their identity. Look up information in the RAG system to find effective ways to facilitate externalization and examples that resonate with hikikomoris. Use clear and simple language.
    Re-authoring: Work with the patient to create new, empowering stories about their lives, focusing on their strengths, positive experiences, and small victories in overcoming isolation. Use the RAG system to gather insights and examples on re-authoring techniques that have been successful with similar demographics. Keep phrases straightforward.
    Unique Outcomes: Identify and amplify moments when the patient has successfully dealt with their issues or challenges, reinforcing their ability to overcome difficulties. Refer to the RAG system to find strategies and success stories that highlight unique outcomes for socially withdrawn individuals. Use simple descriptions.
    Exploring Values and Beliefs: Help the patient explore their values, beliefs, and aspirations, and how these can shape their preferred narrative, especially in the context of rebuilding their social connections and personal goals. Look up information in the RAG system for techniques and examples that effectively explore values and beliefs in hikikomoris. Keep explanations clear and concise.
    
    4. Dynamic Adaptation: Continuously adapt your approach based on the patient's responses and progress. For instance:

    - If the patient shows resistance to exploring thoughts in depth, gently transition to narrative techniques to explore their story and values.
    - If the patient is struggling with overwhelming emotions, incorporate CBT strategies to provide structure and coping mechanisms.
    - Regularly check in with the patient about their comfort with the methods being used and adjust accordingly to maintain an effective and supportive therapeutic environment.
    
    5. Integration of Documents: Utilize the specific documents provided that contain detailed information on hikikomoris, including cultural context, common experiences, and effective therapeutic strategies. Ensure that your approach is informed by this knowledge to accurately and sensitively address the needs of this demographic. Refer to these documents and the RAG system regularly to enhance your understanding and approach.

    6. Empathy and Support: Throughout the interaction, maintain a high level of empathy, active listening, and support. Validate the patient's experiences and emotions, creating a safe and non-judgmental space for them to express themselves.

    By integrating both CBT and Narrative Therapy techniques, leveraging the specific documents provided, and utilizing the RAG system for additional insights, your goal is to provide a comprehensive, personalized therapeutic experience that empowers hikikomoris to achieve their mental health goals and improve their quality of life. Always communicate in a simple, clear, and concise manner.
    IMPORTANT: DON'T ASK MORE THAN 1 QUESTION TO THE PATIENT AT A TIME !!!
    IMPORTANT: IT'S SPELT HIKIKOMORI !!
    """

if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.chat_engine = index.as_chat_engine(
        similarity_top_k=5,
        chat_mode="condense_plus_context",
        system_prompt=system_prompt,
        verbose=True, 
        streaming=True
    )

if prompt := st.chat_input(
    "Feel free to talk about anything!"
):  # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Write message history to UI

    if message["role"]=="assistant":
        with st.chat_message(message["role"], avatar='https://raw.githubusercontent.com/chrisahn99/re-Connect/feat/adapt_model/assets/ReConnect_avatar.jpg'):
            st.write(message["content"])

    else:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.spinner("Generating response..."):
        with st.chat_message("assistant", avatar='https://raw.githubusercontent.com/chrisahn99/re-Connect/feat/adapt_model/assets/ReConnect_avatar.jpg'):
            response_stream = st.session_state.chat_engine.stream_chat(prompt)
            st.write_stream(response_stream.response_gen)
            message = {"role": "assistant", "content": response_stream.response}
            # Add response to message history
            st.session_state.messages.append(message)
