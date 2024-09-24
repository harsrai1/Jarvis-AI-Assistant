import pyttsx3
import speech_recognition as sr
import openai
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import pywhatkit
import subprocess
import requests
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


# Initializing pyttsx3
engine = pyttsx3.init()

# Set your OpenAI API key and customize the ChatGPT role
openai.api_key = "openai_API _key"
messages = [{"role": "system", "content": "Your name is Jarvis and give answers in 2 lines"}]

# Customizing the output voice
voices = engine.getProperty('voices')
rate = engine.getProperty('rate')
volume = engine.getProperty('volume')

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id='d19b91d462b244f3aacaeb081eb11187',
                                                                              client_secret='06b7599e3f9847ff83600cbf6827dc7e'))

def get_response(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wish_me():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am Jarvis Sir. Please tell me how may I help you")



def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

        # Log the user's query to a text file
        with open('conversation_log.txt', 'a') as file:
            file.write(f"User: {query}\n")

        # Check for weather command
        if 'weather' in query:
            speak("Sure, please tell me the name of the city.")
            city = take_command()  # Let the user provide the city name
            weather_data = get_weather(city)  # You need to implement get_weather function
            speak(weather_data)
            return "Weather data fetched."

        # Check for coding commands
        elif 'write code' in query:
            speak("Sure, I'll help you write some code. What specific functionality would you like the code to perform?")
            user_input = take_command()  # You may need to implement this function to capture user speech input
            response = get_response(user_input)  # You need to implement get_response function
            code = response.replace("\n", "")  # Removing newline characters for simplicity
            speak("Here's the generated code:")
            print(code)

            # Prompt user for file name
            speak("What would you like to name the file?")
            file_name = take_command()
            file_name += ".java"  # Assuming Java file for simplicity, you can adjust based on the language
            
            # Write code to the file
            with open(file_name, "w") as file:
                file.write(code)
            speak(f"The code has been saved to {file_name}")
            
            # Open the file in VS Code
            speak("Would you like to open the file in VS Code?")
            response = take_command().lower()
            if 'yes' in response:
                vscode_path = r'C:\Users\Harsh Rai\AppData\Local\Programs\Microsoft VS Code\Code.exe'
                subprocess.Popen([vscode_path, file_name])

            return "Code written successfully."

        # Check for searching on Google command
        elif 'search on google' in query:
            speak("What do you want to search on Google?")
            search_query = take_command()
            if search_query != 'None':
                speak(f"Searching Google for {search_query}")
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
        elif 'search on youtube' in query:
            speak("What do you want to search on YouTube?")
            search_query = take_command()
            if search_query != 'None':
                speak(f"Searching YouTube for {search_query}")
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
    except Exception as e:
        print(e)
        print("Say that again please...")
        return "None"
    return query

def get_weather(city):
    # OpenWeatherMap API endpoint and API key
    api_key = "0cb3f8dee58f809a38f00c25573fb9e2"
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    # Fetching weather data
    try:
        response = requests.get(base_url)
        data = response.json()
        if data["cod"] != "404":
            main_data = data["main"]
            temperature = main_data["temp"]
            description = data["weather"][0]["description"]
            weather_data = f"The temperature in {city} is {temperature} degrees Celsius with {description}."
            return weather_data
        else:
            return "City not found."

    except Exception as e:
        print(e)
        return "Sorry, something went wrong while fetching the weather data."



def send_email_web(to, subject, content):
    # Compose the mailto URL
    mailto_url = f"mailto:{to}?subject={subject}&body={content}"

    # Open the web browser with the pre-filled email composition form
    webbrowser.open(mailto_url)

def get_news():
    api_key = "sk-proj-5cJLmj1xTZBiy92KxTZvT3BlbkFJlKI2nckwsVN1GmsnePbz"
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    response = requests.get(url)
    news_data = response.json()
    articles = news_data['articles']
    headlines = [article['title'] for article in articles[:15]]  # Get the first 15 headlines
    return headlines

if __name__ == "__main__":
    wish_me()
    with open('conversation_log.txt', 'a') as file:
        file.write("Jarvis: I am Jarvis Sir. Please tell me how may I help you\n")
    while True:
        query = take_command().lower()

        if 'jarvis' in query:
            response_from_openai = get_response(query)
            engine.setProperty('rate', 120)
            engine.setProperty('volume', volume)
            engine.setProperty('voice', voices[0].id)  # You can set any voice here
            engine.say(response_from_openai)
            engine.runAndWait()
            with open('conversation_log.txt', 'a') as file:
                file.write(f"Jarvis: {response_from_openai}\n")
        
        elif 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)
            with open('conversation_log.txt', 'a') as file:
                file.write(f"Jarvis: According to Wikipedia\n{results}\n")
        
        elif 'send whatsapp message to' in query:
            recipient = query.split("to ")[-1]
            speak(f"What message do you want to send to {recipient}?")
            message = take_command()
            pywhatkit.sendwhatmsg_instantly(f"{recipient}", f"{message}")
            speak(f"Message sent to {recipient} successfully!")
            with open('conversation_log.txt', 'a') as file:
                file.write(f"Jarvis: Message sent to {recipient}: {message}\n")

        
        elif 'open youtube' in query:
            webbrowser.open("youtube.com")
        
        elif 'search on youtube' in query:
            speak("What do you want to search on YouTube?")
            search_query = take_command()
            if search_query != 'None':
                speak(f"Searching YouTube for {search_query}")
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
        
        elif 'open google' in query:
            webbrowser.open("google.com")
        
        elif 'search on google' in query:
             speak("What do you want to search on Google?")
             search_query = take_command()
             if search_query != 'None':
                speak(f"Searching Google for {search_query}")
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
        
        elif 'open stackoverflow' in query:
            webbrowser.open("stackoverflow.com")
        
        elif 'ufc match' in query:
            webbrowser.open("https://www.youtube.com/watch?v=w9HRy4NtGxk")
        
        elif 'music' in query:
            music_file = r'C:\music\levels.mp3'
            if os.path.exists(music_file):
                os.startfile(music_file)
        
        elif 'the time' in query:
            str_time = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {str_time}")
        


    
        elif 'email to ajay' in query:
          try:
            speak("What should be the subject of the email?")
            subject = take_command()
            speak("What should I say in the email?")
            content = take_command()
            to = "harsrai89@gmail.com"  # Update with Harry's email address
            send_email_web(to, subject, content)
            speak("Email composition opened in your web browser!")
          except Exception as e:
            print(e)
            speak("Sorry my friend hars. I am not able to open the email composition")

        
        elif "latest news" in query or "last two days news" in query:
            speak("Sure, here are the latest news headlines:")
            headlines = get_news()
            for idx, headline in enumerate(headlines, start=1):
                speak(f" {idx}: {headline}")
                if idx == 15 or 'exit' in query:  # Exit after reading 15 headlines or if 'exit' is in the query
                    break
        
        elif "play song" in query:
            speak("Sure, which song would you like me to play?")
            song_name = take_command()
            print("Searching for:", song_name)
            results = spotify.search(q=song_name, type='track')
            if len(results['tracks']['items']) > 0:
                song_uri = results['tracks']['items'][0]['uri']
                # Open the Spotify URI in a web browser
                webbrowser.open(song_uri)
            else:
                speak("Sorry, I couldn't find that song.")
        elif 'exit' in query:
            speak("Exiting. Goodbye!")
            break
            
       