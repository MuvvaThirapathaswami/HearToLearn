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
        # ⏱️ Rate limiting
        current_time = time.time()
        if current_time - LAST_CALL_TIME < COOLDOWN:
            return jsonify({"error": "Please wait 5 seconds before retrying"}), 429

        LAST_CALL_TIME = current_time

        # 📂 File check
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']

        # 📏 File size check (SAFE)
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)

        if file_length > 5 * 1024 * 1024:
            return jsonify({"error": "File too large (max 5MB)"}), 400

        # 📄 Read PDF safely
        try:
            pdf_reader = PyPDF2.PdfReader(file)
        except Exception:
            return jsonify({"error": "Invalid or corrupted PDF"}), 400

        text = ""

        for page in pdf_reader.pages:
            try:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
            except:
                continue

        if not text.strip():
            return jsonify({"error": "No readable text found"}), 400

        # 🧹 Clean text (VERY IMPORTANT)
        text = re.sub(r'\s+', ' ', text)
        text = text.encode('ascii', 'ignore').decode()

        # ✂️ Limit text
        text = text[:2000]

        # 🔊 Convert to speech (SAFE)
        try:
            tts = gTTS(text=text, lang='en')
        except Exception as e:
            print("TTS INIT ERROR:", str(e))
            return jsonify({"error": "TTS initialization failed"}), 500

        audio_bytes = io.BytesIO()

        try:
            tts.write_to_fp(audio_bytes)
        except Exception as e:
            print("TTS WRITE ERROR:", str(e))
            return jsonify({"error": "Audio generation failed"}), 500

        audio_bytes.seek(0)

        return send_file(
            audio_bytes,
            mimetype="audio/mpeg",
            as_attachment=False
        )

    except Exception as e:
        print("FULL ERROR:", str(e))
        return jsonify({"error": "Server crashed. Check logs."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
