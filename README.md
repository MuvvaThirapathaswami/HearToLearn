
**🎧 HearToLearn – AI PDF Voice Reader**

HearToLearn is a full-stack AI-powered web application that converts PDF documents into spoken audio. Users can upload a PDF file and listen to its contents using text-to-speech technology.

🔗 Live Website: https://hear-to-learn.vercel.app

⚙ Backend API: https://heartolearn.onrender.com

**🚀 Features**

  1.📄 Upload PDF documents

  2.🔊 Convert text to speech automatically

  3.🎧 Listen to document content as audio

  4.🌐 Fully deployed full-stack web app

  5.⚡ Simple and user-friendly interface

**🧠 How It Works**

  User uploads a PDF file on the website

  The frontend sends the file to the backend server

  Backend extracts text from the PDF

The text is converted into audio using AI text-to-speech

The audio file is sent back and played in the browser

****🛠 Tech Stack****
**Frontend**

  HTML

  CSS

  JavaScript

  Hosted on Vercel

**Backend**

  Python

  Flask

  Hosted on Render

**AI & Processing**

  gTTS (Google Text-to-Speech)

  PyPDF2 (PDF text extraction)

📁 Project Structure (Monorepo)
HearToLearn
  |->Backend -> app.py
  |->frontend -> index.html
  |-> requirements.txt


⚙️ Setup Instructions (Local)

1️⃣ Clone the repository
  
    git clone https://github.com/MuvvaThirapathaswami/HearToLearn.git
    
    cd HearToLearn/backend

2️⃣ Install dependencies
      
        pip install -r requirements.txt

3️⃣ Run backend server
      python app.py


Backend will run on:

      http://127.0.0.1:5000

4️⃣ Open frontend

    Open frontend/index.html in a browser.

🌍 Deployment

  Part	Platform
  Frontend	Vercel
  Backend	Render

**📌 Future Improvements**

    Drag & drop file upload

    Multiple language support

    Download audio option

    Dark mode UI

    Mobile optimization

👨‍💻 Author

Developed by **Muvva Thirapatha Swami**

Passionate about AI, full-stack development, and building real-world tech
