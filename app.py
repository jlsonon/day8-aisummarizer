import gradio as gr
import requests
import os
import fitz  # PyMuPDF
from fpdf import FPDF
import docx
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv

# -------------------------------
# Load OpenRouter API Key
# -------------------------------
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OpenRouter API key not found. Set it in .env")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "gpt-3.5-turbo"

# -------------------------------
# Call OpenRouter API
# -------------------------------
def call_openrouter(prompt: str):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000
    }
    response = requests.post(API_URL, headers=headers, json=data, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# -------------------------------
# Generate Study Notes
# -------------------------------
def generate_study_notes(text: str, mode: str):
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
    
    return call_openrouter(prompt)

# -------------------------------
# Extract text from PDFs
# -------------------------------
def extract_text_from_pdfs(files):
    combined_text = ""
    for file in files:
        with fitz.open(file.name) as doc:
            for page in doc:
                combined_text += page.get_text()
        combined_text += "\n"
    return combined_text

# -------------------------------
# Create PDF
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
# Main Function
# -------------------------------
def summarize(lecture_text, mode, pdfs):
    text = lecture_text.strip() if lecture_text else ""
    
    if pdfs and len(pdfs) > 0:
        text += extract_text_from_pdfs(pdfs)

    if not text.strip():
        return "Error: Please provide lecture text or upload at least one PDF.", None, None

    result = generate_study_notes(text, mode)
    pdf_path = create_pdf(result)
    docx_path = create_docx(result)

    return result, pdf_path, docx_path

# -------------------------------
# Gradio Layout (Two-Column)
# -------------------------------
with gr.Blocks(theme="soft") as iface:
    gr.Markdown("## AI Study Assistant by Jericho Sonon")
    gr.Markdown("Upload your lecture notes or PDFs to generate **bullet points**, **flashcards**, or **MCQs** using OpenRouter GPT models.")

    with gr.Row():
        with gr.Column(scale=1):
            lecture_text = gr.Textbox(
                lines=35,
                label="Paste Lecture Text",
                placeholder="Paste your lecture or notes here...",
                interactive=True
            )
            mode = gr.Radio(
                ["Bullet Points", "Flashcards", "MCQs"],
                label="Output Mode",
                value="Bullet Points"
            )
            pdfs = gr.File(file_count="multiple", label="Upload PDFs (optional)")
            generate_btn = gr.Button("Generate Study Notes", variant="primary")

        with gr.Column(scale=1):
            generated_notes = gr.Textbox(
                label="Generated Notes",
                lines=35,
                interactive=True,
                show_copy_button=True
            )
            pdf_file = gr.File(label="Download as PDF")
            docx_file = gr.File(label="Download as DOCX")

    generate_btn.click(
        summarize,
        inputs=[lecture_text, mode, pdfs],
        outputs=[generated_notes, pdf_file, docx_file]
    )

iface.launch()
