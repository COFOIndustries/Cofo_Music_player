                                                  # Cofo Music Player

## Overview

The **Cofo Music Player** is a Python-based music player that allows users to search, stream, and download music directly from YouTube. It features a clean and simple graphical user interface (GUI) built with `PySimpleGUI` and supports both online streaming and offline playback. Songs can be added to a playlist, looped, and cached for future offline use.

                          ## Features

- **YouTube Search**: Search for music by song name and stream it directly from YouTube.
- **Offline Mode**: Download songs using `yt-dlp` and store them locally for offline playback.
- **Playlist Management**: Add, clear, and manage your playlist.
- **Loop Songs**: Loop the currently playing song.
- **Customizable Volume**: Adjust the playback volume via a slider in the GUI.
- **Theming**: Switch between different color themes for the player.

                      ## Requirements

To use this music player, you'll need to install the following dependencies:

```plaintext
PySimpleGUI==4.60.1
yt-dlp==2023.7.6
youtubesearchpython==1.6.5




You can install these dependencies using the provided requirements.txt file:


                      How to Use

    Clone the repository.
    Install the dependencies using : pip install -r requirements.txt

    Run the cofo_music_player.py script to launch the music player: python cofo_music_player.py



                    Main Window

    Search Bar: Enter the name of the song you want to play.
    Play, Pause, Stop, Next Buttons: Control song playback.
    Volume Slider: Adjust the playback volume.
    Offline Mode Checkbox: Enable or disable offline playback.
    Loop Song Checkbox: Enable looping for the current song.
    Playlist Management: Add or clear songs in your playlist.

                    Logging

Playback and error messages are logged in music_player.log for troubleshooting purposes.
License

This project is licensed under the MIT License.



### Explanation:
- **Overview**: Describes what the project does.
- **Features**: Lists the key features of the music player.
- **Requirements**: Mentions the libraries needed, connecting back to your `requirements.txt`.
- **How to Use**: Basic instructions on how to run the project.
- **Logging**: Mentions the logging feature in case of troubleshooting.
- **License**: If you're using a permissive license like MIT, it clarifies how people can use it.

Let me know if you need more details added or changed!

