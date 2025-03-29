import fitz
import requests
import re
import ast  # This was missing!

def extract_units_per_table(pdf_path, table_names):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    prompt = f"""
Here is text extracted from a scientific PDF:

\"\"\"{full_text}\"\"\"

For each of these tables: {', '.join(table_names)}, extract the column names and their units if mentioned.

Return your answer ONLY in valid JSON format:
{{
  "Table_1": {{
    "r/Rp": "mm",
    "P/Dp": "Pa"
  }},
  "Table_2": {{
    "XLE/Dp": "cm"
  }}
}}
If no units are mentioned, return an empty dictionary for that table.
Do not add any explanation. Only return valid JSON.
"""

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        print("📥 Raw LLaMA response:")
        print(res.text)  # This will help debug if things go wrong

        if res.status_code != 200:
            print(f"⚠️ Ollama responded with status {res.status_code}")
            return {}

        json_data = res.json()

        if "response" not in json_data:
            print("⚠️ Ollama response missing 'response' key.")
            print("Full JSON:", json_data)
            return {}

        result = json_data["response"]

        # Use regex to extract first JSON block
        json_match = re.search(r"\{[\s\S]*\}", result)
        if not json_match:
            print("⚠️ No JSON block found in response.")
            print("Raw model output:", result)
            return {}

        clean_json = json_match.group(0)

        # Print the cleaned JSON block for debugging
        print("✅ Clean JSON block extracted:")
        print(clean_json)

        return ast.literal_eval(clean_json)

    except Exception as e:
        print("⚠️ Unit extraction failed:", e)
        return {}
