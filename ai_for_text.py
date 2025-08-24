
from openai import OpenAI
import re

with open("markdown_files/api_key.json", "r") as file:
    import json
    api_key = json.load(file)


# Open and read the contents of code.py
with open('static/tutorial.js', 'r') as file:
    code_content1 = file.read()

with open('static/tutorial.css', 'r') as file:
    code_content2 = file.read()

client = OpenAI(api_key=api_key["openai_api_key"])

def get_response(prompt):
    response = client.responses.create(
        model="gpt-4.1",
        input=f"{prompt}"
    )

    return response.output_text

prompt = f'''
Act like a very experienced python flask developer. 
Review the code and provide the corrected version.
Rule 1: Deep think before you act.
Rule 2: Any explanation should be python comment.
Rule 3: Respond only with the code, no other text.
JS:{code_content1}
CSS:{code_content2}

'''



# Example usage
response = get_response(prompt)


with open("response.py", "w") as file:
    file.write(response.replace("```python", "").replace("```", "").strip())

