from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
import requests
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
from fpdf import FPDF
import docx
from tempfile import NamedTemporaryFile
import asyncio

# -------------------------------
# Load OpenRouter API Key
# -------------------------------
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OpenRouter API key not found. Set it in .env")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "gpt-3.5-turbo"

app = FastAPI()


# -------------------------------
# Async API Call to OpenRouter
# -------------------------------
async def call_openrouter(prompt: str):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000
    }
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: requests.post(API_URL, headers=headers, json=data, timeout=60)
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------
# Generate Notes
# -------------------------------
async def generate_study_notes(text: str, mode: str):
    if mode == "Bullet Points":
        prompt = f"Summarize the lecture into concise bullet points:\n\n{text}"
    elif mode == "Flashcards":
        prompt = f"Convert the lecture into question-answer flashcards:\n\n{text}\nFormat: Q: ... A: ..."
    elif mode == "MCQs":
        prompt = f"""
Generate 5 multiple-choice questions from the lecture.
Each question should have 4 options labeled A-D.
Highlight the correct answer in **bold**.
Randomize the order of questions and options.
Lecture: {text}
"""
    else:
        return "Invalid mode selected."
    
    return await call_openrouter(prompt)

# -------------------------------
# Extract text from PDFs
# -------------------------------
async def extract_text_from_pdfs(files):
    combined_text = ""
    for file in files:
        pdf_bytes = await file.read()
        if not pdf_bytes:  # Skip empty files
            continue
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception:
            continue  # Skip invalid PDF files
        for page in doc:
            combined_text += page.get_text()
        combined_text += "\n"
    return combined_text

# -------------------------------
# Create PDF (UTF-8 safe)
# -------------------------------
def create_pdf(text: str):
    safe_text = text.replace("’", "'").replace("“", '"').replace("”", '"').replace("–", "-")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    for line in safe_text.split("\n"):
        pdf.multi_cell(0, 8, line)
    
    tmp_file = NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name

# -------------------------------
# Create DOCX
# -------------------------------
def create_docx(text: str):
    doc = docx.Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    tmp_file = NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(tmp_file.name)
    return tmp_file.name

# -------------------------------
# Home Page
# -------------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>AI Study Assistant - Jericho Sonon</title>
        <style>
            body { font-family: Arial; max-width: 900px; margin: auto; padding: 20px; background-color: #1e1e2f; color: #fff; }
            h1 { color: #ffa500; text-align: center; }
            textarea, input[type=file] { width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #444; margin-bottom: 15px; background-color: #2e2e3f; color: #fff; }
            select, input[type=submit] { padding: 10px; border-radius: 5px; border: 1px solid #444; background-color: #444; color: #fff; }
            input[type=submit]:hover { background-color: #555; }
            .spinner { display: none; margin: 10px auto; border: 6px solid #f3f3f3; border-top: 6px solid #ffa500; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <h1>AI Study Assistant by Jericho Sonon</h1>
        <form id="notesForm" action="/generate" method="post" enctype="multipart/form-data" onsubmit="showSpinner()">
            <label>Paste Lecture Text:</label><br>
            <textarea id="lecture_text" name="lecture_text" rows="10" placeholder="Paste your lecture here..."></textarea><br>
            <label>Or Upload PDFs (multiple allowed):</label><br>
            <input type="file" id="pdf_file" name="pdf_file" accept=".pdf" multiple><br><br>
            <label>Output Mode:</label><br>
            <select name="mode">
                <option value="Bullet Points">Bullet Points</option>
                <option value="Flashcards">Flashcards</option>
                <option value="MCQs">Multiple-Choice Questions</option>
            </select><br><br>
            <input type="submit" id="generateBtn" value="Generate Notes" disabled>
        </form>
        <div class="spinner" id="spinner"></div>
        <script>
            const lectureText = document.getElementById("lecture_text");
            const pdfFile = document.getElementById("pdf_file");
            const generateBtn = document.getElementById("generateBtn");

            function toggleGenerateBtn() {
                if (lectureText.value.trim() !== "" || (pdfFile.files && pdfFile.files.length > 0)) {
                    generateBtn.disabled = false;
                } else {
                    generateBtn.disabled = true;
                }
            }

            lectureText.addEventListener("input", toggleGenerateBtn);
            pdfFile.addEventListener("change", toggleGenerateBtn);

            function showSpinner() { document.getElementById("spinner").style.display = "block"; }

            toggleGenerateBtn();
        </script>
    </body>
    </html>
    """

# -------------------------------
# Generate Notes Page
# -------------------------------
@app.post("/generate", response_class=HTMLResponse)
async def generate(
    lecture_text: str = Form(""),
    mode: str = Form(...),
    pdf_file: list[UploadFile] = File(None)
):
    text = lecture_text.strip() if lecture_text else ""
    pdf_text = ""

    if pdf_file and len(pdf_file) > 0:
        pdf_text = await extract_text_from_pdfs(pdf_file)

    # Use PDF text only if lecture text is empty
    if not text and pdf_text.strip():
        text = pdf_text.strip()

    # Error only if both are empty
    if not text:
        result = "Error: Please provide lecture text or upload at least one PDF."
    else:
        result = await generate_study_notes(text, mode)

    pdf_path = create_pdf(result)
    docx_path = create_docx(result)

    return f"""
    <html>
    <head>
        <title>Generated Notes - Jericho Sonon</title>
        <style>
            body {{ font-family: Arial; max-width: 900px; margin: auto; padding: 20px; background-color: #1e1e2f; color: #fff; }}
            h1 {{ color: #ffa500; text-align: center; }}
            pre {{ background-color: #2e2e3f; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }}
            .buttons {{ margin-top: 10px; }}
            button, a.button {{ padding: 8px 12px; margin-right: 10px; border-radius: 5px; border: none; cursor: pointer; text-decoration: none; }}
            .copy-btn {{ background-color: #e1ef00; color: white; }}
            .copy-btn:hover {{ background-color: #0b7dda; }}
            .pdf-btn {{ background-color: #4CAF50; color: white; }}
            .pdf-btn:hover {{ background-color: #45a049; }}
            .docx-btn {{ background-color: #2196F3; color: white; }}
            .docx-btn:hover {{ background-color: #0b7dda; }}
            .back-btn {{ background-color: #f44336; color: white; }}
            .back-btn:hover {{ background-color: #d32f2f; }}
        </style>
    </head>
    <body>
        <h1>Generated Notes</h1>
        <pre id="output">{result}</pre>
        <div class="buttons">
            <button class="copy-btn" onclick="copyText()">Copy Notes</button>
            <a class="button pdf-btn" href="/download_pdf?path={pdf_path}">Download PDF</a>
            <a class="button docx-btn" href="/download_docx?path={docx_path}">Download DOCX</a>
            <a class="button back-btn" href="/">Go Back</a>  m
        </div>
        <script>
            function copyText() {{
                const text = document.getElementById("output").innerText;
                navigator.clipboard.writeText(text).then(() => {{
                    alert("Notes copied to clipboard!");
                }});
            }}
        </script>
    </body>
    </html>
    """

# -------------------------------
# Download Endpoints
# -------------------------------
@app.get("/download_pdf")
def download_pdf(path: str):
    return FileResponse(path, media_type="application/pdf", filename="study_notes.pdf")

@app.get("/download_docx")
def download_docx(path: str):
    return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="study_notes.docx")
