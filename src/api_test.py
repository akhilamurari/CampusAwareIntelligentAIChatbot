import google.generativeai as genai
from src.core.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)
response = model.generate_content("Reply exactly: Yes mate")
print(response.text)  # Should print: Yes mate