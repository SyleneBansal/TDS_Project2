from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import io
from typing import Optional
from app.utils.openai import get_openai_response
from app.utils.file_handler import save_upload_file_temporarily
from app.utils.functions import *

app = FastAPI(title="IITM Assignment API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def anyname():
    return {"deployed": True}

@app.post("/api/")
async def process_question(
    question: str = Form(...), file: Optional[UploadFile] = File(None)
):
    try:
        temp_file = None
        if file:
            temp_file = io.BytesIO(await file.read())  # Store in memory instead

        answer = await get_openai_response(question, temp_file)  # ✅ Ensure async call

        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/debug/{function_name}")
async def debug_function(
    function_name: str,
    file: Optional[UploadFile] = File(None),
    params: str = Form("{}"),
):
    try:
        temp_file_path = None
        if file:
            temp_file_path = await save_upload_file_temporarily(file)  # ✅ Ensure async

        parameters = json.loads(params)

        if temp_file_path:
            parameters["file_path"] = temp_file_path

        if function_name == "analyze_sales_with_phonetic_clustering":
            result = await analyze_sales_with_phonetic_clustering(**parameters)  # ✅ Ensure async
            return {"result": result}
        elif function_name == "calculate_prettier_sha256":
            if temp_file_path:
                result = await calculate_prettier_sha256(temp_file_path)  # ✅ Ensure async
                return {"result": result}
            else:
                return {"error": "No file provided for calculate_prettier_sha256"}
        else:
            return {"error": f"Function {function_name} not supported for direct testing"}

    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

