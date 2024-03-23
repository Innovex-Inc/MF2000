import pyttsx3 as pyttsx
import speech_recognition as sr
from youtube_search import YoutubeSearch
import webbrowser
import openai
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import random
import os
from datetime import datetime

engine = pyttsx.init()
openai.api_key = "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"

def transcribe_audio_to_text(audio):
    recognizer = sr.Recognizer()
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    return ""

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def play_music_from_youtube(query):
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        video_url = "https://www.youtube.com" + results[0]['url_suffix']
        webbrowser.open(video_url)
    except Exception as e:
        print("Error playing music from YouTube:", e)

def generate_response(prompt):
    response = openai.Completion.create(
        engine="davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def get_joke():
    # API endpoint to fetch jokes
    url = "https://official-joke-api.appspot.com/jokes/random"
    try:
        response = requests.get(url)
        data = response.json()
        if 'setup' in data and 'punchline' in data:
            return data['setup'], data['punchline']
    except Exception as e:
        print("Error fetching joke:", e)
    return None, None

def get_therapy_response():
    responses = [
        "How does that make you feel?",
        "Tell me more about that.",
        "What do you think is the root cause of that?",
        "Have you considered talking to someone about this?",
        "Let's explore that further.",
        "Do you think this is a recurring issue?"
    ]
    return random.choice(responses)

def get_bedtime_story():
    # Fetch bedtime stories from an alternative website
    url = "https://www.storynory.com/category/stories/"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        stories = soup.find_all('h2', class_='entry-title')

        # Extract story titles
        story_titles = [story.text.strip() for story in stories]

        return random.choice(story_titles)
    except Exception as e:
        print("Error fetching bedtime story:", e)
        return None

def converse():
    speak_text("Hello! How are you today?")
    while True:
        print("Listening for command...")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.energy_threshold = 500
            recognizer.dynamic_energy_threshold = False
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
            try:
                user_input = transcribe_audio_to_text(audio)
                if user_input:
                    print("You said:", user_input)
                    if "exit" in user_input.lower():
                        speak_text("Goodbye!")
                        return
                    elif "write essay" in user_input.lower():
                        speak_text("What's the topic for the essay?")
                        audio = recognizer.listen(source)
                        essay_prompt = transcribe_audio_to_text(audio)
                        print("Essay prompt:", essay_prompt)
                        essay = generate_response(essay_prompt)
                        if essay:
                            speak_text(essay)
                    elif "search Google" in user_input.lower():
                        search_google(user_input)
                    elif "tell joke" in user_input.lower():
                        setup, punchline = get_joke()
                        if setup and punchline:
                            joke = f"{setup}. {punchline}"
                            speak_text(joke)
                        else:
                            speak_text("Sorry, I couldn't fetch a joke at the moment.")
                    elif "therapy" in user_input.lower():
                        speak_text(get_therapy_response())
                    elif "bedtime story" in user_input.lower():
                        story = get_bedtime_story()
                        if story:
                            speak_text(story)
                    else:
                        response = generate_response(user_input)
                        if response:
                            speak_text(response)
                else:
                    print("Failed to transcribe audio. Please try again.")
            except Exception as e:
                print('An error occurred:', e)

def search_google(query):
    speak_text("Searching Google for " + query)
    try:
        for j in search(query, num=1, stop=1, pause=2):
            webbrowser.open(j)
            break
    except Exception as e:
        print("Error searching Google:", e)

def main():
    speak_text("Welcome! I'm ready to assist you.")
    try:
        while True:
            print("Listening for command...")
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.energy_threshold = 1000
                recognizer.dynamic_energy_threshold = False
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source)
                try:
                    transcription = transcribe_audio_to_text(audio)
                    if transcription:
                        print("You said:", transcription)
                        if "play music" in transcription.lower():
                            print("What music do you want to play?")
                            speak_text("What music do you want to play?")
                            audio = recognizer.listen(source)
                            query = transcribe_audio_to_text(audio)
                            print("Playing music:", query)
                            speak_text("Playing music: " + query)
                            play_music_from_youtube(query)
                        elif "converse" in transcription.lower():
                            converse()
                        elif "exit" in transcription.lower():
                            print("Exiting the program.")
                            speak_text("Goodbye! Take care of yourself.")
                            return
                    else:
                        print("Failed to transcribe audio. Please try again.")
                except Exception as e:
                    print('An error occurred:', e)
    finally:
        print("Transcript saved.")

if __name__ == "__main__":
    main()
