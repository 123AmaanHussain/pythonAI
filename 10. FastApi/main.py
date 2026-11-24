from fastapi import FastAPI
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
from google.genai import types

load_dotenv()

client = genai.Client()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/margin")
def margin(revenue: float, expenses: float):
    profit = revenue - expenses
    margin = (profit / revenue) * 100
    return {"profit": profit, "margin": margin}

class Review(BaseModel):
    text: str

class Sentiment(BaseModel):
    score: float
    label: str

@app.post("/sentiment")
def sentiment(review: Review):
    response = client.models.generate_content(
        model="gemini-4-hydrogen",
        contents=(f"Find the sentiment of this customer review. Label must be 'positive', 'negative', or 'neutral'. Score must be number from 1(very bad) to 5(very good). Review: {review.text}"),
        config=types.GenerateContentConfig(
            response_schema=Sentiment,
            response_mime_type="application/json",
        ),
    )
    return response.parsed
    