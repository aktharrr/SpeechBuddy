from openai import OpenAI
import pyttsx3
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
import random
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
openAIClient = OpenAI()

class SpeechBuddyVoiceAssistant:
    def __init__(self, model_id='gpt-3.5-turbo', log_file='chat_log.txt', useOpenAiTTS=False, GPTinitialMessage=""):
        self.model_id = model_id
        self.recognizer = sr.Recognizer()
        self.conversation = []
        self.log_file = log_file
        self.clear_log_file()
        self.GPTinitialMessage=GPTinitialMessage
        self.useOpenAiTTS = useOpenAiTTS
        if not useOpenAiTTS:
            self.engine = pyttsx3.init()
            self.set_engine_properties()

    def set_engine_properties(self, rate=180, voice_index=0):
        self.engine.setProperty('rate', rate)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[voice_index].id)

    def append_to_log(text):
        with open("chat_log.txt", "a") as f:
            f.write(text + "\n")

    def text_to_speech(self, text):
        if self.useOpenAiTTS:
            response = openAIClient.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text,
            )
            audio_data = BytesIO(response.content)
            audio = AudioSegment.from_file(audio_data)
            play(audio)
        else:
            self.engine.say(text)
            self.engine.runAndWait()

    def speech_to_text(self, audio_data):
        try:
            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

    def chat_gpt_conversation(self, text):
        # self.append_to_log(f"User: {text}")
        print(f"You said: {text}")
        self.conversation.append({'role': 'user', 'content': text})
        if len(self.conversation) > 5:  # Keep the last 5 exchanges
            self.conversation = self.conversation[-5:]
        response = openAIClient.chat.completions.create(
            model=self.model_id,
            messages=self.conversation,
            max_tokens=50
        )
        reply = response.choices[0].message.content.strip()
        self.conversation.append({'role': 'assistant', 'content': reply})
        # self.append_to_log(f"Jarvis: {reply}")
        print(f"Jarvis: {reply}")

        api_usage = response.usage
        print('\n\t ** Total token consumed: {0} **\n'.format(api_usage.total_tokens))

        return reply

    def listen_for_command(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            return audio

    def clear_log_file(self):
        open(self.log_file, 'w').close()

    def append_to_log(self, text):
        with open(self.log_file, 'a') as f:
            f.write(text + "\n")
    
    def handle_conversation(self):
        while True:
            print("Say something to start the conversation")
            self.conversation.append({'role': 'system', 'content': self.GPTinitialMessage})
            while True:
                audio_data = self.listen_for_command()
                text = self.speech_to_text(audio_data)
                if text:
                    response = self.chat_gpt_conversation(text)
                    self.text_to_speech(response)

def main():
    SpeechBuddyVoiceAssistant(
        useOpenAiTTS=True, 
        GPTinitialMessage="Chat with me as if you are a grammatical correcting assistant. your name is speech buddy. start the cobersation with introducing your self"
        ).handle_conversation()

if __name__ == "__main__":
    main()
