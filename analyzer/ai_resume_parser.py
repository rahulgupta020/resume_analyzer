import ollama
import json

def parse_resume_with_ai(resume_text):

    prompt = f"""
    Convert this resume into structured JSON.

    Schema:
    {{
      "fresher_experience": {{"type": ""}},
      "resume_header": {{
        "full_name":"",
        "profession":"",
        "email":"",
        "phone":"",
        "address":"",
        "linkedin":"",
        "github":"",
        "website":""
      }},
      "resume_summary": {{
        "summary":""
      }},
      "resume_experiences":[
        {{
          "job_title":"",
          "employer":"",
          "location":"",
          "start_month":null,
          "start_year":null,
          "end_month":null,
          "end_year":null,
          "currently_working":false,
          "description":"",
          "skills":""
        }}
      ],
      "resume_education":[
        {{
          "institute_name":"",
          "institute_location":"",
          "degree":"",
          "field_of_study":"",
          "start_year":null,
          "end_year":null
        }}
      ],
      "resume_skills":[
        {{"skill_name":""}}
      ],
      "resume_additional":[
        {{
          "additional_title":"",
          "additional_desc":""
        }}
      ]
    }}

    Resume Text:
    {resume_text}
    """

    response = ollama.chat(
        model="llama3.2:1b",
        format="json",
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0,
            "num_ctx": 2048,
            "num_predict": 512,
            "low_vram": True
        }
    )

    return json.loads(response["message"]["content"])



