from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()

# (a) Upload the PDF
# Newer file APIs accept general user files; purpose may appear as "user_data" in docs.
pdf = client.files.create(
    file=open("/var/home/leverhea/Downloads/Lucas_Everheart.pdf","rb"),
    purpose="user_data"
)

# (b) Call Responses API with your schema + the PDF as input
schema = {
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "contact": {
      "type": "object",
      "properties": {
        "email": {"type": "string"},
        "phone": {"type": "string"},
        "location": {"type": ["string","null"]},
        "linkedin": {"type": ["string","null"]},
        "website": {"type": ["string","null"]}
      },
      "required": ["email","phone"]
    },
    "education": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "institution": {"type": "string"},
          "degree": {"type": ["string","null"]},
          "field_of_study": {"type": ["string","null"]},
          "location": {"type": ["string","null"]},
          "start_date": {"type": ["string","null"]},
          "end_date": {"type": ["string","null"]}
        },
        "required": ["institution"]
      }
    },
    "work_experience": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "company": {"type": "string"},
          "title": {"type": "string"},
          "location": {"type": ["string","null"]},
          "start_date": {"type": ["string","null"]},
          "end_date": {"type": ["string","null"]},
          "highlights": {
            "type": "array",
            "items": {"type": "string"}
          }
        },
        "required": ["company","title"]
      }
    },
    "skills": {
      "type": "array",
      "items": {"type": "string"}
    }
  },
  "required": ["name","contact","work_experience"]
}


resp = client.chat.completions.create(
    model="gpt-4o",  # Use gpt-4o which supports file uploads
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Extract a structured resume JSON from the attached PDF. Use this schema: {schema}. Only return fields that fit the schema. Do not invent data. Return only valid JSON."
                },
                {
                    "type": "file",
                    "file": {
                        "file_id": pdf.id
                    }
                }
            ]
        }
    ],
    response_format={"type": "json_object"}
)

import json
print(json.loads(resp.choices[0].message.content))   # Parse the JSON response


