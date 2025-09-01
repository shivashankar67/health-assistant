import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import httpx
import base64

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Personalized AI Health Assistant API",
    description="A backend API for a health assistant providing tailored suggestions."
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Body Model ---
class HealthInput(BaseModel):
    text_input: Optional[str] = None
    image_data: Optional[str] = None

# --- API Key for Gemini (Provided by user) ---
GEMINI_API_KEY = "AIzaSyD4688hV8zKZF5pFiELetYslhhPFF5UXS0"

# --- System Instruction for Gemini ---
SYSTEM_INSTRUCTION = "You are a friendly and helpful AI Health Assistant. Your sole purpose is to provide advice on general fitness, nutrition, and mental health. " \
"provide medical advice, diagnoses, or prescriptions. For any health concerns " \
"Do not answer questions outside of your specified topics. Maintain a positive and encouraging tone. For example, you can answer 'What are some foods rich in Vitamin C?' but not 'What medicine should I take for a fever?'"

# --- API Endpoint for Health Suggestions ---
@app.post("/api/health-suggestions")
async def get_suggestions(input: HealthInput):
    """
    Receives user input (text or image) and provides personalized health suggestions using the Gemini API.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key is not set. Please add your key to the GEMINI_API_KEY variable in main.py.")
    
    if not input.text_input and not input.image_data:
        raise HTTPException(status_code=400, detail="Either text_input or image_data must be provided.")

    try:
        # Prepare the request payload for Gemini
        parts = []
        if input.text_input:
            parts.append({"text": input.text_input})
        if input.image_data:
            parts.append({
                "inlineData": {
                    "mimeType": "image/jpeg",
                    "data": input.image_data
                }
            })

        payload = {
            "contents": [
                {
                    "parts": parts
                }
            ],
            "systemInstruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION}]
            },
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "text_response": {
                            "type": "STRING",
                            "description": "A health-related suggestion or message."
                        }
                    }
                }
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}",
                json=payload
            )
            response.raise_for_status()
            
            # Extract the generated JSON and return it directly
            response_json = response.json()
            generated_json = json.loads(response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}"))

        return {"success": True, "data": generated_json}

    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to get suggestions from AI model: {e.response.text}")
    except json.JSONDecodeError:
        print(f"JSONDecodeError: Failed to decode JSON from response.")
        raise HTTPException(status_code=500, detail="The AI model returned an unexpected response format.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# --- Main Entry Point ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
