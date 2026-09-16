# GenAI Multi-Modal Assistant
Welcome to the GenAI Multi-Modal Assistant project.
This is a Python-based web application built using Flask that enables users to interact with an AI system 
through multiple input modes such as text, voice, and images. The assistant is designed to provide intelligent
responses while adapting its tone based on the user’s emotional state, creating a more human-like 
interaction experience.

The project focuses on combining Natural Language Processing, speech processing, and emotion-aware response generation into a single, unified system.

 
 

 ## **Key Features**
  * Text-Based Interaction: Users can ask questions through a text input interface and receive AI-generated responses.
  * Voice Interaction (Speech-to-Text & Text-to-Speech): Users can speak directly through the browser microphone using the Web Speech         API,and the AI-generated responses can be spoken aloud using the browser's Speech Synthesis API.
  * Speaker Control Panel: Includes speaker ON/OFF toggle, stop speaking mid-response, and replay the last AI response.
  *  Image Upload & AI Analysis: Users can upload images and receive AI-generated descriptions, explanations, readable text, or solutions       to questions visible in the image.
  * OCR-Based Text Extraction: Uses Tesseract OCR to extract text from uploaded images and provide additional context for image analysis.
  * Emotion Detection: Detects emotions such as angry, confused, happy, sad, and neutral from user input using lightweight rule-based           keyword and phrase matching.
   * Emotion-Aware AI Responses: The assistant dynamically adapts its response style based on the detected emotion—for example, using a        calm tone for frustration, step-by-step explanations for confusion, and a friendly tone for positive emotions.
   * Multi-Modal AI Processing: Combines text, voice, and image inputs into a single AI assistant experience.


 ## **Technologies Used**

* **Python** – Core backend logic and application development
* **Flask** – Web framework for handling routes, requests, and responses
* **Groq API** – Integration with LLM and vision models
* **GPT-OSS-120B** – Text and voice response generation
* **Qwen 3.8 27B** – Image understanding and analysis
* **HTML, CSS, JavaScript** – Frontend interface and user interaction
* **Web Speech API (`SpeechRecognition`)** – Browser-based speech-to-text
* **Web Speech API (`speechSynthesis`)** – Text-to-speech output
* **OpenCV** – Image preprocessing
* **Tesseract OCR** – Text extraction from uploaded images
* **Pillow (PIL)** – Image handling and processing
* **python-dotenv** – Environment variable management

 ## Project Structure

```text
MULTI_MODEL_ASSISTANT/
│
├── app.py                         # Main Flask application
├── requirements.txt               # Project dependencies
├── README.md                      # Project documentation
├── .env                           # API key and environment variables
│
├── templates/
│   └── index.html                 # Main frontend UI
│
├── static/
│   └── style.css                  # Frontend styling
│
├── utils/
│   ├── speech_to_text.py          # Voice input text handling
│   └── image_reader.py            # Image analysis using OCR and vision model
│
└── uploads/                       # Uploaded images
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

- **Text Input:** Type a question and click **Ask AI**.
- **Voice Input:** Click the **Speak** button and speak through the browser microphone.
- **Image Analysis:** Upload an image to receive an AI-generated explanation or analysis.
- **Speaker Controls:** Turn voice output ON/OFF, stop speaking, or replay the last AI response.
- **Emotion-Aware Responses:** The assistant detects emotions from user input and adjusts its response style accordingly.


 ## Future Enhancements

- **Chat History & Session Memory:** Add a chat history panel with session-based conversation memory.
- **User Authentication:** Add secure user registration and login functionality.
- **Emotion Visualization Dashboard:** Display detected emotions using charts or visual indicators.
- **AI Response Summarization:** Provide concise summaries of longer AI-generated responses.
- **Multi-Language Support:** Add automatic language detection and multilingual interaction.

 ```mermaid
flowchart TD
    User([User Input])

    User --> Text[📝 Text Input]
    User --> Voice[🎤 Voice Input]
    User --> Image[🖼️ Image Input]

    %% TEXT PATH
    Text --> EmoT[Emotion Detection<br/>rule-based]
    EmoT --> GPT_T[GPT-OSS-120B]
    GPT_T --> RespT[AI Response]

    %% VOICE PATH
    Voice --> STT[SpeechRecognition<br/>Speech to Text]
    STT --> EmoV[Emotion Detection<br/>rule-based]
    EmoV --> GPT_V[GPT-OSS-120B]
    GPT_V --> RespV[AI Response]
    RespV --> TextOutV([💬 Text Output])
    RespV --> TTS[speechSynthesis]
    TTS --> VoiceOut([🔊 Voice Output])

    %% IMAGE PATH
    Image --> CV[OpenCV<br/>Preprocessing]
    CV --> OCR[Tesseract OCR]
    CV --> Qwen[Qwen 3.8 27B<br/>Vision Model]
    OCR --> Qwen
    Qwen --> RespI[Image Analysis Response]

    style GPT_T fill:#4A90D9,color:#fff
    style GPT_V fill:#4A90D9,color:#fff
    style Qwen fill:#E27D60,color:#fff
```
## License

This project is licensed under the MIT License.
You are free to use, modify, and distribute this project.

## Author
Developed by Nisu Bharti

 
