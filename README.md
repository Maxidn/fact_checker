# Fact Checker  

A simple **Retrieval-Augmented Generation (RAG)** tool that verifies claims using evidence from multiple sources, including:  

- **Wikipedia** summaries  
- **News API** (latest articles)  
- **Wikidata** (structured facts)  
- **Google Fact Check API** (high reliability fact checks)  

The system uses **OpenRouter LLMs** to analyze claims and decide if they are **Supported**, **Refuted**, or if there is **Not Enough Info**.  

---

## Features
- Retrieve evidence from multiple knowledge sources.  
- Normalize entity names (e.g., handles accents like *Pelé* → *Pele*).  
- JSON-based structured verdicts:  
  ```json
  {
    "verdict": "Supported | Refuted | Not Enough Info",
    "explanation": "Short explanation why",
    "follow_up": "If refuted, provide the correct fact",
    "source_titles": ["List of sources used"],
    "confidence": "0-100"
  }

## Installation
1. Clone the repository: <br> 
   git clone https://github.com/Maxidn/fact_checker.git <br>
   cd fact_checker
2. Create and activate a virtual environment:<br>
   python -m venv .venv <br>
  .venv\Scripts\activate   # On Windows <br>
   source .venv/bin/activate # On macOS/Linux <br>
3. Install dependencies: <br>
   pip install -r requirements.txt
4. Run the Streamlit app: <br>
  streamlit run app.py
5. Open your browser at: http://localhost:8501

## Project Structure
fact_checker/<br>
│── app.py         # Streamlit front-end<br> 
│── checker.py     # Core fact-checking logic (LLM + prompts)<br>
│── retriever.py   # Evidence retrieval from Wikipedia, News, Wikidata, Google Fact Check<br>
│── requirements.txt<br>
│── README.md

## API Keys Needed
OpenRouter API key (for LLMs)<br>
NewsAPI key (for news articles)<br>
Google Fact Check API key (for reliable fact checks)<br>

## Example Queries
"Pelé was a French football player" → Refuted ✅<br>
"Javier Milei is the President of Argentina" → Supported ✅<br>
"Colombia is a country in Asia" → Refuted ✅

## Future Improvements
Entity & Disambiguation Issues: Some examples returned poor evidence because Wikipedia sometimes fails to match the correct entity page.<br>
Possible solution: Add entity linking / fuzzy matching to map claims to the right Wikipedia/Wikidata entry.

Evidence Retrieval vs Usage: Sometimes relevant sources are retrieved but not used properly in the explanation, leading to wrong verdicts.<br>
Possible solution: Improve the reasoning chain by explicitly aligning verdicts with all retrieved evidence, not just a subset.

Over- or Under-Sensitivity to Evidence: In some cases, the model incorrectly marked claims as Supported due to partial overlaps (e.g., family members, related organizations).<br>
Possible solution: Strengthen prompt rules and add post-processing filters to enforce subject consistency.

Next Technical Steps:<br>
Integrate more reliable sources: PolitiFact, Snopes, official government datasets.<br>
Add semantic search / embedding-based retrieval for more robust evidence ranking.<br>
Evaluate accuracy with a benchmark set of claims (precision, recall, F1).<br>
Build a feedback loop: allow users to flag wrong verdicts and iteratively improve responses (RLHF-style).<br>





