import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="LLM Judge API with ORA API",
    description="Distribute points among posts based on appeal using ORA API",
    version="1.0"
)

# Retrieve ORA API key from environment variables
ORA_API_KEY = os.getenv("ORA_API_KEY")
if not ORA_API_KEY:
    raise Exception("ORA_API_KEY environment variable not set! Please set it before running the app.")

# ORA API endpoint for chat completions
ORA_CHAT_COMPLETIONS_URL = "https://api.ora.io/v1/chat/completions"

def create_batch_prompt(users, posts, total_points=24000):
    prompt = f"""
You are given a list of social media posts along with their corresponding creator names.
Your task is to distribute a total of {total_points} points among these posts based solely on the text content of each post.
...
Here are the posts with their creators as well so remeber to use those names and put them in the creator fields in the JSON output.:
"""
    for idx, post in enumerate(posts, start=1):
        text = post.get("text", "")
        creator_name = users[idx-1] if idx-1 < len(users) else f"post_{idx}"
        prompt += f"{idx}. Creator: {creator_name}\n   Tweet: {text}\n"
    prompt += "\nProvide the JSON output now."
    print(prompt)
    return prompt

def parse_ora_response(response_json):
    """
    Extracts and parses the assistant message content from the ORA API response.
    Tries to extract a JSON block from the message if the entire content isn't valid JSON.
    """
    try:
        choices = response_json.get("choices", [])
        if not choices:
            raise ValueError("No choices found in response.")
        # Get the assistant message content
        message_content = choices[0].get("message", {}).get("content", "")
        
        # Try parsing the whole content first
        try:
            return json.loads(message_content)
        except Exception:
            # If that fails, try to extract a JSON substring.
            start = message_content.find('{')
            end = message_content.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = message_content[start:end+1]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON block found in response message")
    except Exception as e:
        print("Error parsing ORA response:", e)
        return None

# New JudgeRequest schema that accepts users, posts, and total_points
class JudgeRequest(BaseModel):
    users: list[str]
    posts: list[dict]
    total_points: int = 24000

@app.post("/judge", summary="Distribute points among posts using ORA API")
def judge_posts(request: JudgeRequest):
    # Create the prompt using both users and posts
    prompt = create_batch_prompt(request.users, request.posts, request.total_points)
    # ORA API expects a messages array; here we send the prompt as a user message.
    messages = [{"role": "user", "content": prompt}]
    
    payload = {
        "model": "deepseek-ai/DeepSeek-V3",  # Adjust model if necessary
        "messages": messages
    }
    
    headers = {
        "Authorization": f"Bearer {ORA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        ora_response = requests.post(
            ORA_CHAT_COMPLETIONS_URL,
            headers=headers,
            json=payload,
            timeout=120  # Adjust timeout as needed
        )
        print("ORA API response object:", ora_response)
        ora_response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling ORA API: {str(e)}")
    
    try:
        response_json = ora_response.json()
        print("Response JSON from ORA API:", response_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing ORA API response as JSON: {str(e)}")
    
    # Parse the assistant's response to get the distributed points in JSON format
    ratings_dict = parse_ora_response(response_json)
    if ratings_dict is None:
        raise HTTPException(status_code=500, detail="Could not parse the ORA API output as JSON.")
    
    # Optionally, verify that the total distributed points equals total_points
    # total = sum(ratings_dict.values())
    # if total != request.total_points:
    #     print(f"Warning: Distributed points sum to {total} instead of expected {request.total_points}")
    
    return ratings_dict

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
