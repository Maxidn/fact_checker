import openai
from retriever import retrieve_all_sources
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter client setup

client = openai.OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


# Filter evidence by entity

def filter_sources_by_entity(all_sources, entity):
    if not isinstance(entity, str):
        entity = str(entity)  # Fallback safeguard

    filtered = {}
    for source_name, entries in all_sources.items():
        if isinstance(entries, list):
            new_entries = []
            for entry in entries:
                text = ""
                if isinstance(entry, dict):
                    text = entry.get("title", "") + " " + entry.get("summary", "")
                else:
                    text = str(entry)

                # ✅ Safe check: only split if string
                if any(part.lower() in text.lower() for part in entity.split()):
                    new_entries.append(entry)
            filtered[source_name] = new_entries
        else:
            filtered[source_name] = entries
    return filtered




# Main Analyzer

def analyze_claim_with_openrouter(claim, entity):
    # Step 1: retrieve and filter
    if not isinstance(entity, str):
        print(f" Received non-string entity in checker: {type(entity)}. Using claim instead.")
        entity = str(claim)
    all_sources = retrieve_all_sources(claim, entity)
    all_sources = filter_sources_by_entity(all_sources, entity)

    # Step 2: format evidence
    formatted_sources = []
    for source_name, entries in all_sources.items():
        if isinstance(entries, list):
            for entry in entries:
                if isinstance(entry, dict):
                    title = entry.get("title", "")
                    summary = entry.get("summary", entry.get("description", ""))
                    if source_name.lower() == "googlefactcheck":
                        formatted_sources.append(
                            f"[{source_name.upper()} - HIGH RELIABILITY] Title: {title}\nSummary: {summary}"
                        )
                    else:
                        formatted_sources.append(
                            f"[{source_name}] Title: {title}\nSummary: {summary}"
                        )
                else:
                    if source_name.lower() == "googlefactcheck":
                        formatted_sources.append(f"[{source_name.upper()} - HIGH RELIABILITY] {entry}")
                    else:
                        formatted_sources.append(f"[{source_name}] {entry}")
        else:
            formatted_sources.append(f"[{source_name}] {str(entries)}")

    combined_evidence = "\n\n".join(formatted_sources)

    # Step 3: confidence heuristic
    if not all_sources.get("Wikipedia"):
        max_confidence = 50
    else:
        max_confidence = 100

    # Step 4: prompt
    prompt = f"""
You are a fact-checking assistant. Your goal is to verify whether a claim is true or false using the provided evidence.

Claim: "{claim}"

Evidence is provided from multiple sources: Wikipedia, Wikidata, News, and Google Fact Check.

Rules:
- Prioritize **Google Fact Check** results if available, since they are the most reliable.
- If Google Fact Check contradicts other sources, prefer Google Fact Check.
- If a name or surname is mentioned, check on Wikipedia using the full name. For example if the claim is about "Einstein", look for "Albert Einstein".
- Supported: Only classify a claim as Supported if the evidence EXACTLY confirms the subject (the same person, place, or object) and the specific role, title, or fact in the claim.
- If Supported: restate the confirming evidence clearly.
- Refuted: evidence directly contradicts the claim. Do not treat partial overlaps (e.g., the claim mentions Karina Milei as President, but evidence says Javier Milei is President) as support. This must be Refuted.
- If Refuted: explicitly state what the correct fact is.
- Not Enough Info: no clear evidence found. Explain that the evidence is insufficient.
- Do not treat unrelated matches as valid evidence unless directly connected to the claim.
- Keep explanations short and focused ONLY on evidence relevant to the claim.
- If evidence mentions related people, family members, colleagues, or organizations, but not the subject itself holding the claimed role, classify as Refuted.
- Always check subject consistency: the same person/entity in the claim must appear in the evidence with the same role.
- Confidence must not exceed {max_confidence} if entity evidence is missing.

Evidence:
{combined_evidence}

Respond ONLY in this strict JSON format:
{{
    "verdict": "Supported | Refuted | Not Enough Info",
    "explanation": "Short explanation why",
    "follow_up": "If refuted, provide the correct information",
    "source_titles": ["List of sources used"],
    "confidence": "0-100"
}}
"""

    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    raw_output = response.choices[0].message.content.strip()

    # Step 5: JSON safe parsing
    try:
        # Extract only the JSON part (between first { and last })
        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result_data = json.loads(json_str)
        else:
            raise json.JSONDecodeError("No JSON object found", raw_output, 0)
    except json.JSONDecodeError:
        result_data = {
            "verdict": "Error",
            "explanation": f"Model did not return valid JSON. Raw output: {raw_output}",
            "follow_up": "",
            "source_titles": [],
            "confidence": "0"
        }

    return json.dumps(result_data, indent=2)
