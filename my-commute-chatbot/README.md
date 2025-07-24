Commute Recommendation Chatbot with Agent-Based Simulation
This project is a Streamlit web application that acts as a personalized commuting recommendation chatbot. It leverages a Theory of Planned Behavior (TPB) driven commuter dataset and a simplified agent-based simulation (ABS) to provide tailored advice, especially considering potential crowding.

Features
Interactive Chatbot: Engage in a conversation to get commuting advice.

Personalized Recommendations: Recommendations are based on a commuter's behavioral profile (Attitude, Subjective Norm, Perceived Behavioral Control).

Crowding Insights: The chatbot can incorporate insights from a simplified agent-based simulation to inform recommendations about public transport crowding.

Gemini API Integration: Uses the Google Gemini API for natural language understanding and generation.

Setup Instructions
1. Clone the Repository (or create files manually)
If you're starting from scratch, create the directory structure as described in the project.

2. Install Dependencies
Navigate to the my-commute-chatbot directory in your terminal and install the required Python packages:

pip install -r requirements.txt

3. Set up Gemini API Key
You need a Gemini API key to run the chatbot.

Create a .streamlit directory in the root of your project if it doesn't exist.

Inside .streamlit, create a file named secrets.toml.

Add your Gemini API key to secrets.toml in the following format:

GEMINI_API_KEY="your_gemini_api_key_here"

Replace "your_gemini_api_key_here" with your actual Gemini API key.

Security Note: Never hardcode your API key directly into your Python scripts, especially if you plan to share your code publicly. secrets.toml is a secure way to manage secrets in Streamlit.

4. Prepare the Data
Ensure the data directory exists and contains commuter_data.csv with the sample data provided in the project.

5. Run the Streamlit Application
From the root directory of your project (my-commute-chatbot), run the Streamlit app using the following command:

streamlit run app.py

This will open the application in your web browser.

How to Use the Chatbot
Select a Commuter Profile: Choose a CommuterID from the dropdown menu to simulate a user with a specific TPB profile from the dataset. This will influence the recommendations.

Interact with the Chatbot: Type your commuting-related questions or concerns into the chat input box.

Get Recommendations: The chatbot will provide personalized recommendations based on the selected profile and its understanding of your query, potentially incorporating crowding insights.

Project Structure
app.py: The main Streamlit application script.

src/: Contains core logic modules.

agent_simulation.py: Simplified Agent-Based Model for crowding.

chatbot_logic.py: Handles Gemini API calls and chat interactions.

recommendation_engine.py: Generates personalized recommendations.

data/: Stores the commuter_data.csv dataset.

.streamlit/secrets.toml: Secure storage for API keys.

requirements.txt: Lists all Python dependencies.

Customization and Expansion
Enhance Agent-Based Model:

Implement more realistic movement, schedules, and vehicle capacities.

Add dynamic interactions between agents (e.g., agents seeing crowded vehicles and reacting).

Integrate spatial data (e.g., a simplified road/PT network).

Refine Recommendation Logic:

Develop more sophisticated rules for mapping TPB scores to specific advice.

Allow users to input their own TPB scores directly rather than selecting from the dataset.

Incorporate more factors (e.g., weather, real-time traffic data).

Improve Chatbot Intelligence:

Use more advanced prompt engineering for the Gemini API to better understand nuanced user queries.

Implement conversation history for more coherent interactions.

User Interface:

Add visualizations for crowding data or recommendation impact.

Allow users to "rate" recommendations for feedback.