# AURA - AI-Powered Real-Time Vision Assistant for Visually Impaired People

AURA is a comprehensive vision assistant that helps visually impaired people navigate their environment using AI-powered object detection, face recognition, OCR text reading, and voice commands.

## Features

- **Real-time Object Detection**: Detects people, vehicles, obstacles, and fire hazards using YOLOv8
- **Face Recognition**: Recognizes known faces and announces them with relationship information
- **Voice Commands**: "Hey Aura" wake word system with natural language commands
- **OCR Text Reading**: Reads medicine labels, signs, and documents using Tesseract
- **Smart Alert System**: 3 priority levels (Critical/Important/Informational) with intelligent cooldowns
- **Text-to-Speech**: Offline audio output using pyttsx3
- **Web Interface**: Accessible from any browser (desktop and mobile)
- **Session Management**: Start/stop sessions with automatic logging
- **Caregiver Logs**: Review session history and event logs

## Tech Stack

- **Backend**: Flask + Flask-SocketIO
- **Object Detection**: YOLOv8 (Ultralytics) - runs on CPU
- **Scene Understanding**: Google Gemini Vision API (free tier)
- **Face Recognition**: face_recognition library (local)
- **OCR**: Tesseract (local)
- **Text-to-Speech**: pyttsx3 (offline)
- **Speech Recognition**: SpeechRecognition with Google API
- **Wake Word**: Vosk (offline)
- **Database**: SQLite
- **Frontend**: HTML/CSS/JS with Tailwind CDN

## Prerequisites

- Windows 10/11
- Python 3.8 or higher
- Webcam
- Microphone
- Internet connection (for Gemini API)

## Installation

### Step 1: Install Python

1. Download Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Verify installation:
```bash
python --version
```

### Step 2: Install Tesseract OCR

1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer and note the installation path (default: `C:\Program Files\Tesseract-OCR`)
3. Add Tesseract to your system PATH:
   - Open System Properties > Environment Variables
   - Add `C:\Program Files\Tesseract-OCR` to Path variable
4. Verify installation:
```bash
tesseract --version
```

### Step 3: Clone or Download Project

```bash
cd aura
```

### Step 4: Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If you encounter errors installing `dlib` or `face_recognition`, you may need to install Visual C++ Build Tools:
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install "Desktop development with C++" workload

### Step 6: Get Google Gemini API Key (Free)

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key
5. Create a `.env` file in the project root:
```
GOOGLE_GEMINI_API_KEY=your_api_key_here
```

**Free Tier Limits**:
- 15 requests per minute
- 1,500 requests per day
- No credit card required

### Step 7: Download AI Models

Run the model download script:

```bash
python scripts\download_models.py
```

**Note**: YOLOv8 model will be automatically downloaded on first run (~6MB).

### Step 8: Initialize Database

```bash
python scripts\init_db.py
```

### Step 9: Test Hardware

Test your camera:
```bash
python scripts\test_camera.py
```

Test your microphone:
```bash
python scripts\test_mic.py
```

## Running the Application

### Start the Server

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Access the Web Interface

1. Open your browser (Chrome, Firefox, Edge, etc.)
2. Navigate to `http://localhost:5000`
3. For mobile access, use your computer's IP address: `http://YOUR_IP:5000`

**Find your IP address**:
- Open Command Prompt
- Type: `ipconfig`
- Look for "IPv4 Address" (usually starts with 192.168.x.x)

## Usage Guide

### Starting a Session

1. Click "START SESSION" on the main page
2. Grant camera and microphone permissions when prompted
3. The system will begin detecting objects and faces
4. Say "Hey Aura" to activate voice commands

### Voice Commands

After saying "Hey Aura", you can use these commands:

- **"What's in front of me?"** - Get AI-powered scene description
- **"What's the red light signal right now?"** - Check traffic light color
- **"Read this"** - Read text from camera view (point camera at text)
- **"Who is here?"** - List detected faces
- **"Describe what you see"** - Full scene description
- **"Pause"** - Pause automatic alerts
- **"Resume"** - Resume automatic alerts

### Adding Known Faces

1. Go to the "Faces" page
2. Click "Add Face"
3. Enter name and select relationship (Family/Friend/Caregiver/Other)
4. Upload a clear photo with one face visible
5. The system will recognize this person in future sessions

### Alert System

**Critical Alerts** (Priority 1):
- Fire/smoke detection
- Fast-approaching vehicles
- Imminent collisions
- Interrupts ongoing speech, repeats every 3 seconds

**Important Alerts** (Priority 2):
- Known face detected
- New person enters view
- Once per event, 30-60 second cooldown

**Informational Alerts** (Priority 3):
- Voice command responses only

### Viewing Logs

