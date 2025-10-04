import google.generativeai as genai
from config import GEMINI_API_KEY

class GeminiHandler:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_response(self, user_question, scraped_data):
        """Generate response using Gemini AI based on scraped data"""
        
        prompt = f"""
        User Question: {user_question}
        
        Context from Rajasthan tourism websites:
        {scraped_data}
        
        Based on the above context from official Rajasthan tourism websites, 
        provide a helpful and accurate answer to the user's question.
        If the information is not available in the context, politely inform the user.
        
        Answer in Hindi or English based on user's language preference.
        Keep the response concise and informative.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
