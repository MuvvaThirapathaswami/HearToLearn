from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from gtts import gTTS
import PyPDF2
import io
import os
import time

app = Flask(__name__)
CORS(app)

# ⏱️ Global cooldown (prevent spam requests)
LAST_CALL_TIME = 0
COOLDOWN = 5  # seconds

@app.route("/")
def home():
    return "HearToLearn Backend Running 🚀"

@app.route("/read_pdf", methods=["POST"])
def read_pdf():
    global LAST_CALL_TIME

    try:
        # 🚫 Rate limiting
        current_time = time.time()
        if current_time - LAST_CALL_TIME < COOLDOWN:
            return jsonify({"error": "Too many requests. Please wait a few seconds."}), 429

        LAST_CALL_TIME = current_time

        # 📂 Check file
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']

        # 📄 Read PDF
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""

        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        if not text.strip():
            return jsonify({"error": "No readable text found in PDF"}), 400

        # ✂️ Limit text (avoid gTTS crash)
        MAX_CHARS = 2500
        text = text[:MAX_CHARS]

        # 🔊 Convert to speech
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
        return jsonify({"error": "Server error. Try again later."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
