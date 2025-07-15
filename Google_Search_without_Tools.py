import google.generativeai as genai
import os
from PIL import Image
import requests
import json

# 1. Configure the Gemini API key
API_KEY = "Your API key"
if not API_KEY:
    API_KEY = input("Please enter your Google API key: ")
try:
    genai.configure(api_key=API_KEY)
    print("Gemini API key configured.")
except Exception as e:
    print(f"Error configuring API key: {e}")
    exit()

# 2. Define the Google Search function
def google_search_medicine(predicted_name: str) -> str:
    GOOGLE_SEARCH_API_KEY = "AIzaSyA6-8U6_92GuMXpYauzPQXP0Zzgp5RgVUo"
    SEARCH_ENGINE_ID = "86f0eb0de71e94468"
    
    print(f"Searching Google for medicine name: {predicted_name}")
    
    try:
        # Create the search query - looking specifically for similar medicines
        query = f"{predicted_name} medicine bangladesh"
        
        # Make the API request to Google Custom Search
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_SEARCH_API_KEY,
            'cx': SEARCH_ENGINE_ID,
            'q': query
        }
        
        response = requests.get(url, params=params)
        search_results = response.json()
        
        # Extract the most relevant medicine name from search results
        if 'items' in search_results and len(search_results['items']) > 0:
            # Check if Google has any spelling suggestions
            if 'spelling' in search_results and 'correctedQuery' in search_results['spelling']:
                corrected_query = search_results['spelling']['correctedQuery']
                print(f"Google suggested correction: {corrected_query}")
                # Extract just the medicine name from the corrected query
                corrected_medicine = corrected_query.replace("medicine bangladesh", "").strip()
                if corrected_medicine:
                    return corrected_medicine
            
            # Extract medicine name from the first result title
            first_result_title = search_results['items'][0]['title']
            # Extract just the likely medicine name from the title
            # This might need more sophisticated parsing depending on the search results
            medicine_name = first_result_title.split('-')[0].strip()
            print(f"Found similar medicine from Google: {medicine_name}")
            return medicine_name
        else:
            print("No search results found")
            return predicted_name
            
    except Exception as e:
        print(f"Error in Google Search: {e}")
        return predicted_name

# 3. Initialize the Gemini model
try:
    model = genai.GenerativeModel( 
        model_name="gemini-2.0-flash",  # Make sure this is a valid model name
        tools=[google_search_medicine]
    )
    print(f"Model {model._model_name} initialized with 'google_search_medicine' tool.")
except Exception as e:
    print(f"Error initializing model: {e}")
    print("Please check if the selected model supports multimodal input and function calling.")
    model = None

# 4. Prepare the input (Image and Text Prompt)
image_path = input("Enter the path to the handwritten prescription image (e.g., prescription.jpg): ")
try:
    prescription_image = Image.open(image_path)
    print(f"Successfully loaded image: {image_path}")
except Exception as e:
    print(f"Error opening image: {e}")
    prescription_image = None

# Define the prompt for the LLM
prompt = """
Suppose you are one of the best pharmacists in Bangladesh. You have knowledge of many medicine names. 
I have given you a medicine prescription, and you need to provide me with the list of medicines written in the prescription.

For each medicine name you identify:
1. First, predict the medicine name based on what you see in the image
2. Use the google_search_medicine tool to verify if your prediction is correct or find a more accurate name
3. If the tool returns a different medicine name, use that corrected name instead

Example: If you predict "Papa" and the tool returns "Napa", you should list "Napa" in your final result.

Now give me the medcine list 
"""

# 5. Start a chat session and send the multimodal input
if model and prescription_image:
    try:
        print("\nSending request to Gemini model...")
        chat_session = model.start_chat(enable_automatic_function_calling=True)
        response = chat_session.send_message([prompt, prescription_image])

        print("\n--- Model Response ---")
        print(response.text)
        print("--------------------")
    except Exception as e:
        print(f"\nAn error occurred during the chat interaction: {e}")
else:
    print("\nModel or image not loaded successfully. Cannot proceed with chat.")
