from flask import Flask, request, send_file, jsonify, Response
from flask_cors import CORS
from gtts import gTTS
import PyPDF2
import io
import os
import time
import tempfile

app = Flask(__name__)
CORS(app)


@app.route("/read_pdf", methods=["POST"])
def read_pdf():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        pdf = request.files["file"]
        if pdf.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        reader = PyPDF2.PdfReader(pdf)

        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "

        print("Extracted text length:", len(text))
        text = text[:1500].strip()

        if not text:
            return jsonify({"error": "No readable text found. PDF may be a scanned image."}), 400

        # ✅ Save to a REAL temp file instead of BytesIO — fixes empty audio bug
        last_error = None
        tmp_path = None

        for attempt in range(3):
            try:
                tts = gTTS(text, lang="en")

                # Write to actual temp file on disk
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tmp_path = tmp.name

                tts.save(tmp_path)

                file_size = os.path.getsize(tmp_path)
                print(f"Audio file size: {file_size} bytes (attempt {attempt + 1})")

                if file_size == 0:
                    raise Exception("gTTS saved an empty file")

                break  # success

            except Exception as e:
                last_error = str(e)
                print(f"Attempt {attempt + 1} failed: {last_error}")
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    tmp_path = None
                time.sleep(3)

        if tmp_path is None:
            return jsonify({"error": f"TTS failed after 3 attempts: {last_error}"}), 500

        # ✅ Stream the real file back, then clean it up
        def stream_and_cleanup():
            with open(tmp_path, "rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
            os.remove(tmp_path)
            print("Temp file cleaned up")

        return Response(
            stream_and_cleanup(),
            mimetype="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=audio.mp3",
                "Cache-Control": "no-cache"
            }
        )

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": f"Error: {str(e)}"}), 500


@app.route("/")
def home():
    return "HearToLearn PDF Voice Reader API is Running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
