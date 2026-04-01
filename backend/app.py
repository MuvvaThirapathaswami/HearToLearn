from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from gtts import gTTS
import PyPDF2
import io
import os
import time
import re

app = Flask(__name__)
CORS(app)

LAST_CALL_TIME = 0
COOLDOWN = 5

@app.route("/")
def home():
    return "Backend Running 🚀"

@app.route("/read_pdf", methods=["POST"])
def read_pdf():
    global LAST_CALL_TIME

    try:
        current_time = time.time()
        if current_time - LAST_CALL_TIME < COOLDOWN:
            return jsonify({"error": "Wait a few seconds"}), 429

        LAST_CALL_TIME = current_time

        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']

        # File size check
        file_bytes = file.read()
        if len(file_bytes) > 5 * 1024 * 1024:
            return jsonify({"error": "File too large"}), 400

        file.seek(0)

        pdf_reader = PyPDF2.PdfReader(file)
        text = ""

        for page in pdf_reader.pages:
            try:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
            except:
                continue

        if not text.strip():
            return jsonify({"error": "No readable text"}), 400

        # Clean text
        text = re.sub(r'\s+', ' ', text)
        text = text.encode('ascii', 'ignore').decode()

        text = text[:2500]

        try:
            tts = gTTS(text=text, lang='en')
        except:
            return jsonify({"error": "TTS failed"}), 500

        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        return send_file(audio_bytes, mimetype="audio/mpeg")

    except Exception as e:
        print("FULL ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
