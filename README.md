## Running the project

1. **Clone the repository**

2. **Create and activate a Python virtual environment**
```bash
# Create a new virtual environment (you can name it .venv or anything else)
python3.13 -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

3. **Install the required packages**
```bash
pip install -r requirements.txt
```

4. **Set up the environment variables**  
Follow the `.env.example` file to create a `.env` file in the root directory of the project. You will need to set up the following variables:
```dotenv
OPENAI_API_KEY=
LANGSMITH_TRACING=true
LANGCHAIN_TRACING_V2=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
```

5. **Run the application**
```bash
streamlit run app.py
```

6. **Open your browser**  
Go to: [http://localhost:8501](http://localhost:8501)
