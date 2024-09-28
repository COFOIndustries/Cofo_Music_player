import os
import subprocess
import PySimpleGUI as sg
from youtubesearchpython import VideosSearch

# Function to search YouTube for a song
def search_song(query):
    search = VideosSearch(query, limit=1)
    results = search.result()['result']
    if results:
        video_url = results[0]['link']
        return video_url
    return None

# Function to play the song using mpv (via youtube-dl stream)
def play_song(video_url):
    # Use mpv to stream the audio
    subprocess.run(['mpv', '--no-video', video_url])

# Build the simple UI with PySimpleGUI
def create_gui():
    layout = [
        [sg.Text('Enter the name of the song you want to play:')],
        [sg.InputText(key='song_input')],
        [sg.Button('Play'), sg.Button('Exit')],
        [sg.Output(size=(50,10))]
    ]

    window = sg.Window('Made by Cofo - Music Player', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break

        if event == 'Play':
            song_name = values['song_input']
            print(f"Searching for {song_name}...")
            video_url = search_song(song_name)

            if video_url:
                print(f"Playing: {video_url}")
                play_song(video_url)
            else:
                print("Song not found, please try again.")

    window.close()

# Run the GUI
if __name__ == "__main__":
    create_gui()
