from fastapi import FastAPI, File, UploadFile
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Enable CORS for React and Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Change this for production)
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ✅ Streamlit Backend URL (Update with your actual Streamlit API URL)
STREAMLIT_API_URL = "https://docex-backend-yjpzesvjjhttbdnp4h8upv.streamlit.app"

# ✅ API 1: Receive image from React and forward to Streamlit
@app.post("/api/upload")
async def upload_to_streamlit(file: UploadFile = File(...)):
    """Receives file from React and forwards it to Streamlit"""

    # ✅ Read file data
    files = {"file": (file.filename, file.file, file.content_type)}

    # ✅ Forward file to Streamlit for processing
    response = requests.post(STREAMLIT_API_URL, files=files)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to process image in Streamlit"}

# ✅ API 2: Receive processed data from Streamlit and return to React
@app.post("/api/return")
async def return_to_react(data: dict):
    """Receives processed results from Streamlit and sends them to React"""

    extracted_text = data.get("text")
    processed_image = data.get("image")

    return {
        "text": extracted_text,
        "image": processed_image
    }
