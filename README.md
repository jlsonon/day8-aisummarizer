# AI Study Assistant

**Day 8 of 30 Days of Generative AI**

Build an **AI-powered Study Assistant** web app that can **summarize lectures**, **generate flashcards**, and **create multiple-choice questions (MCQs)** using **GPT-3.5-turbo via OpenRouter**.  
The app supports **PDF uploads**, **text input**, and **exporting generated notes as PDF or DOCX** — all inside a clean, two-column **Gradio interface**.

---

## Features

1. **Multiple Output Modes**
   - **Bullet Points:** Summarizes long lectures into concise bullet-form notes.  
   - **Flashcards:** Converts lecture notes into question-answer style flashcards.  
   - **MCQs:** Generates multiple-choice questions with randomized options and highlighted correct answers.

2. **PDF Upload Support**
   - Upload one or multiple PDF lecture files.  
   - Automatically extracts and processes text from each page.

3. **Downloadable Notes**
   - Export generated study notes as **PDF** or **DOCX** files.  
   - Ideal for reviewing, printing, or sharing offline.

4. **Professional Interface**
   - Built with **Gradio Blocks** for a modern, responsive layout.  
   - Two-column design keeps lecture input and AI output side-by-side for better workflow.

---

## Project Goals

- Develop an intelligent AI study assistant for students and educators.  
- Automate note-taking, flashcard creation, and quiz generation.  
- Integrate PDF parsing and export options for convenience.  
- Deliver a professional, deployable, and portfolio-ready AI project.

---

## System Requirements

- Python 3.10 or higher  
- gradio  
- requests  
- python-dotenv  
- PyMuPDF  
- fpdf  
- python-docx  

---

## Setup Instructions

### 1. **Clone Repository**
```bash
git clone https://github.com/jlsonon/day8-aisummarizer.git
cd day8-aisummarizer
```

### 2. Install Dependecies
```bash
pip install -r requirements.txt
```
### 3. Set Up Environment Variables
- Create a .env file in the project root with your OpenRouter API key:
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```
### 4. Run the App
```bash
python app.py
```
A local Gradio interface will open in your browser where you can input text or upload PDFs.
---
## Project Structure
```bash
day8-aisummarizer/
│
├── app.py               # Main Gradio application
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (OpenRouter API key)
└── README.md            # Project documentation
```
---
## How It Works
1. **Enter Text** – The user types or pastes the text they want to enhance.

2. **Select Mode** – Choose between Grammar Correction, Rewriting, or Paraphrasing.

3. **Choose Tone** – Adjust tone (Formal, Casual, Professional, Academic, Creative).

4. **AI Processing** – The app sends the text to GPT-4o-mini via OpenRouter for rewriting.

5. **Output Displayed** – The rewritten text appears instantly, with session-based history.
 
---
## Tech Stack
- **Frontend:** Gradio (Blocks + Column layout for responsive design)

- **Backend:** Python-based text rewriting logic with GPT-4o-mini via OpenRouter

- **Environment Management:** python-dotenv for secure API key handling

- **Networking:** requests library for API communication

- **Deployment Options:** Hugging Face Spaces, Vercel, or local Python runtime

---
## Next Steps / Improvements

- Add support for summarizing lecture audio transcripts.

- Integrate subject-based customization (e.g., Math, History, Science).

- Improve layout with dark/light theme toggle.

- Enable batch export of all generated notes in one click.

- Add real-time token usage display and progress indicators.

---
Gradio Deployment: https://huggingface.co/spaces/jlsonon/day8-aisummarizer
---
## Acknowledgements

- **GPT-3.5-turbo via OpenRouter** for text generation and summarization.

- **Gradio** for building fast and interactive web apps.

- **PyMuPDF** for accurate PDF text extraction.

- **FPDF** and **python-docx** for export functionality.

- **python-dotenv** for secure environment variable management.
---
## About the Author
### Jericho Sonon

#### Medium: medium.com/@jlsonon12

#### GitHub: github.com/jlsonon

#### LinkedIn: linkedin.com/in/jlsonon
