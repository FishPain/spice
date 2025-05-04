# spice

## What this project does
A website that will scrape the news page of various gov agencies once a day. 

The scraped content will be passed through a LLM to determine:
•⁠  ⁠relevance (can sit spice partner with them?)
•⁠  ⁠⁠target company (any companies that they licensed to, or is it an inter gov agency effort)
•⁠  ⁠⁠opportunity (what are the problems identified through the article and how spice can come into play.)
•⁠  ⁠⁠retrieve company events (if any)
•⁠  ⁠⁠auto email drafting (auto draft cold email to be sent - requires manual sending)

## Running the project
1. Clone the repository
2. Install the required packages
```bash
# require python 3.13 or higher
pip install -r requirements.txt
```
3. Set up the environment variables
```bash
export OPENAI_API_KEY=your_api_key
```
4. Run the application
```bash
streamlit run app.py
```
5. Open your browser and go to `http://localhost:8501`