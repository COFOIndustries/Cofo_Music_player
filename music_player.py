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
current_song = None
is_playing = False
loop_song = False
loop_count = 0
user_data = {}

# ASCII art for COFO branding
COFO_ASCII = r"""
  ____    ____   ______   ______ 
 |    \  /    | /  __  \ |      \
 |  _  \/  _  ||  |  |  ||  ||  |
 |  ||  ||  || ||  |  |  ||  ||  |
 |__| \__|__|__||__|  |__||______|
"""

# Load and save user data
def load_user_data():
    global user_data
    try:
        with open(USER_DATA_PATH, 'r') as f:
            user_data = json.load(f)
    except FileNotFoundError:
        logging.warning("User data file not found, creating default settings.")
        user_data = {
            "theme": "White",
            "volume": 50,
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

            # Check if looping is enabled
            if not loop_song:
                break  # Exit loop if looping is disabled

            loop_count += 1
            logging.info(f"Looped {loop_count} times")
            window['loop_count'].update(f"Looped {loop_count} times")

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
    volume = int(values['volume'])  # Convert to integer for compatibility
    user_data["volume"] = volume
    save_user_data()

    loop_count = 0  # Reset loop count when playing a new song
    window['loop_count'].update(f"Looped {loop_count} times")  # Reset loop count display

    if song_name:
        print(f"Searching for {song_name}...")
        video_url = search_song(song_name)

        if video_url:
            print(f"Playing: {video_url}")
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
    sg.theme('SystemDefault')

    layout = [
        [sg.Text(COFO_ASCII, font=("Courier", 14), justification='center')],
        [sg.Text('Enter the name of the song you want to play:')],
        [sg.InputText(key='song_input')],
        [sg.Button('Play'), sg.Button('Pause'), sg.Button('Stop')],
        [sg.Text('Volume:'), sg.Slider(range=(0, 100), default_value=user_data.get("volume", 50), orientation='h', size=(40, 15), key='volume')],
        [sg.Checkbox('Offline Mode', key='offline_mode', default=False)],
        [sg.Checkbox('Loop Song', key='loop_song', default=False)],  # Loop option
        [sg.Text('Loop Count: 0', key='loop_count')],  # Text element for loop count
        [sg.Output(size=(50, 10))],
        [sg.Button('Exit'), sg.Button('Change Theme')]
    ]

    global window
    window = sg.Window('COFO Music Player', layout)

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

        if event == 'Change Theme':
            theme = sg.popup_get_text('Enter Theme (White, Black, etc.):')
            if theme:
                user_data["theme"] = theme
                save_user_data()
                sg.theme(theme)
                window.close()
                create_gui()

        if event == 'volume':
            user_data["volume"] = values['volume']
            save_user_data()

        # Update the loop_song variable based on checkbox
        global loop_song
        loop_song = values['loop_song']

    window.close()

# Run the GUI
if __name__ == "__main__":
    create_gui()
