<p align="center">
<h1 align="center">Voice Assistant with OpenAI
</h1>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/OpenAI-API-412991?logo=openai&logoColor=white" alt="OpenAI">
    <img src="https://img.shields.io/badge/SpeechRecognition-3.8%2B-FF6F61?logo=google-assistant&logoColor=white" alt="SpeechRecognition">
    <img src="https://img.shields.io/badge/macOS-TTS-000000?logo=apple&logoColor=white" alt="macOS">
    <img src="https://img.shields.io/badge/PyAudio-Audio%20I%2FO-0077B5?logo=audio-technica&logoColor=white" alt="PyAudio">
</p>



<p align="center">
  <a href="https://youtu.be/1EY0Sf1pzc4" target="_blank">
    <img src="https://img.youtube.com/vi/1EY0Sf1pzc4/maxresdefault.jpg" width="600" alt="Voice Assistant Demo">
    <br>
    <strong>▶️ Watch Demo on YouTube</strong>
  </a>
</p>


## 🎤 Voice Assistant with OpenAI

A voice-controlled AI assistant that uses speech recognition to listen to user's voice, processes it through OpenAI's language models, and responds with synthesized speech. The assistant's text response is displayed and also spoken via the thread-safe TTS queue.

## 1. What's This Project About?

This project creates an interactive voice assistant that:
- 🎤 **Listens** to user's voice commands using speech recognition
- 🧠 **Processes** user's speech through OpenAI's language models (GPT-3.5-turbo or GPT-4)
- 🔊 **Speaks back** responses using text-to-speech synthesis
- 🔄 **Prevents feedback loops** by muting the microphone during responses

**Key Features:**

- Thread-safe TTS to prevent audio overlap
- Configurable listening timeouts and response lengths
- Easy setup with environment variables
- macOS-native text-to-speech with `say` command

## 2. Tech Stack

### Core Technologies
- **Python 3.8+** - Primary programming language
- **OpenAI API** - For natural language processing
- **SpeechRecognition** - For converting speech to text
- **macOS Native TTS** - For text-to-speech synthesis

### Libraries Used
- `openai>=1.0.0` - Modern OpenAI API client
- `SpeechRecognition>=3.8.1` - Speech-to-text conversion
- `PyAudio` - Audio input handling
- `python-dotenv` - Environment variable management
- `pyttsx3` - Cross-platform TTS (fallback)

### Architecture Highlights
- **Thread-safe TTS Queue** - Prevents speech overlap
- **Feedback Prevention** - Microphone muting during responses
- **Error Handling** - Graceful fallbacks for failed recognitions
- **Modular Design** - Separated concerns for TTS, STT, and AI

## 3. Installation and Setup Guide

### Prerequisites
- Python 3.8 or higher
- macOS (or adjust TTS for your platform)
- OpenAI API key
- Microphone

### Step 1: Create and activate virtual environment
```bash
python3 -m venv .vvenv
source .vvenv/bin/activate
```

### Step 2: Install requirements

```bash
pip install -r requirements_openai.txt
```

### Step 3: Run the python file

```bash
python3 voicebot.py
```