import sys
import speech_recognition as sr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import load_config
from core.voice import VoiceSystem


def test_microphone():
    print("=== AURA Microphone Test ===")
    print()
    
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("Adjusting for ambient noise...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("Microphone ready!")
        print("Say something... (5 second timeout)")
        
        with microphone as source:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        
        print("Processing audio...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        print()
        print("Microphone test successful!")
        return True
        
    except sr.WaitTimeoutError:
        print("ERROR: No audio detected within timeout period")
        return False
    except sr.UnknownValueError:
        print("ERROR: Could not understand audio")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        print("Possible issues:")
        print("1. Microphone not connected")
        print("2. Microphone permissions not granted")
        print("3. No default microphone selected")
        return False


def test_tts():
    print("=== AURA Text-to-Speech Test ===")
    print()
    
    config = load_config()
    voice_system = VoiceSystem(config)
    
    print("Testing text-to-speech...")
    test_message = "Hello, this is a test of the AURA text to speech system."
    
    print(f"Saying: {test_message}")
    voice_system.speak(test_message)
    print("Text-to-speech test complete!")


if __name__ == "__main__":
    print("Choose test:")
    print("1. Microphone")
    print("2. Text-to-Speech")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        test_microphone()
    elif choice == "2":
        test_tts()
    elif choice == "3":
        test_microphone()
        print()
        test_tts()
    else:
        print("Invalid choice")

