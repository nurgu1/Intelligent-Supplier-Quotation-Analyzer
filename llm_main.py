from dotenv import load_dotenv

import json
import os
from groq import Groq
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

EXTRACTION_PROMPT = """
You are an expert procurement analyst.

Extract structured data from the supplier quotation text.
Return ONLY valid JSON. Do not include explanations.

Fields:
{
  "supplier_name": "",
  "part_name": "",
  "part_number": "",
  "unit_price": null,
  "currency": "",
  "annual_quantity": null,
  "annual_price": null,
  "tooling_costs": null,
  "delivery_terms": "",
  "payment_terms": "",
  "client_name": "<company the quote was addressed to>",

  "delivery_time": "",
  "validity_period": "",
  "MOQ": "",
  "year_by_year_pricing": [
      {"year": "", "price": "", "volume": ""}
  ],
  "technical_specifications": {},
  "other_notes": ""
}

Rules:
- Extract only what exists in the text.
- Convert numeric values (e.g., "USD 12,000" → 12000).
- If something is missing, return null or empty string.
- If multiple table rows appear (years, prices), parse them into year_by_year_pricing.
- Do not invent data.

TEXT:
"""
def extract_supplier_data(text):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You output ONLY valid JSON. "
                    "No explanations. No markdown. No text outside JSON. "
                    "If something is missing, use null."
                )
            },
            {
                "role": "user",
                "content": EXTRACTION_PROMPT + text
            }
        ],
        temperature=0,
        max_tokens=2048,
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()

    return json.loads(raw)
