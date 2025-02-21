import os
from dotenv import load_dotenv  # Add this line to load the .env file
load_dotenv()  # Load environment variables from .env

import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from huggingface_hub import InferenceClient

# Initialize FastAPI app
app = FastAPI(title="LLM Judge API", description="Distribute 24,000 points among posts based on appeal", version="1.0")

# Read Hugging Face token from environment variable
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise Exception("HF_TOKEN environment variable not set! Please set it before running the app.")

repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
llm_client = InferenceClient(
    model=repo_id,
    token=HF_TOKEN,
    timeout=120,
)

def create_batch_prompt(posts_list, total_points=24000):
    prompt = f"""
You are given a list of social media posts. Your task is to distribute a total of {total_points} points among these posts based on how appealing and eye-catching they are.
Consider factors such as creativity, clarity, visual impact, and potential engagement.
Return your answer in JSON format with keys "post_1", "post_2", etc. Make sure that the sum of all the points equals exactly {total_points}.
Here are the posts:
"""
    for idx, post in enumerate(posts_list, start=1):
        prompt += f"{idx}. {post}\n"
    prompt += "\nProvide the JSON output now."
    return prompt

def parse_llm_json(response_text):
    try:
        # Extract the JSON block from the response text
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        json_str = response_text[start:end]
        ratings = json.loads(json_str)
        return ratings
    except Exception as e:
        print("Error parsing JSON:", e)
        return None

# Define the request payload
class JudgeRequest(BaseModel):
    posts: list[str]
    total_points: int = 24000

# Define the API endpoint
@app.post("/judge", summary="Distribute points among posts")
def judge_posts(request: JudgeRequest):
    prompt = create_batch_prompt(request.posts, request.total_points)
    try:
        response = llm_client.text_generation(prompt=prompt, max_new_tokens=500)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in text generation: {str(e)}")
    
    ratings_dict = parse_llm_json(response)
    if ratings_dict is None:
        raise HTTPException(status_code=500, detail="Could not parse the LLM output as JSON.")
    
    # Optionally, verify that the sum equals total_points
    total = sum(ratings_dict.values())
    if total != request.total_points:
        print(f"Warning: Distributed points sum to {total} instead of expected {request.total_points}")
    
    return ratings_dict
