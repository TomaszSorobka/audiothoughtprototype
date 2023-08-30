import threading
import streamlit as st
from utils import transcribe_audio, summarize_transcript, count_down
import theme
from audiorecorder import audiorecorder
import os
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder
import time
import json
import os
from typing import Optional

import streamlit.components.v1 as components

_RELEASE = True

if _RELEASE:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _audio_recorder = components.declare_component(
        "audio_recorder", path=build_dir
    )
else:
    _audio_recorder = components.declare_component(
        "audio_recorder",
        url="http://localhost:3001",
    )


def audio_recorder(
    text: str = "Click to record",
    energy_threshold: float = 0.01,
    pause_threshold: float = 0.8,
    neutral_color: str = "#303030",
    recording_color: str = "#de1212",
    icon_name: str = "microphone",
    icon_size: str = "3x",
    sample_rate: Optional[int] = None,
    key: Optional[str] = None,
) -> Optional[bytes]:
    """Create a new instance of "audio_recorder".

    Parameters
    ----------
    text: str
        The text to display next to the recording button.
    energy_threshold: Union[float, Tuple[float, float]]
        The energy recording sensibility above which we consider that the user
        is speaking. If it is a float, then this is the energy threshold used
        to automatically detect recording start and recording end. You can
        provide a tuple for specifying different threshold for recording start
        detection and recording end detection.
    pause_threshold: float
        The number of seconds to spend below `energy_level` to automatically
        stop the recording.
    neutral_color: str
        Color of the recorder icon while stopped.
    recording_color: str
        Color of the recorder icon while recording.
    icon_name: str
        Font Awesome solid icon name
        (https://fontawesome.com/search?o=r&s=solid)
    icon_size: str
        Size of the icon (https://fontawesome.com/docs/web/style/size)
    sample_rate: Optional[int]
        Sample rate of the recorded audio. If not provided, this will use the
        default sample rate
        (https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/AudioContext).
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will be
        re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    Optional[bytes]
        Bytes representing the recorded audio in the `audio/wav` format.

    """
    if type(energy_threshold) in [list, tuple]:
        start_threshold, end_threshold = energy_threshold
    else:
        start_threshold = energy_threshold
        end_threshold = energy_threshold

    data = _audio_recorder(
        text=text,
        start_threshold=start_threshold,
        end_threshold=end_threshold,
        pause_threshold=pause_threshold,
        neutral_color=neutral_color,
        recording_color=recording_color,
        icon_name=icon_name,
        icon_size=icon_size,
        sample_rate=sample_rate,
        key=key,
        default=None,
    )
    audio_bytes = bytes(json.loads(data)) if data else None
    return audio_bytes


if not _RELEASE:
    import streamlit as st

    st.subheader("Base audio recorder")
    base_audio_bytes = audio_recorder(key="base")
    if base_audio_bytes:
        st.audio(base_audio_bytes, format="audio/wav")

    st.subheader("Custom recorder")
    custom_audio_bytes = audio_recorder(
        text="",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="user",
        icon_size="6x",
        sample_rate=41_000,
        key="custom"
    )
    st.text("Click to record")
    if custom_audio_bytes:
        st.audio(custom_audio_bytes, format="audio/wav")

    st.subheader("Fixed length recorder")
    fixed_audio_bytes = audio_recorder(
        energy_threshold=(-1.0, 1.0),
        pause_threshold=3.0,
        key="fixed",
    )
    st.text("Click to record 3 seconds")
    if fixed_audio_bytes:
        st.audio(fixed_audio_bytes, format="audio/wav")

# Load variables from .env file into the environment
load_dotenv()
api_key = st.secrets["API_KEY"]#os.getenv("API_KEY")
col1, col2, col3 = st.columns(3)


    
# Streamlit app
#st.set_page_config(**theme.page_config)

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
guide = '''
<h4>Please allow for the use of microphone!</h4>
1. Press the grey microphone below to start recording <br>  2. Speak your thoughts (max. 2 minutes) <br> 3.Press the red microphone icon to stop recording <br> 4. Press \"Generate Summary\" button! <br><br>
'''
st.write(guide, unsafe_allow_html=True)

#api_key = ""#st.text_input("Enter your OpenAI API key:", type="password")
models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4-0613"]
model = "gpt-3.5-turbo"#st.selectbox("Select a model:", models)



audio_bytes = audio_recorder(text = "", neutral_color="#808080",icon_size="5x",  energy_threshold=(-1.0, 1.0), pause_threshold=120.0, key="Record")

#uploaded_audio = st.file_uploader("Upload an audio file", type=['m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg'], accept_multiple_files=False)

if audio_bytes:
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

custom_prompt = None

custom_prompt = '''Summarize the following audio using an every day simple language, using the 1st person (never use the 3rd person) and most importantly keep it short (no longer than half of the length of the transcription):'''
#st.text_input("Enter a custom prompt:", value = "Summarize the following audio transcription:")

if st.button("Generate Summary"):
    if uploaded_audio:
        if api_key:
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
        else:
            st.error("Please enter a valid OpenAI API key.")


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
