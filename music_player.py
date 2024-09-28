import os
import subprocess
import PySimpleGUI as sg
import threading
import json
from youtubesearchpython import VideosSearch
import yt_dlp

# Global variables
playlist = []
current_song = None
is_playing = False
offline_mode = False
user_data = {}
cache_dir = os.path.expanduser("~/.cofo_music_cache/")
os.makedirs(cache_dir, exist_ok=True)

# Load user data
def load_user_data():
    global user_data
    try:
        with open('user_data.json', 'r') as f:
            user_data = json.load(f)
    except FileNotFoundError:
        user_data = {
            "theme": "DarkAmber",
            "volume": 50,
            "playlist": [],
            "cache": {}
        }

# Save user data
def save_user_data():
    with open('user_data.json', 'w') as f:
        json.dump(user_data, f)

# Search YouTube for a song
def search_song(query):
    search = VideosSearch(query, limit=1)
    results = search.result()['result']
    if results:
        video_url = results[0]['link']
        return video_url
    return None

# Download a song for offline playback using yt-dlp
def download_song(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(cache_dir, '%(id)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        file_path = os.path.join(cache_dir, f"{info['id']}.mp3")
        return file_path

# Play a song with mpv in the background
def play_song(video_url, volume):
    global is_playing, current_song
    current_song = video_url
    is_playing = True
    if offline_mode:
        file_path = download_song(video_url)
        subprocess.run(['mpv', '--no-video', f'--volume={volume}', file_path])
    else:
        subprocess.run(['mpv', '--no-video', f'--volume={volume}', video_url])
    is_playing = False

# Play the next song in the playlist
def play_next_song():
    if playlist:
        next_song = playlist.pop(0)
        user_data["playlist"] = playlist
        save_user_data()
        threading.Thread(target=play_song, args=(next_song, user_data["volume"])).start()

# Stop playback
def stop_playback():
    global is_playing
    is_playing = False
    subprocess.run(['pkill', 'mpv'])

# Create the GUI
def create_gui():
    load_user_data()
    sg.theme(user_data["theme"])

    layout = [
        [sg.Text('Enter the name of the song you want to play:')],
        [sg.InputText(key='song_input')],
        [sg.Button('Play'), sg.Button('Pause'), sg.Button('Stop'), sg.Button('Next')],
        [sg.Text('Volume:'), sg.Slider(range=(0, 100), default_value=user_data["volume"], orientation='h', size=(40, 15), key='volume', enable_events=True)],
        [sg.Checkbox('Offline Mode', key='offline_mode', default=False)],
        [sg.Text('Playlist:'), sg.Listbox(values=user_data.get("playlist", []), size=(50, 10), key='playlist')],
        [sg.Button('Add to Playlist'), sg.Button('Clear Playlist')],
        [sg.Output(size=(50, 10))],
        [sg.Button('Exit'), sg.Button('Change Theme')]
    ]

    window = sg.Window('Made by Cofo - Music Player', layout)

    while True:
        event, values = window.read(timeout=100)
        
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            stop_playback()
            break

        if event == 'Play':
            song_name = values['song_input']
            offline_mode = values['offline_mode']
            volume = values['volume']
            user_data["volume"] = volume
            save_user_data()

            print(f"Searching for {song_name}...")
            video_url = search_song(song_name)

            if video_url:
                print(f"Playing: {video_url}")
                playlist.insert(0, video_url)  # Play immediately
                user_data["playlist"] = playlist
                save_user_data()
                threading.Thread(target=play_song, args=(video_url, volume)).start()
            else:
                print("Song not found, please try again.")

        if event == 'Pause':
            if is_playing:
                subprocess.run(['pkill', '-STOP', 'mpv'])
            else:
                subprocess.run(['pkill', '-CONT', 'mpv'])

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

        # Update volume
        if event == 'volume':
            volume = values['volume']
            user_data["volume"] = volume
            save_user_data()

    window.close()

# Run the GUI
if __name__ == "__main__":
    create_gui()
