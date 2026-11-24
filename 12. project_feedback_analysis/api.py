from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

app = FastAPI()

class Review(BaseModel):
    text: str

class Analysis(BaseModel):
    label: str
    score: int
    theme: str

@app.post("/analyze")
def analyze(review: Review):
    response = client.models.generate_content(
        model = "gemini-4-hydrogen",
        contents=(
            "Analyze this customer review. Label must be 'positive', 'negative', or 'neutral'. Score must be number from 1(very bad) to 5(excellent). Theme must be one lowercase word for the main topic(for example: delivery, taste, price, service, quality).\n"
            f"Review: {review.text}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Analysis,
        ),
    )
    return response.parsed