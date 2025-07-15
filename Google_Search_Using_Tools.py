API_KEY = "YOUR API KEY"
prompt="""

Suppose you are one of the best medicine specialist. You can find any medicine name and isntruction using google search.

Task:
1. Now read the medicine prescription carefully and search each medicine name from google
2. Always take result from MedEx or Arogga
3. If Google shows a "Did you mean" or suggests a correction for this medicine name, give me ONLY the corrected medicine name.


Read the medicine name and dosages very carefully and give me the perfect output .
Output format:
Medicine 1:
Medicine name:
Dosage: 1+0+0

Medicine 2:
Medicine name: Napa
Dosage: 1+1+0
"""
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

client = genai.Client(api_key=API_KEY)
model_id = "gemini-2.0-flash"

image = client.files.upload(file="/content/1.jpg")

google_search_tool = Tool(
    google_search = GoogleSearch()
)

response = client.models.generate_content(
    model=model_id,
    contents=[prompt,image],
    config=GenerateContentConfig(
        tools=[google_search_tool],
        response_modalities=["TEXT"],
        temperature=0.2
    )
)


print(response.text)
