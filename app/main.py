import os
import subprocess
import threading
from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

VIDEO_DIR = os.environ.get('VIDEO_PATH', '/app/videos')
syncplay_process = None

def get_video_files():
    """Scans the video directory for supported video files."""
    supported_formats = ('.mp4', '.mkv', '.avi', '.webm', '.mov')
    video_files = []
    if os.path.exists(VIDEO_DIR):
        for root, _, files in os.walk(VIDEO_DIR):
            for file in files:
                if file.lower().endswith(supported_formats):
                    relative_path = os.path.relpath(os.path.join(root, file), VIDEO_DIR)
                    video_files.append(relative_path.replace('\\', '/'))
    return sorted(video_files)

def read_syncplay_output(pipe):
    """Reads Syncplay's stdout and emits socket events."""
    for line in iter(pipe.readline, ''):
        line = line.strip()
        print(f"Syncplay: {line}")  # Debugging
        socketio.emit('syncplay_output', {'data': line}, namespace='/sync')
    pipe.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify(status='ok')

@app.route('/api/videos')
def list_videos():
    """API endpoint to list video files."""
    videos = get_video_files()
    return jsonify(videos)

@app.route('/videos/<path:filename>')
def serve_video(filename):
    """Serves a video file from the mounted volume."""
    return send_from_directory(VIDEO_DIR, filename)

@socketio.on('connect_syncplay', namespace='/sync')
def connect_syncplay(data):
    """Starts the syncplay-cli client."""
    global syncplay_process
    if syncplay_process and syncplay_process.poll() is None:
        emit('status', {'message': 'Syncplay is already running.'})
        return

    server = data.get('server')
    room = data.get('room')
    username = data.get('username')
    video_path = data.get('videoPath')

    full_video_path = os.path.join(VIDEO_DIR, video_path)

    command = [
        'syncplay', '--no-gui',
        '--host', server,
        '--name', username,
        '--room', room,
        '--', full_video_path
    ]

    try:
        syncplay_process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        output_thread = threading.Thread(target=read_syncplay_output, args=(syncplay_process.stdout,))
        output_thread.daemon = True
        output_thread.start()

        emit('status', {'message': f'Connecting to {server} in room {room}...'})

    except Exception as e:
        emit('status', {'message': f'Failed to start Syncplay: {e}'})

@socketio.on('playback_action', namespace='/sync')
def playback_action(data):
    """Sends playback actions to the syncplay process."""
    if syncplay_process and syncplay_process.poll() is None:
        action = data.get('action')
        command = ""
        if action == 'pause':
            command = 'p'
        elif action == 'play':
            command = 'u'
        elif action == 'seek':
            position = data.get('position')
            command = f's {int(position)}'

        if command:
            try:
                syncplay_process.stdin.write(command + '\n')
                syncplay_process.stdin.flush()
            except (IOError, OSError) as e:
                print(f"Error writing to syncplay stdin: {e}")
                emit('status', {'message': 'Failed to send command to Syncplay.'})

@socketio.on('chat_message', namespace='/sync')
def chat_message(data):
    """Sends a chat message to the syncplay process."""
    if syncplay_process and syncplay_process.poll() is None:
        message = data.get('message')
        if message:
            try:
                syncplay_process.stdin.write(message + '\n')
                syncplay_process.stdin.flush()
            except (IOError, OSError) as e:
                print(f"Error writing to syncplay stdin: {e}")
                emit('status', {'message': 'Failed to send chat message.'})

@socketio.on('disconnect', namespace='/sync')
def on_disconnect():
    """Stops the syncplay-cli client on socket disconnect."""
    global syncplay_process
    if syncplay_process and syncplay_process.poll() is None:
        syncplay_process.terminate()
        syncplay_process = None
    print('Client disconnected')

# The application is now run via Gunicorn, so this block is no longer needed.
# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0', port=8000)
