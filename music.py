import asyncio
from bleak import BleakClient
import random
import vlc
import time
import threading
import requests
import numpy as np
import datetime

# Bluetooth device MAC address
mac_address = "C0:CD:12:E4:37:44"

# Global player variable
player = None
running = True  # Global flag to control program execution
current_genre = None  # Track the current genre
last_play_time = None  # Track the last time a song was played
lock_genre = False  # Flag to lock genre for 30 seconds

# Heart rate data storage
heart_rate_data = []  # Temporary storage for the current batch of heart rates
heart_rate_groups = []  # List to store groups of 30 heart rates

# Current HRV value
current_hrv = 50  # Initial placeholder value

# Mapping heart rate and states to music genres
genre_mapping = {
    "Intense exercise": "Rap/Hip Hop",
    "Relaxed or calm": "Jazz",
    "Light exercise": "Dance",
    "Fatigued or low activity": "Blues",
    "Stressed": "Classical",
    "Excited": "Pop"
}

# Function to infer states
def analyze_state(heart_rate, hrv):
    """
    Infer user's emotional and activity state based on heart rate and HRV
    """
    # state determination
    if heart_rate > 150 and hrv > 30:
        state = "Intense exercise"
    if heart_rate > 150 and hrv < 30:
        state = "Stressed"
    elif 100 < heart_rate < 150 and hrv > 30:
        state = "Light exercise"
    elif 100 < heart_rate < 150 and hrv < 30:
        state = "Excited"
    elif 70 < heart_rate < 100:
        state = "Relaxed or calm"
    else:
        state = "Fatigued or low activity"

    return state

# Function to calculate HRV (using RMSSD method)
def calculate_hrv(heart_rates):
    # Convert heart rate values to RR intervals in milliseconds
    rr_intervals = [60000 / hr for hr in heart_rates]

    # Calculate successive RR interval differences
    rr_diffs = np.diff(rr_intervals)

    # Calculate RMSSD (Root Mean Square of Successive Differences)
    rmssd = np.sqrt(np.mean(rr_diffs ** 2))

    return rmssd

# Function to get music by genre
def get_music_by_genre(genre_name):
    base_url = "https://api.deezer.com/search"
    params = {
        'q': f'genre:"{genre_name}"',
        'limit': 50
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('data'):
            return data['data']
        else:
            return "No recommended songs found."
    else:
        return f"Error: {response.status_code}"

# Function to play music
def play_music(song_url):
    global player, last_play_time, lock_genre
    # Stop previous music
    if player:
        player.stop()
    # Initialize the player and play the new song
    player = vlc.MediaPlayer(song_url)
    player.play()
    last_play_time = datetime.datetime.now()  # Update the last play time
    lock_genre = True  # Lock genre for 30 seconds

# Function to stop music playback
def stop_music():
    global player
    if player:
        player.stop()
        print("Music stopped.")

# Callback function to handle Bluetooth notifications
async def notification_handler(sender: int, data: bytearray):
    global current_genre, running, heart_rate_data, heart_rate_groups, current_hrv, lock_genre
    if len(data) > 1:
        heart_rate = data[1]

        # Store heart rate data
        heart_rate_data.append(heart_rate)
        if len(heart_rate_data) == 30:
            heart_rate_groups.append(heart_rate_data.copy())
            print(f"Stored a group of 30 heart rates: {heart_rate_groups[-1]}")
            print(f"All stored heart rate groups: {heart_rate_groups}")

            # Calculate HRV for the current group of heart rates
            current_hrv = calculate_hrv(heart_rate_data)
            heart_rate_data.clear()  # Clear the list after storing

            print(f"Calculated HRV for the current group: {current_hrv}")

        # Infer states
        state = analyze_state(heart_rate, current_hrv)

        # Automatically play music based on state
        genre_name = genre_mapping.get(state, "Classical")
        if not lock_genre:
            if genre_name != current_genre:
                current_genre = genre_name
                print(f"Switching to music genre: {genre_name}")
                songs = get_music_by_genre(genre_name)
                if isinstance(songs, list):
                    random_song = random.choice(songs)
                    song_url = random_song['preview']
                    print(f"Now playing: {random_song['title']} by {random_song['artist']['name']}")
                    play_music(song_url)
            else:
                # Check if it's time to play a new song after 30 seconds
                if last_play_time and (datetime.datetime.now() - last_play_time).total_seconds() >= 30:
                    print(f"Replaying genre: {current_genre}")
                    songs = get_music_by_genre(current_genre)
                    if isinstance(songs, list):
                        random_song = random.choice(songs)
                        song_url = random_song['preview']
                        print(f"Now playing (periodic): {random_song['title']} by {random_song['artist']['name']}")
                        play_music(song_url)
        else:
            # Unlock genre change after 30 seconds
            if last_play_time and (datetime.datetime.now() - last_play_time).total_seconds() >= 30:
                lock_genre = False

# Function to connect to Bluetooth device and subscribe to heart rate notifications
async def connect_and_read():
    global running
    async with BleakClient(mac_address) as client:
        print(f"Connected: {client.is_connected}")
        await client.start_notify("00002a37-0000-1000-8000-00805f9b34fb", notification_handler)
        try:
            while running:
                await asyncio.sleep(5)  # Sleep for a short interval to avoid busy waiting
        finally:
            await client.stop_notify("00002a37-0000-1000-8000-00805f9b34fb")
            print("Stopped notifications.")

# Threaded function to handle user input and exit the program
def handle_exit():
    global running
    while running:
        user_input = input("Type '0' to stop the program: ")
        if user_input == '0':
            print("Exiting program...")
            running = False
            stop_music()

# Main event loop
async def main():
    # Run connect_and_read concurrently
    await connect_and_read()

if __name__ == "__main__":
    # Run exit handler in a separate thread
    exit_thread = threading.Thread(target=handle_exit)
    exit_thread.daemon = True
    exit_thread.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
