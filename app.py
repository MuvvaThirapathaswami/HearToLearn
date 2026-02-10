from flask import Flask, request, send_file
from flask_cors import CORS
from gtts import gTTS
import PyPDF2
import io

app = Flask(__name__)
CORS(app)

@app.route("/read_pdf", methods=["POST"])
def read_pdf():
    pdf = request.files["file"]
    reader = PyPDF2.PdfReader(pdf)

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    tts = gTTS(text)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)

    return send_file(audio_fp, mimetype="audio/mpeg", download_name="speech.mp3")
@app.route("/")
def home():
    return "PDF Voice Reader API Running"

if __name__ == "__main__":
    app.run()


