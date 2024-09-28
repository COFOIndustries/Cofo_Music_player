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
loop_song = False  # New variable for looping functionality
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
    global is_playing, loop_song
    is_playing = True  # Playback is active

    try:
        while is_playing:  # Keep playing as long as the song is playing
            if offline:
                file_path = download_song(video_url)
                process = subprocess.Popen(['mpv', '--no-video', f'--volume={volume}', file_path])
            else:
                process = subprocess.Popen(['mpv', '--no-video', f'--volume={volume}', video_url])

            process.wait()  # Wait for song to complete
            
            if not loop_song:  # If loop is disabled, stop replaying
                break

    except Exception as e:
        logging.error(f"Error during playback: {str(e)}")
    finally:
        is_playing = False  # Playback is no longer active when song or loop finishes

# Play next song in playlist
def play_next_song(auto_stream=False):
    global playlist
    if playlist:
        next_song = playlist.pop(0)
        user_data["playlist"] = playlist
        save_user_data()
        window.Element('playlist').update(user_data["playlist"])  # Refresh the playlist UI

        # Play song in a new thread
        threading.Thread(target=play_song, args=(next_song, user_data["volume"]), daemon=True).start()

        if auto_stream:  # Auto-queue next song if auto-streaming is active
            threading.Thread(target=check_and_autostream, daemon=True).start()

# Stop playback
def stop_playback():
    global is_playing
    is_playing = False
    subprocess.run(['pkill', 'mpv'])
    logging.info("Playback stopped.")

# Handle play button
def handle_play(values):
    global loop_song
    song_name = values['song_input']
    offline_mode = values['offline_mode']
    volume = values['volume']
    user_data["volume"] = volume
    save_user_data()

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

# GUI management
def create_gui():
    load_user_data()
    sg.theme(user_data.get("theme", "DarkAmber"))
    
    layout = [
        [sg.Text('Enter the name of the song you want to play:')],
        [sg.InputText(key='song_input')],
        [sg.Button('Play'), sg.Button('Pause'), sg.Button('Stop'), sg.Button('Next')],
        [sg.Text('Volume:'), sg.Slider(range=(0, 100), default_value=user_data.get("volume", 50), orientation='h', size=(40, 15), key='volume')],
        [sg.Checkbox('Offline Mode', key='offline_mode', default=False)],
        [sg.Checkbox('Loop Song', key='loop_song', default=False)],  # New loop option
        [sg.Listbox(values=user_data.get("playlist", []), size=(50, 10), key='playlist')],
        [sg.Button('Add to Playlist'), sg.Button('Clear Playlist')],
        [sg.Output(size=(50, 10))],
        [sg.Button('Exit'), sg.Button('Change Theme')]
    ]

    global window
    window = sg.Window('Cofo Music Player', layout)
    
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

        if event == 'Next':
            play_next_song()

        if event == 'Add to Playlist':
            song_name = values['song_input']
            video_url = search_song(song_name)
            if video_url:
                playlist.append(video_url)
                print(f"Added {video_url} to playlist.")
                user_data["playlist"] = playlist
                save_user_data()
            else:
                print("Song not found, please try again.")

        if event == 'Clear Playlist':
            playlist.clear()
            print("Playlist cleared.")
            user_data["playlist"] = playlist
            save_user_data()

        if event == 'Change Theme':
            theme = sg.popup_get_text('Enter Theme (DarkAmber, LightBlue, etc.):')
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
        loop_song = values['loop_song']

    window.close()

# Run the GUI
if __name__ == "__main__":
    create_gui()
