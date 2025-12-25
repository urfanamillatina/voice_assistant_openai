
import os
import time
import traceback
import sys
import threading
import queue
import subprocess

try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    import pyttsx3
except Exception:
    pyttsx3 = None
    
from dotenv import load_dotenv
load_dotenv()


# Global state

_is_speaking = False
_tts_lock = threading.Lock()

# OpenAI client

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

client_modern = None

def init_openai_client():
    global client_modern
    if OPENAI_API_KEY is None:
        print("Warning: OPENAI_API_KEY is not set. OpenAI calls will fail.", file=sys.stderr)
    try:
        from openai import OpenAI
        client_modern = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else OpenAI()
        print("Using modern OpenAI client (OpenAI()).")
    except Exception as e:
        client_modern = None
        print(f"OpenAI client failed: {e}")

def ask_openai_chat(prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
    if client_modern is None:
        init_openai_client()
    
    if client_modern is None:
        return "OpenAI client not available. Please check your OPENAI_API_KEY."
    
    try:
        response = client_modern.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print("OpenAI API call failed:", e, file=sys.stderr)
        traceback.print_exc()
        if "OPENAI_API_KEY" in str(e):
            return "OpenAI API error: API key not set."
        return f"OpenAI API error: {e}"


# Thread-safe TTS

TTS_RATE = 120
_tts_queue = queue.Queue()
_tts_thread = None
_tts_stop_event = threading.Event()

def speak_macos(text: str):
    global _is_speaking
    try:
        clean_text = text.replace('"', "'").replace('\n', ' ')
        subprocess.run(["say", clean_text], check=True)
    except Exception as e:
        print(f"macOS TTS failed: {e}")
        print("[TTS] " + text)

def _tts_worker():
    """Worker thread for TTS"""
    global _is_speaking
    
    while not _tts_stop_event.is_set():
        try:
            text = _tts_queue.get(timeout=0.5)
        except queue.Empty:
            continue
        if text is None:
            break
        
        if not text:
            continue
        
        # Set speaking flag
        with _tts_lock:
            _is_speaking = True
        
        # Speak the text
        print(f"[Speaking] {text[:100]}{'...' if len(text) > 100 else ''}")
        speak_macos(text)
        
        # Clear speaking flag
        with _tts_lock:
            _is_speaking = False

def start_tts_thread():
    global _tts_thread
    if _tts_thread is None or not _tts_thread.is_alive():
        _tts_stop_event.clear()
        _tts_thread = threading.Thread(target=_tts_worker, name="TTS-Thread", daemon=True)
        _tts_thread.start()

def stop_tts_thread():
    _tts_stop_event.set()
    try:
        _tts_queue.put_nowait(None)
    except Exception:
        pass
    if _tts_thread is not None:
        _tts_thread.join(timeout=2)

def speak(text: str):
    """Speak text and update speaking state"""
    if not text:
        return
    start_tts_thread()
    _tts_queue.put(text)

def is_speaking():
    """Check if TTS is currently speaking"""
    with _tts_lock:
        return _is_speaking


# Speech recognition

_recognizer = sr.Recognizer() if sr is not None else None
_microphone = None

def init_audio_resources():
    global _microphone
    if sr is None:
        print("SpeechRecognition library not available. STT disabled.", file=sys.stderr)
        return
    if _microphone is not None:
        return
    try:
        _microphone = sr.Microphone()
    except Exception as e:
        print("Microphone initialization failed:", e, file=sys.stderr)
        traceback.print_exc()
        _microphone = None

def listen_once(timeout: float = 30, phrase_time_limit: float = 50) -> str:
    # no listening when user is speaking
    if is_speaking():
        return ""
    
    init_audio_resources()
    if _microphone is None or _recognizer is None:
        return ""
    
    with _microphone as source:
        try:
            _recognizer.adjust_for_ambient_noise(source, duration=0.6)
            print("Listening... (speak now)")
            audio = _recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return ""
        except Exception as e:
            print("Error while listening:", e)
            traceback.print_exc()
            return ""
    
    try:
        text = _recognizer.recognize_google(audio)
        print("Recognized:", text)
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print("API request failed:", e)
        try:
            text = _recognizer.recognize_sphinx(audio)
            print("Sphinx recognized:", text)
            return text
        except Exception as e2:
            print("Pocketsphinx fallback failed:", e2)
            return ""
    except Exception as e:
        print("Unexpected error:", e)
        traceback.print_exc()
        return ""


# Main loop

def main_loop():
    print("Starting voice bot with OpenAI integration. Say 'quit' to stop.")
    print("Note: Microphone is muted while assistant is speaking to prevent feedback.")
    init_openai_client()
    start_tts_thread()
    
    try:
        while True:
            # Wait a moment before starting to listen (avoid echo)
            time.sleep(0.5)
            
            user_text = listen_once()
            if not user_text:
                continue
            
            if user_text.strip().lower() in ("quit", "exit", "stop", "goodbye"):
                speak("Goodbye. Shutting down.")
                time.sleep(2)  # Wait for speech to finish
                break
            
            print("You:", user_text)
            print("Sending to OpenAI...")
            reply = ask_openai_chat(user_text)
            print("Assistant:", reply)
            
            # Speak the reply
            speak(reply)
            
            # Wait for speech to finish before listening again
            while is_speaking():
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        stop_tts_thread()
        print("Exited cleanly.")

if __name__ == "__main__":
    main_loop()