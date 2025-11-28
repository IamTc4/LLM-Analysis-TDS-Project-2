import os
import google.generativeai as genai

# Inject credentials explicitly
os.environ["GOOGLE_API_KEY"] = "AIzaSyDD8cUMuIHAbyVn4EO30uzg-Y4hA2VaX6Q"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
