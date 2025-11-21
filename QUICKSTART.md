# AURA Quick Start Guide

## Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Tesseract OCR installed and in PATH
- [ ] Virtual environment created and activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Google Gemini API key obtained and added to `.env`
- [ ] Database initialized: `python scripts\init_db.py`
- [ ] Camera tested: `python scripts\test_camera.py`
- [ ] Microphone tested: `python scripts\test_mic.py`

## Running AURA

1. Activate virtual environment (if using one)
2. Start the server: `python app.py`
3. Open browser: `http://localhost:5000`
4. Click "START SESSION"
5. Grant camera/microphone permissions
6. Say "Hey Aura" to activate voice commands

## Common Issues

**Import Errors**: Make sure you've activated your virtual environment

**Camera Not Found**: Check Windows camera permissions and close other apps using camera

**Tesseract Not Found**: Restart terminal after installing Tesseract

**API Errors**: Verify `.env` file exists with `GOOGLE_GEMINI_API_KEY=your_key`

**Face Recognition Errors**: Ensure dlib installed correctly (may need Visual C++ Build Tools)

## Getting Help

1. Check `logs/session_logs/` for error messages
2. Run test scripts to isolate issues
3. Review README.md for detailed troubleshooting

