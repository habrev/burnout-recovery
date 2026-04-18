import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_burnout(text):
    config = types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema={
            'type': 'object',
            'properties': {
                'primary_emotion': {'type': 'string'},
                'stress_level_int': {'type': 'integer'},
                'burnout_risk_score': {'type': 'number'},
                'context_summary': {'type': 'string'}
            },
            'required': ['primary_emotion', 'stress_level_int', 'burnout_risk_score', 'context_summary']
        }
    )

    prompt = f"""
    Act as a clinical data extractor for a Gen Z professional burnout app.
    Analyze the following telemetry and return data matching the schema.
    stress_level_int must be between 1 and 10.
    burnout_risk_score must be between 0.0 and 1.0.

    User Telemetry: {text}
    """

    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt,
            config=config
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"GenAI SDK Error: {e}")
        return None
