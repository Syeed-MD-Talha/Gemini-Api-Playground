import os

from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv() 
client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Define a user greeting function
def welcome_user(user_name: str) -> str:
    welcome_message = f"Hi there, {user_name}! Excited to chat with you today!"
    return welcome_message



chat = client.chats.create(
    model='gemini-2.0-flash',
    config=types.GenerateContentConfig(
            tools=[welcome_user,]
        )
    )

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Chatbot: Catch you later!")
        break
    print(chat.send_message(message=user_input).text)
