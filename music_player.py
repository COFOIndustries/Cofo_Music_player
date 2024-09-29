import os
import subprocess
import PySimpleGUI as sg
import threading
import json
from youtubesearchpython import VideosSearch
import yt_dlp
import logging

# Configure logging
logging.basicConfig(filename="music_player.log", level=logging.DEBUG)

# Paths and directories
CACHE_DIR = os.path.expanduser("~/.cofo_music_cache/")
USER_DATA_PATH = "user_data.json"

# Ensure the cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

# Initialize global variables
playlist = []
current_song = None
is_playing = False
loop_song = False
loop_count = 0
user_data = {}

# Load and save user data
def load_user_data():
    global user_data
    try:
        with open(USER_DATA_PATH, 'r') as f:
            user_data = json.load(f)
    except FileNotFoundError:
        logging.warning("User data file not found, creating default settings.")
        user_data = {
            "theme": "DarkAmber",
            "volume": 50,
            "playlist": [],
            "cache": {}
        }

def save_user_data():
    with open(USER_DATA_PATH, 'w') as f:
        json.dump(user_data, f, indent=4)

# Search YouTube
def search_song(query):
    try:
        search = VideosSearch(query, limit=1)
        result = search.result()['result']
        if result:
            return result[0]['link']
    except Exception as e:
        logging.error(f"Error searching for song: {query} - {str(e)}")
    return None

# Download and cache song
def download_song(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(CACHE_DIR, '%(id)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = os.path.join(CACHE_DIR, f"{info['id']}.mp3")
            logging.info(f"Downloaded song to {file_path}")
            return file_path
    except Exception as e:
        logging.error(f"Failed to download song: {video_url} - {str(e)}")
    return None

# Play song with subprocess and handle looping
def play_song(video_url, volume, offline=False):
    global is_playing, loop_song, loop_count
    is_playing = True
    loop_count = 0  # Reset the loop count each time a new song starts playing
    
    try:
        while True:  # Keep looping if loop_song is enabled
            logging.info(f"Starting playback: {video_url}")
            if offline:
                file_path = download_song(video_url)
                if file_path:
                    process = subprocess.Popen(['mpv', '--no-video', f'--volume={volume}', file_path])
            else:
                process = subprocess.Popen(['mpv', '--no-video', f'--volume={volume}', video_url])

            process.wait()  # Wait for the song to finish

            if not loop_song:
                break  # Exit loop if looping is disabled

            loop_count += 1  # Increment loop count
            logging.info(f"Looped {loop_count} times")

    except Exception as e:
        logging.error(f"Error during playback: {str(e)}")
    finally:
        is_playing = False
        logging.info("Playback finished or stopped.")

# Handle play button
def handle_play(values):
    global loop_count
    song_name = values['song_input']
    offline_mode = values['offline_mode']
    volume = values['volume']
    user_data["volume"] = volume
    save_user_data()

    loop_count = 0  # Reset loop count when playing a new song
    if song_name:
        print(f"Searching for {song_name}...")
        video_url = search_song(song_name)

        if video_url:
            print(f"Playing: {video_url}")
            playlist.insert(0, video_url)  # Play immediately
            user_data["playlist"] = playlist
            save_user_data()

            # Play song in a new thread, avoiding blocking the GUI
            threading.Thread(target=play_song, args=(video_url, volume, offline_mode), daemon=True).start()
        else:
            print("Song not found, please try again.")

# Stop playback
def stop_playback():
    global is_playing
    is_playing = False
    subprocess.run(['pkill', 'mpv'])
    logging.info("Playback stopped.")

# GUI management
def create_gui():
    load_user_data()
    sg.theme('LightBlue')  # Set a light theme

    layout = [
        [sg.Text(' C O F O ', font=('Akira Expanded', 24), text_color='forest green', justification='center')],
        [sg.Text('Enter the name of the song you want to play:', font=('Akira Expanded', 12))],
        [sg.InputText(key='song_input', size=(40, 1), font=('Akira Expanded', 12))],
        [sg.Button('Play', button_color=('white', 'lime green'), font=('Akira Expanded', 12)),
         sg.Button('Pause', button_color=('white', 'lime green'), font=('Akira Expanded', 12)),
         sg.Button('Stop', button_color=('white', 'lime green'), font=('Akira Expanded', 12))],
        [sg.Text('Volume:', font=('Akira Expanded', 12)), 
         sg.Slider(range=(0, 100), default_value=user_data.get("volume", 50), orientation='h', size=(40, 15), key='volume')],
        [sg.Checkbox('Offline Mode', key='offline_mode', default=False, font=('Akira Expanded', 12))],
        [sg.Text('Loop Song:', font=('Akira Expanded', 12)), sg.Checkbox('', key='loop_song', default=False)],
        [sg.Output(size=(50, 10), font=('Akira Expanded', 12))],
        [sg.Button('Exit', button_color=('white', 'red'), font=('Akira Expanded', 12))]
    ]

    global window
    window = sg.Window('Cofo Music Player', layout, background_color='#A0D8D0')  # Light pastel mint blue

    while True:
        event, values = window.read(timeout=100)
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            stop_playback()
            break

        if event == 'Play':
            handle_play(values)

        if event == 'Pause':
            stop_playback()

        if event == 'Stop':
            stop_playback()

        # Update the loop_song variable based on checkbox
        loop_song = values['loop_song']

    window.close()

# Run the GUI
if __name__ == "__main__":
    create_gui()
