from flask import Flask, request, send_file
from flask_cors import CORS
from gtts import gTTS
import PyPDF2
import io
import os

app = Flask(__name__)
CORS(app)


@app.route("/read_pdf", methods=["POST"])
def read_pdf():
    try:
        pdf = request.files["file"]
        reader = PyPDF2.PdfReader(pdf)

        text = ""

        # 🔍 Extract text safely
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        print("Extracted text length:", len(text))

        # 🔥 LIMIT TEXT (IMPORTANT)
        text = text[:1500]

        # 🚨 Handle empty text
        if not text.strip():
            return "No readable text found in PDF", 400

        # 🔊 Convert to speech
        tts = gTTS(text)

        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)

        return send_file(
            audio_fp,
            mimetype="audio/mpeg",
            as_attachment=False
        )

    except Exception as e:
        print("ERROR:", str(e))
        return f"Error generating audio: {str(e)}", 500


@app.route("/")
def home():
    return "PDF Voice Reader API Running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
