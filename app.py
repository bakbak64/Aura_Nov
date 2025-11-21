import os
import time
import uuid
import base64
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from dotenv import load_dotenv

from utils.helpers import load_config
from utils.database import Database
from utils.logger import Logger
from utils.helpers import ensure_directory

from core.camera import Camera
from core.detector import ObjectDetector
from core.face_rec import FaceRecognizer
from core.ocr import OCRReader
from core.scene_ai import SceneAI
from core.voice import VoiceSystem
from core.alerts import AlertManager
from core.wake_word import WakeWordDetector

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/uploads/faces'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

config = load_config()
db = Database()
logger = Logger()

camera = Camera(config)
detector = ObjectDetector(config)
face_recognizer = FaceRecognizer(config, db)
ocr_reader = OCRReader(config)
scene_ai = SceneAI(config)
voice_system = VoiceSystem(config)
alert_manager = AlertManager(config)
wake_word_detector = WakeWordDetector(config)

ensure_directory(app.config['UPLOAD_FOLDER'])

session_state = {
    'active': False,
    'session_id': None,
    'start_time': None,
    'frame_count': 0,
    'last_frame_time': time.time(),
    'processing_thread': None,
    'alert_count': 0,
    'wake_word_active': False,
    'voice_listening': False
}


def process_frame():
    frame_skip = config['detection'].get('frame_skip', 2)
    inactivity_threshold = config['alerts'].get('auto_pause_inactivity_minutes', 15) * 60
    last_activity = time.time()
    
    while session_state['active']:
        frame = camera.get_raw_frame()
        if frame is None:
            time.sleep(0.1)
            continue
        
        current_time = time.time()
        session_state['frame_count'] += 1
        
        if session_state['frame_count'] % frame_skip != 0:
            continue
        
        try:
            detections = detector.detect(frame)
            face_recognitions = face_recognizer.recognize(frame, current_time)
            
            for detection in detections:
                priority = detection.get('priority', 'informational')
                alert_type = f"object_{detection['class']}"
                identifier = f"{detection['class']}_{detection['direction']}"
                
                if alert_manager.should_alert(alert_type, priority, identifier):
                    distance_cat, distance_feet = calculate_distance_estimate(
                        detection['size'][1], frame.shape[0]
                    )
                    
                    if priority == 'critical':
                        message = f"{detection['class'].upper()} detected {distance_cat} distance from your {detection['direction']}!"
                    elif priority == 'important':
                        message = f"{detection['class']} detected {distance_cat} distance from your {detection['direction']}"
                    else:
                        message = f"{detection['class']} in view"
                    
                    formatted_msg = alert_manager.format_alert_message(priority, message)
                    
                    voice_system.speak(formatted_msg, interrupt=(priority == 'critical'))
                    alert_manager.add_to_history(priority, message, detection)
                    
                    db.add_event_log(
                        session_state['session_id'],
                        'object_detection',
                        priority,
                        message,
                        detection
                    )
                    
                    socketio.emit('alert', {
                        'priority': priority,
                        'message': message,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    session_state['alert_count'] += 1
                    last_activity = current_time
            
            for recognition in face_recognitions:
                alert_type = f"face_{recognition['name']}"
                
                if alert_manager.should_alert(alert_type, 'important', str(recognition['face_id'])):
                    message = f"{recognition['name']} is {recognition['distance_feet']:.0f} feet in front of you"
                    formatted_msg = alert_manager.format_alert_message('important', message)
                    
                    voice_system.speak(formatted_msg)
                    alert_manager.add_to_history('important', message, recognition)
                    
                    db.add_event_log(
                        session_state['session_id'],
                        'face_recognition',
                        'important',
                        message,
                        recognition
                    )
                    
                    socketio.emit('alert', {
                        'priority': 'important',
                        'message': message,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    session_state['alert_count'] += 1
                    last_activity = current_time
            
            if current_time - last_activity > inactivity_threshold:
                session_state['active'] = False
                socketio.emit('session_paused', {'reason': 'inactivity'})
                break
            
            time.sleep(1.0 / config['detection'].get('target_fps', 15))
        
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            time.sleep(0.1)


def calculate_distance_estimate(bbox_height, frame_height):
    height_ratio = bbox_height / frame_height
    
    if height_ratio >= config['distance']['bounding_box_threshold_small']:
        return "very close", config['distance']['very_close_feet']
    elif height_ratio >= config['distance']['bounding_box_threshold_large']:
        return "close", config['distance']['close_feet']
    else:
        return "medium", config['distance']['medium_feet']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/faces')
def faces():
    return render_template('faces.html')


@app.route('/logs')
def logs():
    return render_template('logs.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/api/faces', methods=['GET'])
def get_faces():
    faces = db.get_all_faces()
    return jsonify([{
        'id': f['id'],
        'name': f['name'],
        'relationship': f['relationship'],
        'created_at': f['created_at']
    } for f in faces])


@app.route('/api/faces', methods=['POST'])
def add_face():
    if 'photo' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['photo']
    name = request.form.get('name', '')
    relationship = request.form.get('relationship', 'Other')
    
    if not name or file.filename == '':
        return jsonify({'error': 'Name and photo required'}), 400
    
    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    face_id = face_recognizer.add_face(filepath, name, relationship)
    
    if face_id:
        return jsonify({'success': True, 'face_id': face_id})
    else:
        return jsonify({'error': 'Could not detect face in image'}), 400


@app.route('/api/faces/<int:face_id>', methods=['DELETE'])
def delete_face(face_id):
    if face_recognizer.delete_face(face_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Face not found'}), 404


@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = db.get_all_sessions()
    return jsonify(sessions)


@app.route('/api/logs', methods=['GET'])
def get_logs():
    session_id = request.args.get('session_id')
    limit = int(request.args.get('limit', 100))
    
    if session_id:
        logs = db.get_session_logs(session_id)
    else:
        logs = db.get_all_event_logs(limit)
    
    return jsonify(logs)


@app.route('/api/session/start', methods=['POST'])
def start_session():
    if session_state['active']:
        return jsonify({'error': 'Session already active'}), 400
    
    session_id = str(uuid.uuid4())
    session_state['session_id'] = session_id
    session_state['start_time'] = time.time()
    session_state['frame_count'] = 0
    session_state['alert_count'] = 0
    session_state['active'] = True
    
    if not camera.start():
        session_state['active'] = False
        return jsonify({'error': 'Could not start camera'}), 500
    
    db.create_session(session_id)
    
    session_state['processing_thread'] = threading.Thread(target=process_frame, daemon=True)
    session_state['processing_thread'].start()
    
    if not session_state['wake_word_active']:
        wake_word_detector.start_listening(lambda: on_wake_word())
        session_state['wake_word_active'] = True
    
    logger.info(f"Session started: {session_id}")
    socketio.emit('session_started', {'session_id': session_id})
    
    return jsonify({'success': True, 'session_id': session_id})


@app.route('/api/session/stop', methods=['POST'])
def stop_session():
    if not session_state['active']:
        return jsonify({'error': 'No active session'}), 400
    
    session_state['active'] = False
    
    if session_state['processing_thread']:
        session_state['processing_thread'].join(timeout=3)
    
    camera.stop()
    wake_word_detector.stop_listening()
    session_state['wake_word_active'] = False
    
    duration = int(time.time() - session_state['start_time']) if session_state['start_time'] else 0
    db.end_session(session_state['session_id'], duration, session_state['alert_count'])
    
    logger.info(f"Session stopped: {session_state['session_id']}")
    socketio.emit('session_stopped')
    
    return jsonify({'success': True})


@app.route('/api/voice/command', methods=['POST'])
def handle_voice_command():
    data = request.json
    command = data.get('command', '').lower()
    
    if not session_state['active']:
        return jsonify({'error': 'No active session'}), 400
    
    frame = camera.get_raw_frame()
    if frame is None:
        return jsonify({'error': 'Camera not available'}), 400
    
    response_text = ""
    
    if 'what\'s in front' in command or 'describe' in command or 'what do you see' in command:
        response_text = scene_ai.describe_scene(frame)
        voice_system.speak(response_text)
    
    elif 'traffic light' in command or 'red light' in command:
        light_color = scene_ai.detect_traffic_light(frame)
        if light_color:
            response_text = f"The traffic light is {light_color}"
        else:
            response_text = "I don't see a traffic light"
        voice_system.speak(response_text)
    
    elif 'read this' in command or 'read' in command:
        text = ocr_reader.read_text(frame)
        if text:
            response_text = f"I read: {text}"
        else:
            response_text = "I couldn't read any text"
        voice_system.speak(response_text)
    
    elif 'who is here' in command or 'who\'s here' in command:
        face_recognitions = face_recognizer.recognize(frame, time.time())
        if face_recognitions:
            names = [r['name'] for r in face_recognitions]
            response_text = f"I see: {', '.join(names)}"
        else:
            response_text = "I don't recognize anyone"
        voice_system.speak(response_text)
    
    elif 'pause' in command:
        alert_manager.pause()
        response_text = "Alerts paused"
        voice_system.speak(response_text)
    
    elif 'resume' in command:
        alert_manager.resume()
        response_text = "Alerts resumed"
        voice_system.speak(response_text)
    
    else:
        response_text = "I didn't understand that command"
        voice_system.speak(response_text)
    
    db.add_event_log(
        session_state['session_id'],
        'voice_command',
        'informational',
        response_text,
        {'command': command}
    )
    
    return jsonify({'success': True, 'response': response_text})


@socketio.on('connect')
def handle_connect():
    emit('connected', {'status': 'connected'})


@socketio.on('get_frame')
def handle_frame_request():
    if session_state['active']:
        result = camera.get_frame()
        if result:
            jpeg_data, _ = result
            frame_base64 = base64.b64encode(jpeg_data).decode('utf-8')
            emit('frame', {'data': f'data:image/jpeg;base64,{frame_base64}'})


def on_wake_word():
    if session_state['active'] and not session_state['voice_listening']:
        session_state['voice_listening'] = True
        socketio.emit('wake_word_detected')
        
        def listen_callback(text):
            session_state['voice_listening'] = False
            socketio.emit('voice_command', {'command': text})
        
        voice_text = voice_system.listen(callback=listen_callback)
        if voice_text:
            session_state['voice_listening'] = False


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

