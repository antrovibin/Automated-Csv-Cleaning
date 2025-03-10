from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join("templates", "index.html"))

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (modify for security)
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define folders
UPLOAD_FOLDER = "uploads"
CLEANED_FOLDER = "cleaned"

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a CSV file, cleans it (removes NaN and 0 values), and provides a download link.
    """
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Load CSV using Pandas
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"error": f"Invalid CSV file: {str(e)}"}

    # Replace 0 values with NaN (only for numeric columns)
    df.replace(0, pd.NA, inplace=True)

    # Drop rows that are fully NaN
    df_cleaned = df.dropna(how='all')

    # Drop columns that are fully NaN (optional)
    df_cleaned = df_cleaned.dropna(axis=1, how='all')


    # Save cleaned file
    cleaned_filename = f"cleaned_{file.filename}"
    cleaned_file_path = os.path.join(CLEANED_FOLDER, cleaned_filename)
    df_cleaned.to_csv(cleaned_file_path, index=False)

    print(f"Cleaned file saved at: {cleaned_file_path}")

    return {"message": "Processing completed", "download_url": f"/download/{cleaned_filename}"}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Serves the cleaned CSV file for download.
    """
    file_path = os.path.join(CLEANED_FOLDER, filename)

    # Check if file exists
    if not os.path.exists(file_path):
        return {"error": "File not found!"}

    return FileResponse(file_path, media_type="text/csv", filename=filename)