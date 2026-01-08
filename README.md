# GenAI Multi-Modal Assistant
Welcome to the GenAI Multi-Modal Assistant project.
This is a Python-based web application built using Flask that enables users to interact with an AI system 
through multiple input modes such as text, voice, and images. The assistant is designed to provide intelligent
responses while adapting its tone based on the user’s emotional state, creating a more human-like 
interaction experience.

The project focuses on combining Natural Language Processing, speech processing, and emotion-aware response generation into a single, unified system.

## Key Features
 -Text-Based Interaction:Users can ask questions using a text input interface.
 -Voice Interaction (Speech-to-Text & Text-to-Speech): Users can speak directly to the assistant using a browser microphone, and AI responses are spoken aloud.
 -Speaker Control Panel: Includes speaker ON/OFF toggle, stop speaking mid-response, and replay last AI response.
 -Image Upload & Explanation:Users can upload an image and receive an AI-generated explanation of its content.
 -Emotion Detection:The system detects emotions such as angry, confused, happy, or neutral from user input and adjusts the response tone accordingly.
 -Emotion-Aware AI Responses: The AI maintains correct answers while modifying tone based on detected emotion (calm, explanatory, friendly, etc.).

## Technologies Used

 Python – Core backend logic
 Flask – Web framework
 Groq LLM API – Large Language Model integration
 HTML, CSS, JavaScript – Frontend interface
 SpeechRecognition API (Browser) – Voice input
 Web Speech API – Text-to-speech output
dotenv – Environment variable management

## Project Structure
```
MULTI_MODEL_ASSISTANT/
│
├── app.py                     # Main Flask application
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation
├── .env                       # API keys and environment variables
│
├── templates/
│   └── index.html             # Main UI template
│
├── static/
│   └── style.css              # Styling
│
├── utils/
│   ├── speech_to_text.py      # Voice input handling
│   └── emotion_detector.py    # Emotion detection logic
│
├── uploads/                   # Uploaded images

```
## Setup Instructions

### 1. Clone the Repository
```
git clone <repository-url>
cd MULTI_MODEL_ASSISTANT

```
### 2. Create Virtual Environment
```
 python -m venv venv
 source venv/bin/activate #on windows:venv\Scripts\activate
```
### 3. Install Dependencies
```
pip install -r requirements.txt

```
### 4. Configure Environment Variables
    Create a .env file in the root directory:
```
   GROQ_API_KEY=your_groq_api_key_here
```

 ### 5. Run the Application
 ```
    python app.py
 ```
Open the browser and go to:
 ```
 http://127.0.0.1:5000

 ```

## Usage

Type a question and click Ask AI
Use the Speak button for voice input
Upload an image to receive AI explanation
Control AI voice using speaker controls
Observe emotion-aware responses based on your input tone


## Future Enhancements

Chat history panel with session-based memory
User authentication
Emotion visualization dashboard
AI response summarization
Multi-language auto-detection

## License

This project is licensed under the MIT License.
You are free to use, modify, and distribute this project.

## Author
Developed by Nisu Bharti
