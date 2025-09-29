import wikipedia
import warnings
from wikipedia.exceptions import DisambiguationError, PageError
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import unicodedata

warnings.filterwarnings("ignore", category=UserWarning, module="wikipedia")
wikipedia.set_lang("en")  # Default language


# Normalization Helper

def normalize_text(text):
    """Remove accents/diacritics and lowercase the text."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.lower()


# Wikipedia Retrieval

def retrieve_top_wikipedia_summaries(query, num_results=4):
    search_results = wikipedia.search(query, results=num_results)
    summaries = []

    for title in search_results:
        try:
            page = wikipedia.page(title, auto_suggest=False)
            summaries.append({
                "title": title,
                "summary": page.summary,
                "url": page.url
            })
        except (DisambiguationError, PageError):
            continue
        except Exception as e:
            print(f"Error with page {title}: {e}")
    
    return summaries


# Wikidata Retrieval

def query_wikidata(entity):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(f"""
    SELECT ?itemLabel ?valueLabel WHERE {{
      ?item rdfs:label "{entity}"@en.
      ?item ?property ?value.
      ?value rdfs:label ?valueLabel.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }} LIMIT 10
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [res["valueLabel"]["value"] for res in results["results"]["bindings"]]


# News Retrieval

def get_news_articles(query):
    api_key = "bce075bd88cc498587c9f8b0cb561a74"  
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    return [article["title"] + ": " + article["description"] for article in data.get("articles", [])[:3]]


# Google Fact Check API

API_KEY = "AIzaSyAIUjg3seo8eWk0y-jWVehCZpM1RoeBEGw"
BASE_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

def get_google_fact_checks(query):
    try:
        params = {"query": query, "key": API_KEY}
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json().get("claims", [])
    except Exception as e:
        print(f"Google Fact Check API error: {e}")
        return []


# Unified Retriever

def retrieve_all_sources(query, entity=None):
    # Retrieve with original query
    wikipedia_original = retrieve_top_wikipedia_summaries(query)
    news_original = get_news_articles(query)
    wikidata_original = query_wikidata(query)
    google_original = get_google_fact_checks(query)

    # Retrieve with normalized query
    normalized_query = normalize_text(query)
    wikipedia_normalized = retrieve_top_wikipedia_summaries(normalized_query)
    news_normalized = get_news_articles(normalized_query)
    wikidata_normalized = query_wikidata(normalized_query)
    google_normalized = get_google_fact_checks(normalized_query)

    # Merge results (avoid duplicates)
    all_sources = {
        "Wikipedia": wikipedia_original + [item for item in wikipedia_normalized if item not in wikipedia_original],
        "News": news_original + [item for item in news_normalized if item not in news_original],
        "Wikidata": wikidata_original + [item for item in wikidata_normalized if item not in wikidata_original],
        "GoogleFactCheck": google_original + [item for item in google_normalized if item not in google_original]
    }
    return all_sources
