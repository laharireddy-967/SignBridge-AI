# SignBridge AI

AI-powered sign language communication system designed to reduce communication barriers between sign language users and non-signers.

## 🌟 About the Project

SignBridge AI is a prototype focused on making communication more accessible through real-time sign and speech interaction.

The system explores two-way communication:

**Sign → Text → Speech**

**Speech/Text → Sign**

## 🚀 Current Features

- ✋ Real-time hand gesture detection
- 📝 Gesture-to-text conversion
- 🔊 Text-to-speech output
- 🎤 Speech-to-text input
- 🖼️ Text/voice-to-sign image output
- 🌐 Flask-based web interface
- 🤝 Predefined sign and phrase recognition

## 🛠️ Technologies Used

- **Python**
- **OpenCV** – Computer vision and camera processing
- **MediaPipe** – Hand landmark detection
- **gTTS** – Text-to-speech
- **SpeechRecognition** – Speech-to-text
- **Flask** – Web application backend
- **HTML, CSS & JavaScript** – Web interface

## ⚙️ System Flow

### Sign Language → Speech

Camera  
↓  
Hand Detection  
↓  
Gesture Recognition  
↓  
Text  
↓  
Voice Output

### Speech/Text → Sign

Speech / Text Input  
↓  
Phrase Recognition  
↓  
Sign Representation  
↓  
Sign Image / Animation

## 📁 Project Structure

```text
SignBridge-AI/
│
├── signbridge.py
├── web_app.py
├── test_mic.py
├── signs/
│   ├── agree.jpeg
│   ├── callme.jpeg
│   ├── goodjob.jpeg
│   ├── hello.jpeg
│   ├── pleasewait.jpeg
│   └── thankyou.jpeg
│
├── web/
│   └── templates/
│       └── index.html
│
├── SignProject/
│   └── Previous team implementation
│
├── .gitignore
└── README.md
