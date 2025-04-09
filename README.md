# HeartSync Music Player 🎵❤️
**HeartSync** is an intelligent music playback system that dynamically recommends different styles of music that match the user's mood/exercise state by monitoring the user's heart rate and heart rate variability (HRV) in real time. The front end provides an elegant player interface, and the back end implements biofeedback-driven playback based on Bluetooth heart rate devices.

## Main features ✨
- **Real-time analysis of biological data**
Connect the heart rate belt/Chest Strap via Bluetooth, calculate HRV every 30 heartbeats, and intelligently identify 6 physiological states
- **Dynamic music recommendation**
Access Deezer API, automatically switch 6 music genres such as Rap/Jazz/Dance according to the state
- **Immersive playback experience**
Responsive web player supports playback control, volume adjustment, and playlist management
- **Intelligent anti-shake mechanism**
New tracks are locked for 30 seconds to avoid frequent switching affecting the experience
- **Multi-threaded architecture**
Asynchronous Bluetooth communication + independent control thread to ensure smooth operation

## Technology stack 🛠️
**Front-end**
- Material Design icon system
- Adaptive CSS layout
- Visual progress bar/volume control

**Back-end**
- Bleak (Bluetooth BLE communication)
- VLC (cross-platform audio playback)
- Deezer API (music library access)
- NumPy (HRV algorithm calculation)

## Quick Start 🚀
### Prerequisites
- Python 3.9+
- VLC media player
- Bluetooth heart rate monitoring device (Huawei band9 can be used to enable the heart rate broadcast function)

- Here is the demo video to show basic function : https://www.youtube.com/watch?v=HmnCV0jZlmw
