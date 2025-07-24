# src/chatbot_logic.py

import google.generativeai as genai
import os

class Chatbot:
    def __init__(self, gemini_api_key):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash') # Changed from 'gemini-pro' to 'gemini-1.5-flash'
        self.conversation_history = []

    def get_chat_response(self, user_message, system_prompt="You are a helpful commuting assistant. Provide concise and relevant information."):
        """
        Gets a response from the Gemini API.
        """
        # Gemini API typically uses a list of messages with roles 'user' and 'model'
        # System instructions are often best integrated into the first user prompt or a dedicated safety setting.
        # For simplicity, we'll prepend the system prompt to the user message for now.

        # Prepare messages for Gemini API
        messages = []
        # Add system prompt as part of the initial user message or context
        if not self.conversation_history:
            full_user_message = f"{system_prompt}\n\nUser: {user_message}"
        else:
            full_user_message = f"User: {user_message}"

        # Append existing history in Gemini format
        for msg in self.conversation_history:
            if msg["role"] == "user":
                messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                messages.append({"role": "model", "parts": [msg["content"]]})

        messages.append({"role": "user", "parts": [full_user_message]})

        try:
            response = self.model.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7, # Controls randomness: lower for more focused, higher for more creative
                    max_output_tokens=150
                )
            )
            chat_response = response.text
            self.conversation_history.append({"role": "user", "content": user_message}) # Store original user message
            self.conversation_history.append({"role": "assistant", "content": chat_response})
            return chat_response
        except Exception as e:
            return f"Gemini API Error: {e}"

# Example usage (for testing this module directly)
if __name__ == "__main__":
    # For local testing, you might temporarily set your API key here
    # os.environ["GEMINI_API_KEY"] = "YOUR_TEST_GEMINI_API_KEY"
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable not set. Cannot run chatbot test.")
    else:
        chatbot = Chatbot(api_key)
        print("Chatbot initialized. Type 'exit' to quit.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            response = chatbot.get_chat_response(user_input)
            print(f"Bot: {response}")
