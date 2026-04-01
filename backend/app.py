from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from gtts import gTTS
import PyPDF2
import io
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "HearToLearn Backend Running"

@app.route("/read_pdf", methods=["POST"])
def read_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']

        # Read PDF
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""

        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        if not text.strip():
            return jsonify({"error": "No text found in PDF"}), 400

        # LIMIT TEXT (important for gTTS)
        text = text[:3000]

        # Convert text to speech
        tts = gTTS(text=text, lang='en')

        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        return send_file(
            audio_bytes,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="output.mp3"
        )

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
