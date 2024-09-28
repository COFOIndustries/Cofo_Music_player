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
