import os
import re
import chromadb
import urllib.parse
from google import genai
from dotenv import load_dotenv


# ============================================
# Load API Keys
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", "api.env")
load_dotenv(ENV_PATH)


# ============================================
# Safe Groq Import
# ============================================

try:
    from groq import Groq
except ImportError:
    Groq = None


# ============================================
# Model Clients
# ============================================

client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "models/gemini-flash-latest"

if Groq and os.getenv("GROQ_API_KEY"):
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    GROQ_MODEL = "llama-3.1-8b-instant"
else:
    groq_client = None


# ============================================
# ChromaDB (Portable Path)
# ============================================

CHROMA_PATH = os.path.abspath(
    r"C:\Users\Pc\OneDrive\Desktop\Travel_itinerary_copy2\chroma_db"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)

blogs = client.get_collection("tokyo_travel")
transcripts = client.get_collection("tokyo_transcripts")
frames = client.get_collection("tokyo_frames")


# ============================================
# Detect Trip Days (Fixed)
# ============================================

word_to_num = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

def detect_days(user_query):
    text = user_query.lower()

    match = re.search(r"(\d+)\s*days?", text)
    if match:
        return int(match.group(1))

    for word, num in word_to_num.items():
        if f"{word} day" in text or f"{word} days" in text:
            return num

    if "weekend" in text:
        return 2
    if "week" in text:
        return 7

    return 3


# ============================================
# Improved Retrieval (Distance Filter)
# ============================================

def retrieve_multimodal(query, top_k=3):

    docs, metas = [], []

    def query_collection(collection):
        res = collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        return res["documents"][0], res["metadatas"][0], res["distances"][0]

    for collection in [blogs, transcripts, frames]:
        d, m, dist = query_collection(collection)

        for doc, meta, distance in zip(d, m, dist):
            if distance < 1.2:
                docs.append(doc)
                metas.append(meta)

    return docs, metas


# ============================================
# Budget Extraction (Hybrid Logic)
# ============================================

def calculate_evidence_budget(metas):

    total_known_cost = 0
    price_found = False

    for meta in metas:
        if isinstance(meta, dict) and "avg_price" in meta:
            try:
                total_known_cost += float(meta["avg_price"])
                price_found = True
            except:
                pass

    return total_known_cost, price_found


# ============================================
# Maps Injection
# ============================================

def maps_link(place_name):
    query = f"{place_name}, Tokyo, Japan"
    return (
        "https://www.google.com/maps/search/?api=1&query="
        + urllib.parse.quote(query)
    )

def clean_place_name(place):
    place = re.sub(r"\(.*?\)", "", place)
    # place = place.replace("’", "").replace("'", "")
    # place = place.replace(",", "")
    place = place.replace("SOURCE:", "")
    return place.strip()


def inject_maps_links(text):

    lines = text.split("\n")
    new_lines = []

    for line in lines:
        new_lines.append(line)

        if line.strip().startswith("- ") and "(SOURCE:" in line:
            place = line.split("(SOURCE:")[0]
            place = place.replace("- ", "").strip()
            place = clean_place_name(place)
            map_url = maps_link(place)

            new_lines.append(
                f'  <a href="{map_url}" target="_blank" class="map-btn">📍 Open in Google Maps</a>'
            )

    return "\n".join(new_lines)


# ============================================
# Main Trip Planner
# ============================================

def plan_trip(user_query, docs, metas):

    num_days = detect_days(user_query)

    if not docs:
        return "❌ No travel evidence found in database."

    # Memory optimization
    context_blocks = []
    for doc, meta in zip(docs, metas):
        src = meta.get("source_file", "unknown")
        context_blocks.append(f"[SOURCE: {src}]\n{doc[:8000]}")

    context = "\n\n".join(context_blocks)

    # Hybrid Budget
    known_cost, has_price_data = calculate_evidence_budget(metas)

    if has_price_data:
        budget_instruction = f"""
Budget Rule:
Known total cost from database metadata = ¥{int(known_cost)}.
Use this number. Do NOT invent new totals.
"""
        budget_source = "Database Metadata"
    else:
        budget_instruction = """
Budget Rule:
No price metadata available.
Estimate realistic Tokyo costs for food and activities only.
"""
        budget_source = "AI Estimated"

    prompt = f"""
You are a Tokyo Travel Architect AI.

ONLY use evidence below.
Do NOT repeat same areas again.

EVIDENCE:
{context}

{budget_instruction}

Create EXACTLY {num_days} days itinerary.

FORMAT:

Day 1:
Area: <area>

Food Spots:
- Place (SOURCE: file)
- Place (SOURCE: file)

Hidden Gem:
- Place (SOURCE: file)

Estimated Budget:
Food Total: ¥XXXX
Activities Total: ¥XXXX
Grand Total: ¥XXXX

Repeat until Day {num_days}.
"""

    model_used = "Gemini ⚡"

    try:
        response = client_gemini.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        raw_output = response.text.strip()
    except Exception as e:

        if groq_client is None:
            return f"❌ Model Error:\n\n{e}"

        model_used = "Groq 🚀 (Llama3 Backup)"

        chat = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a Tokyo itinerary planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        raw_output = chat.choices[0].message.content.strip()

    raw_output = (
        f"## ✅ Generated By: {model_used}\n"
        f"## 💰 Budget Source: {budget_source}\n\n"
        + raw_output
    )

    return inject_maps_links(raw_output)