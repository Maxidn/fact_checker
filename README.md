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
1. Clone the repository: 
 git clone https://github.com/Maxidn/fact_checker.git <br>
 cd fact_checker
2. Create and activate a virtual environment:<br>
   python -m venv .venv <br>
  .venv\Scripts\activate   # On Windows <br>
   source .venv/bin/activate # On macOS/Linux <br>
3. Install dependencies:
   pip install -r requirements.txt