1. Go to the "Logs" page
2. View session history and event logs
3. Filter by session ID
4. All alerts and events are logged with timestamps

## Configuration

Edit `config.yaml` to customize settings:

```yaml
camera:
  resolution_width: 640
  resolution_height: 480
  fps: 20

detection:
  confidence_threshold: 0.25
  frame_skip: 2

alerts:
  critical:
    repeat_interval_seconds: 3
  important:
    cooldown_seconds: 30

voice:
  tts_rate: 150
  tts_volume: 0.8
```

## Troubleshooting

### Camera Not Working

- Check if camera is being used by another application
- Verify camera permissions in Windows Settings
- Try changing `device_id` in `config.yaml` (0, 1, 2, etc.)

### Microphone Not Working

- Check microphone permissions in Windows Settings
- Verify microphone is set as default input device
- Test microphone in Windows Sound settings

### Tesseract Not Found

- Ensure Tesseract is installed and in PATH
- Restart terminal/command prompt after installation
- Verify with: `tesseract --version`

### Face Recognition Not Working

- Ensure uploaded photos have clear, single faces
- Good lighting and frontal view work best
- Check that `dlib` installed correctly

### Gemini API Errors

- Verify API key is correct in `.env` file
- Check internet connection
- Monitor rate limits (15 requests/minute)
- System will use local-only mode if API fails

### Low Performance/FPS

- Reduce camera resolution in `config.yaml`
- Increase `frame_skip` value (process every Nth frame)
- Close other applications using CPU
- Ensure good lighting for better detection

### Models Not Downloading

- Check internet connection
- YOLOv8 downloads automatically on first use
- Vosk model can be downloaded manually from: https://alphacephei.com/vosk/models/

## Project Structure

```
aura/
├── app.py                  # Main Flask application
├── config.yaml             # Configuration file
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .env.example           # API key template
│
├── core/                   # Core modules
│   ├── camera.py          # Camera handling
│   ├── detector.py        # YOLOv8 object detection
│   ├── face_rec.py        # Face recognition
│   ├── ocr.py             # Tesseract OCR
│   ├── scene_ai.py        # Gemini API
│   ├── voice.py           # TTS and speech recognition
│   ├── alerts.py          # Alert management
│   └── wake_word.py       # Wake word detection
│
├── utils/                  # Utility modules
│   ├── database.py        # SQLite operations
│   ├── logger.py          # Logging system
│   └── helpers.py         # Helper functions
│
├── static/                 # Static files
│   ├── css/style.css      # Styling
│   ├── js/main.js         # Frontend logic
│   ├── js/socket.js       # WebSocket handling
│   └── uploads/faces/     # Uploaded face photos
│
├── templates/              # HTML templates
│   ├── index.html         # Main control panel
│   ├── faces.html         # Face management
│   ├── logs.html          # Session logs
│   └── settings.html      # Settings page
│
├── scripts/                # Helper scripts
│   ├── download_models.py # Download AI models
│   ├── init_db.py         # Initialize database
│   ├── test_camera.py     # Test camera
│   └── test_mic.py        # Test microphone
│
├── database/               # SQLite database
│   └── aura.db            # Auto-created
│
├── logs/                   # Log files
│   └── session_logs/      # Session logs
│
└── models/                 # AI models (auto-download)
    └── vosk-model-small-en/
```

## Database Schema

```sql
-- Known faces
CREATE TABLE known_faces (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    relationship TEXT,
    face_encoding BLOB NOT NULL,
    photo_path TEXT,
    created_at TIMESTAMP
);

-- Sessions
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    total_alerts INTEGER
);

-- Event logs
CREATE TABLE event_logs (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    timestamp TIMESTAMP,
    event_type TEXT,
    priority TEXT,
    message TEXT,
    metadata JSON
);
```

## Performance Tips

- **CPU Optimization**: Process every 2nd frame (`frame_skip: 2`)
- **Resolution**: Lower resolution (640x480) for better FPS
- **Lighting**: Ensure good lighting for better detection accuracy
- **Model Size**: Using YOLOv8-nano for fastest CPU performance

## Security Notes

- Keep your `.env` file secure (never commit it to version control)
- API keys are private - don't share them
- Face photos are stored locally in `static/uploads/faces/`
- All processing happens locally except Gemini API calls

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review error logs in `logs/session_logs/`
3. Test individual components using test scripts

## Acknowledgments

- Ultralytics for YOLOv8
- Google for Gemini API
- face_recognition library
- Tesseract OCR
- Vosk for wake word detection
- Flask and Flask-SocketIO communities

## Future Enhancements

- Mobile app (iOS/Android)
- Cloud sync for settings and faces
- Additional language support
- More voice command options
- Advanced scene understanding
- Integration with smart home devices

---

**Built with ❤️ for the visually impaired community**

