from flask import Flask, render_template
from flask_socketio import SocketIO
import speech_recognition as sr
import pyttsx3
import mail
import weather
import video
import scraping
import os
import reminder
import internet
import re

state = 1

# Initialize recognizer
recognizer = sr.Recognizer()

# speech recognition instance
r = sr.Recognizer()

# Initialize the engine
def speak_text(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()

def speech():
    global state
    try:
        # Use the microphone as the source for input
        with sr.Microphone() as source:
            # Wait for a second to let the recognizer adjust the energy threshold based on the surrounding noise level
            r.adjust_for_ambient_noise(source, duration=0.2)
            print("Listening...")
            socketio.emit("listening_mic")
            # Listens for the user's input
            audio = r.listen(source, timeout=None)
            print("Processing...")
            socketio.emit("processing_mic")
            # Using Google to recognize audio
            text = r.recognize_google(audio)
            if state == 2:
                text = 'break'
                state = 1
            text = text.lower()
            if 'break' in text:
                print()
            else:    
                print(text)
                socketio.emit("all_in_one_update_transcription",text)
            return text

    #keyboard interrupt to stop the speech engine
    except KeyboardInterrupt:
        print('A KeyboardInterrupt encountered; Terminating the Program !!!')
        socketio.emit("all_in_one_update_transcription", "A KeyboardInterrupt encountered; Terminating the Program !!!")
        exit(0)
    except sr.RequestError as e:
        print("Could not request results: {0}".format(e))
        socketio.emit("all_in_one_update_transcription", "Could not request results: {0}".format(e))
    except sr.UnknownValueError:
        pass

def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    try:
        return int(textnum)
    except ValueError:
        pass

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('stop_listening')
def fn():
    socketio.emit("processing_mic")
    state = 2

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('start_listening')
def start_listening():
    # Python speech recognition logic here
    while True:
        
        if internet.check_internet_connection():
            socketio.emit("internet_connection_true")
        else:
            socketio.emit("internet_connection_false")
        
        text = speech()

        try:
            if state == 2:
                break

            if 'oxy' in text:
                keyword_detected = True
                while keyword_detected:

                    if 'compose' in text or 'send' in text:
                        print("Who will be the recipient of this mail?")
                        socketio.emit("all_in_one_update_transcription", "Who will be the recipient of this mail?")
                        speak_text("Who will be the recipient of this mail?")
                        name = speech()
                        recipient_email = mail.get_email_from_database(name, 'email_database.txt')
                        if recipient_email:
                            print("What is the subject of the mail?")
                            socketio.emit("all_in_one_update_transcription", "What is the subject of the mail?")
                            speak_text("What is the subject of the mail?")
                            subject = speech()
                            print("What will be the content of the mail?")
                            socketio.emit("all_in_one_update_transcription", "What will be the content of the mail?")
                            speak_text("What will be the content of the mail?")
                            content = speech()
                            mail.send_email(recipient_email, subject, content)
                            print("Email sent successfully!")
                            socketio.emit("all_in_one_update_transcription", "Email sent successfully!")
                            speak_text("Email sent successfully!")
                        else:
                            print("Recipient not found in the database.")
                            socketio.emit("all_in_one_update_transcription", "Recipient not found in the database.")
                            speak_text("Recipient not found in the database.")
                    
                    elif 'weather' in text or 'temperature' in text or 'humidity' in text or 'wind speed' in text:
                        print("Kindly provide the location")
                        socketio.emit('all_in_one_update_transcription', 'Kindly provide the location')
                        speak_text("Kindly provide the location")
                        location = speech()
                        location, temperature, precipitation, humidity, wind_speed, wind_direction = weather.get_weather(location)
                        print(f"Weather in {location}:")
                        print(f"Temperature: {temperature}°C")
                        print(f"Precipitation: {precipitation} mm")
                        print(f"Humidity: {humidity}%")
                        print(f"Wind Speed: {wind_speed} m/s")
                        print(f"Wind Direction: {wind_direction}°")
                        weatherList = {"location": location,
                                        "temperature": temperature,
                                        "precipitation": precipitation,
                                        "humidity": humidity,
                                        "windSpeed": wind_speed,
                                        "windDirection": wind_direction,
                                    }
                        socketio.emit("all_in_one_update_transcription", weatherList)
                        speak_text(f"Weather in {location} Temperature: {temperature}°C, Precipitation: {precipitation} mm, Humidity: {humidity}%")
                        speak_text(f"Wind Speed: {wind_speed} meters per second, Wind Direction: {wind_direction}°")

                    elif 'play' in text:
                        print("Kindly provide the title")
                        socketio.emit("all_in_one_update_transcription", "Kindlly provide the title")
                        speak_text("Kindly provide the title")
                        title = speech()
                        print("Playing Video...")
                        socketio.emit("all_in_one_update_transcription", "Playing Video")
                        speak_text("Playing Video")
                        video.play_video(title)

                    elif 'list' in text:
                        while True:
                            print("What is the name of the list?")
                            socketio.emit("all_in_one_update_transcription", "What is the name of the list?")
                            speak_text("What is the name of the list?")
                            list_name = speech()
                            try:
                                if os.path.exists(list_name + ".txt"):
                                    print("List already exists.")
                                    socketio.emit("all_in_one_update_transcription", "List already exists.")
                                    speak_text("List already exists.")
                                    print("What would you like to do?")
                                    socketio.emit("all_in_one_update_transcription", "What would you like to do?")
                                    speak_text("What would you like to do?")
                                    text = speech()
                                    if 'add' in text:
                                        print("Name the item to be added to the list.")
                                        socketio.emit("all_in_one_update_transcription", "Name the item to be added to the list.")
                                        speak_text("Name the item to be added to the list.")
                                        item = speech()
                                        with open(list_name + ".txt", "a") as f:
                                            f.write(item + "\n")
                                            print("Item added successfully!")
                                            socketio.emit("all_in_one_update_transcription", "Item added successfully!")
                                            speak_text("Item added successfully!")
                                        print("The list is currently: ")
                                        socketio.emit("all_in_one_update_transcription", "The list is currently: ")
                                        speak_text("The list is currently: ")
                                        with open(list_name + ".txt", "r") as f:
                                            print(f.read())
                                            socketio.emit("all_in_one_update_transcription", f.read())
                                            speak_text(f.read())
                                            break
                                    elif 'remove' in text:
                                        print("Name the item to be removed from the list.")
                                        socketio.emit("all_in_one_update_transcription", "Name the item to be removed from the list.")
                                        speak_text("Name the item to be removed from the list.")
                                        item = speech()
                                        with open(list_name + ".txt", "r") as f:
                                            lines = f.readlines()
                                        with open(list_name + ".txt", "w") as f:
                                            for line in lines:
                                                if line.strip("\n") != item:
                                                    f.write(line)
                                            print("Item removed successfully!")
                                            socketio.emit("all_in_one_update_transcription", "Item removed successfully!")
                                            speak_text("Item removed successfully!")
                                        print("The list is currently: ")
                                        socketio.emit("all_in_one_update_transcription", "The list is currently: ")
                                        speak_text("The list is currently: ")
                                        with open(list_name + ".txt", "r") as f:
                                            print(f.read())
                                            socketio.emit("all_in_one_update_transcription", f.read())
                                            speak_text(f.read())
                                            break
                                    elif 'display' in text or 'show' in text:
                                        print("The list is currently: ")
                                        socketio.emit("all_in_one_update_transcription", "The list is currently: ")
                                        speak_text("The list is currently: ")
                                        with open(list_name + ".txt", "r") as f:
                                            print(f.read())
                                            socketio.emit("all_in_one_update_transcription", f.read())
                                            speak_text(f.read())
                                            break
                                    elif 'delete' in text:
                                        os.remove(list_name + ".txt")
                                        print("List has been deleted")
                                        socketio.emit("all_in_one_update_transcription", "List has been deleted")
                                        speak_text("List has been deleted")
                                        break
                                    else:
                                        print("Could not recognise command!")
                                        socketio.emit("all_in_one_update_transcription", "Could not recognise command!")
                                        speak_text("Could not recognise command!")
                                        continue
                                else:
                                    with open(list_name + ".txt", "w") as f:
                                        print("New list created.")
                                        socketio.emit("all_in_one_update_transcription", "New list created.")
                                        speak_text("New list created.")
                                    print("How many items would you like to add?")
                                    socketio.emit("all_in_one_update_transcription", "How many times would you like to add?")
                                    speak_text("How many items would you like to add?")
                                    number = speech()
                                    count = text2int(number)
                                    for i in range(count):
                                        print("Name the item to be added to the list.")
                                        socketio.emit("all_in_one_update_transcription", "Name the item to be added to the list.")
                                        speak_text("Name the item to be added to the list.")
                                        item = speech()
                                        with open(list_name + ".txt", "a") as f:
                                            f.write(item + "\n")
                                    print("Items added successfully!")
                                    socketio.emit("all_in_one_update_transcription", "Items added successfully!")
                                    speak_text("Items added successfully!")
                                    with open(list_name + ".txt", "r") as f:
                                        print(f.read())
                                        socketio.emit("all_in_one_update_transcription", f.read())
                                        speak_text(f.read())
                                        break
                            except:
                                pass

                    elif 'search' in text or 'what' in text or 'who' in text:
                        print("What/Who are you looking for?")
                        socketio.emit("all_in_one_update_transcription", "What/Who are you looking for?")
                        speak_text("What/Who are you looking for?")
                        query = speech()
                        print(f"Results for {query}: ")
                        socketio.emit("all_in_one_update_transcription", "Results for " + query + ": ")
                        text = scraping.search_wikipedia(query)
                        text = re.sub(r'\s*\([^)]*\)\s*', ' ', text)
                        print(text)
                        socketio.emit("all_in_one_update_transcription", text)
                        text = text[:250]
                        speak_text(text)

                    elif 'remind' in text or 'alarm' in text:
                        while True:
                            print("Would you like to be reminded hours/minutes/seconds later?")
                            socketio.emit("all_in_one_update_transcription", "Would you like to be reminded hours/minutes/seconds later?")
                            speak_text("Would you like to be reminded hours/minutes/seconds later?")
                            format = speech()
                            try:
                                if format == 'hours':
                                    print("How many hours later?")
                                    socketio.emit("all_in_one_update_transcription", "How many hours later?")
                                    speak_text("How many hours later?")
                                    number = speech()
                                    count = text2int(number)
                                    seconds = count*60*60
                                    print("What would you like to be reminded of?")
                                    socketio.emit("all_in_one_update_transcription", "What would you like to be reminded of?")
                                    speak_text("What would you like to be reminded of?")
                                    text = speech()
                                    reminder.timer(text, seconds)
                                    break
                                elif format == 'minutes':
                                    print("How many minutes later?")
                                    socketio.emit("all_in_one_update_transcription", "How many minutes later?")
                                    speak_text("How many minutes later?")
                                    number = speech()
                                    count = text2int(number)
                                    seconds = count*60
                                    print("What would you like to be reminded of?")
                                    socketio.emit("all_in_one_update_transcription", "What would you like to be reminded of?")
                                    speak_text("What would you like to be reminded of?")
                                    text = speech()
                                    reminder.timer(text, seconds)
                                    break
                                elif format == 'seconds':
                                    print("How many seconds later?")
                                    socketio.emit("all_in_one_update_transcription", "How many seconds later?")
                                    speak_text("How many seconds later?")
                                    number = speech()
                                    count = text2int(number)
                                    seconds = count
                                    print("What would you like to be reminded of?")
                                    socketio.emit("all_in_one_update_transcription", "What would you like to be reminded of?")
                                    speak_text("What would you like to be reminded of?")
                                    text = speech()
                                    reminder.timer(text, seconds)
                                    break
                                else:
                                    print("Could not understand the time format. Try again!")
                                    socketio.emit("all_in_one_update_transcription", "Could not understand the time format. Try again!")
                                    speak_text("Could not understand the time format. Try again!")
                                    pass
                            except:
                                pass

                    else:
                        print("Command not recognised")
                        socketio.emit("all_in_one_update_transcription", "Command not recognised")
                        speak_text("Command not recognised")

                    keyword_detected = False
            
            
            if 'stop' in text or 'break' in text:
                break

        except:
            pass
        pass
        

if __name__ == '__main__':
    socketio.run(app, debug=True)