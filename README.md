# Web Syncplay on Raspberry Pi

This project provides a Dockerized web interface for Syncplay, allowing you to watch local video files synchronized with others over the network. It's designed to be lightweight and run on a Raspberry Pi 5 (ARM64).

## Features

-   **Web-based UI:** Access a video player and file browser from any device on your local network.
-   **Syncplay Integration:** Synchronize video playback (play, pause, seek) with other users in a Syncplay room.
-   **Local Video Files:** Mount your local video directory into the container to browse and play your media.
-   **Dockerized:** Easy to set up and run using Docker and Docker Compose.
-   **ARM64 Compatible:** Built to run on Raspberry Pi 5 and other ARM64 devices.

## Requirements

-   Raspberry Pi 5 (or any other ARM64 device)
-   Docker and Docker Compose installed.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd web-syncplay
    ```

2.  **Organize Your Media:**
    Place the video files you want to watch in a directory. For this example, we'll use a directory named `videos` in the project root.
    ```bash
    mkdir videos
    # Copy your series/movies into the videos/ directory
    # e.g., cp /media/hdd/series/my_show.mp4 ./videos/
    ```
    The `docker-compose.yml` is configured to mount `./videos` to `/app/videos` inside the container. You can change the host path (`./videos`) to any directory on your Raspberry Pi (e.g., `/media/hdd/series`).

3.  **Build and Run the Container:**
    From the project's root directory, run the following command:
    ```bash
    docker-compose up --build -d
    ```
    This will build the Docker image and start the `web-syncplay` service in the background.

4.  **Access the Web Interface:**
    Open your web browser and navigate to your Raspberry Pi's IP address on port 8000:
    `http://<your-pi-ip-address>:8000`

## How to Use

1.  **Select a Video:**
    The file browser on the left will show a list of all supported video files found in the mounted directory. Click on a file to load it into the video player.

2.  **Configure Syncplay:**
    -   **Server:** Enter the address of the Syncplay server (e.g., `syncplay.pl:8999`).
    -   **Room:** Enter the name of the room you want to join.
    -   **Username:** Choose a username.

3.  **Connect:**
    Click the "Connect" button. The application will start the Syncplay client in the background. Status messages and chat will appear in the chatbox on the right.

4.  **Watch Synchronized:**
    Once connected, your playback controls (play, pause, seek) will be synchronized with everyone else in the Syncplay room. Any actions performed by others will also be reflected in your player.

## Configuration (Environment Variables)

You can customize the Syncplay connection settings in the `docker-compose.yml` file:

-   `SYNCPLAY_SERVER`: The default Syncplay server address. (Default: `syncplay.pl:8999`)
-   `SYNCPLAY_ROOM`: The default room name. (Default: `room1`)
-   `SYNCPLAY_USERNAME`: The default username. (Default: `docker-user`)
-   `VIDEO_PATH`: The path inside the container where videos are located. This should match the container-side of the volume mount. (Default: `/app/videos`)

## Security

This application is designed for use within a trusted local network and has no authentication by default. If you plan to expose this to the internet, you should implement a reverse proxy with proper security measures (e.g., Basic Auth, HTTPS).
