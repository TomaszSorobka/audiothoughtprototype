import webbrowser
import streamlit as st
from utils import transcribe_audio, summarize_transcript, count_down
import theme
from audio_recorder_streamlit import audio_recorder
import time

# import os
# import dotenv
custom_prompt = '''Summarize the following audio using an every day simple language, using the 1st person (never use the 3rd person) and most importantly keep it short (no longer than half of the length of the transcription):'''

def initialize_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.timesUsed = 0
        st.session_state.time = time.time()-30

initialize_session_state()
# Load variables from .env file into the environment
#dotenv.load_dotenv() os.getenv("API_KEY")
api_key = st.secrets["API_KEY"]

# Streamlit app
st.set_page_config(**theme.page_config)
#st.write("Value:", st.session_state.timesUsed)

class AudioBytesWrapper:
    def __init__(self, audio_bytes):
        self.audio_bytes = audio_bytes
        self.name = "audio.wav"

    def read(self):
        return self.audio_bytes

title = """
    <h1 style="color:#eb5266; font-family:sans-serif;">🎙️AudioThought Prototype: Audio Transcription and Summarization 🎙️</h1>
"""
st.markdown(title, unsafe_allow_html=True)

linkTutorial = '[See a tutorial](https://www.loom.com/share/03aec25952e146cb9f870efec92bdc01)'
st.markdown(linkTutorial, unsafe_allow_html=True)

guide = '''
<h4>Please allow for the use of microphone!</h4>
1. Press the grey microphone below to start recording <br>  2. Speak your thoughts (max. 3 minutes) <br> 3. Press the red microphone icon to stop recording <br> 4. Wait for the summary to generate! <br><br>
'''
st.write(guide, unsafe_allow_html=True)

#api_key = ""#st.text_input("Enter your OpenAI API key:", type="password")
models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4-0613"]
model = "gpt-3.5-turbo"#st.selectbox("Select a model:", models)



audio_bytes = audio_recorder(text = "Click to start/stop recording->", neutral_color="#808080",icon_size="8x",  energy_threshold=(-1.0, 1.0), pause_threshold=180.0, key="Record")

#uploaded_audio = st.file_uploader("Upload an audio file", type=['m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg'], accept_multiple_files=False)
if st.session_state.timesUsed <= 10:
    if audio_bytes:
        st.session_state.timesUsed += 1
        # countdown_time = 120  # Countdown time in seconds
        # with st.empty():
        #     for remaining_time in range(countdown_time, 0, -1):
        #         mins, secs = divmod(remaining_time, 60)
        #         time_now = '{:02d}:{:02d}'.format(mins, secs)
        #         st.header(f"Recording... Time remaining: {time_now}")
        #         time.sleep(1)
        
        # st.header("Recording completed!")
        st.audio(audio_bytes, format="audio/wav")
        uploaded_audio = AudioBytesWrapper(audio_bytes)
        if api_key:
            currentTime = time.time()
            if currentTime - st.session_state.time > 10.0:
                st.session_state.time = time.time()
                st.markdown("Transcribing the audio...")
                transcript = transcribe_audio(api_key, uploaded_audio)
                st.markdown(f"###  Transcription:\n\n<details><summary>Click to view</summary><p><pre><code>{transcript.text}</code></pre></p></details>", unsafe_allow_html=True)

                st.markdown("Summarizing the transcription...")
                if custom_prompt:
                    summary = summarize_transcript(api_key, transcript, model, custom_prompt)
                else:
                    summary = summarize_transcript(api_key, transcript, model)
                    
                st.markdown(f"### Summary:")
                st.write(summary)
                st.write("<i>Do you like this app? Then please reach out to us at audiothought.contact@gmail.com!</i>", unsafe_allow_html=True)
            else:
                st.error("please wait at least 10 seconds between generating each summary")
        else:
            st.error("Please enter a valid OpenAI API key.")
else:
    st.error("Wow slow down, you generated 10 summaries already! Please come back at a later time or reach out to me at audiothought.contact@gmail.com if you want more!")

#st.text_input("Enter a custom prompt:", value = "Summarize the following audio transcription:")
# if st.button("Generate Summary"):
#     if uploaded_audio:
#         if api_key:
#             currentTime = time.time()
#             if currentTime - oldTime > 200.0:
#                 oldTime = time.time()
#                 st.markdown("Transcribing the audio...")
#                 transcript = transcribe_audio(api_key, uploaded_audio)
#                 st.markdown(f"###  Transcription:\n\n<details><summary>Click to view</summary><p><pre><code>{transcript.text}</code></pre></p></details>", unsafe_allow_html=True)

#                 st.markdown("Summarizing the transcription...")
#                 if custom_prompt:
#                     summary = summarize_transcript(api_key, transcript, model, custom_prompt)
#                 else:
#                     summary = summarize_transcript(api_key, transcript, model)
                    
#                 st.markdown(f"### Summary:")
#                 st.write(summary)
#             else:
#                 st.error("please wait at least 20 seconds between generating each summary")
#         else:
#             st.error("Please enter a valid OpenAI API key.")


# st.markdown(
#     """
#     ---
#     ### Source code and contact information
#     - The source code for this app can be found on GitHub: [SpeechDigest](https://github.com/StanGirard/speechdigest)
#     - If you have any questions or comments, feel free to reach out to me on Twitter: [@_StanGirard](https://twitter.com/_StanGirard)
#     """
# )

# col1, col2 = st.columns(2)

# with col1:
#     st.markdown(
#         """
#         [![Tweet](https://img.shields.io/twitter/url?url=https%3A%2F%2Fgithub.com%2FStanGirard%2Fspeechdigest)](https://twitter.com/intent/tweet?url=https://github.com/StanGirard/speechdigest&text=Check%20out%20this%20awesome%20Speech%20Digest%20app%20built%20with%20Streamlit!%20%23speechdigest%20%23streamlit)
#         """
#     )

# with col2:
#     st.markdown(
#         """
#         [![GitHub Stars](https://img.shields.io/github/stars/StanGirard/speechdigest?style=social)](https://github.com/StanGirard/speechdigest/stargazers)
#         """
#     )
