import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from pydantic import BaseModel
from typing import Dict
import uuid

# Initialize FastAPI app
app = FastAPI(title="BrepMFR API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Warning: SUPABASE_URL or SUPABASE_KEY not set.")
    supabase: Client = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Placeholder for core logic imports
# from core.step_to_graph import step_to_graph
# from core.inference import predict
# from core.geometry import convert_step_to_glb

class AnalysisResult(BaseModel):
    glb_url: str
    features: Dict[str, str]

@app.get("/")
async def root():
    return {"message": "BrepMFR API is running"}

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_step_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.stp', '.step')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .stp or .step files are allowed.")

    # Create a temporary directory for processing
    temp_id = str(uuid.uuid4())
    temp_dir = f"temp/{temp_id}"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # TODO: Upload raw STEP to Supabase
        
        # TODO: Convert STEP to GLB
        # glb_path = convert_step_to_glb(file_path, temp_dir)
        
        # TODO: Upload GLB to Supabase
        # glb_url = upload_to_supabase(glb_path, "models")
        
        # TODO: Run Inference
        # graph = step_to_graph(file_path)
        # predictions = predict(graph)
        
        # Placeholder response
        return {
            "glb_url": "https://placeholder.url/model.glb",
            "features": {"Face_0": "Hole", "Face_1": "Plane"}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
