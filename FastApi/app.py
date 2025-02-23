from fastapi import FastAPI, File, UploadFile
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Enable CORS for React and Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Change for production)
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ✅ Streamlit Backend URL
STREAMLIT_API_URL = "https://your-streamlit-app.streamlit.app/process"

@app.post("/api/upload")
async def upload_to_streamlit(file: UploadFile = File(...), doc_type: str = "Aadhar"):
    """Receives file from React and forwards it to Streamlit for processing"""
    
    # ✅ Read file data
    files = {"file": (file.filename, file.file, file.content_type)}

    # ✅ Send file and document type to Streamlit
    response = requests.post(f"{STREAMLIT_API_URL}?doc_type={doc_type}", files=files,verify=False)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to process {doc_type} in Streamlit"}

# ✅ Receive processed results from Streamlit and return to React
@app.post("/api/return")
async def return_to_react(data: dict):
    """Receives processed results from Streamlit and sends them to React"""

    extracted_text = data.get("text")
    processed_image = data.get("image")

    return {
        "text": extracted_text,
        "image": processed_image
    }
