# AI-Tokyo-Travel-Architect

Multimodal RAG-Based Intelligent Itinerary Generator

An AI-powered travel planning system that generates structured, evidence-grounded Tokyo itineraries using Retrieval-Augmented Generation (RAG) with Gemini + Groq fallback, powered by ChromaDB vector search and enriched with Google Maps integration.

Project Overview :

This project builds a production-style AI travel planner that:

Retrieves relevant travel knowledge from blogs, YouTube transcripts, and video frames

Uses semantic search via vector embeddings

Applies hybrid budget reasoning

Generates strictly structured itineraries

Injects clickable Google Maps links

Uses Gemini with automatic Groq fallback

It is designed to minimize hallucination and enforce evidence-grounded generation.

System Architecture :

User Query
    ↓
Detect Trip Duration
    ↓
Multimodal Retrieval (ChromaDB)
    ↓
Distance Filtering
    ↓
Hybrid Budget Logic
    ↓
Prompt Engineering (Strict Grounding)
    ↓
Gemini API (Primary)
    ↓
Groq Llama 3 (Fallback)
    ↓
Google Maps Link Injection
    ↓
Final Structured Itinerary


Technologies Used :

1️ Python

Core backend language.

2️ ChromaDB

Vector database for semantic retrieval.

3️ Google Gemini API

Primary LLM for itinerary generation.

4️ Groq (Llama 3.1 8B Instant)

Fallback LLM for reliability.

5️ dotenv

Secure API key management.

6️ urllib.parse

Google Maps URL encoding.

 Key Features
 Multimodal Retrieval

The system retrieves data from:

tokyo_travel (Blogs)

tokyo_transcripts (YouTube transcripts)

tokyo_frames (Video metadata)

This improves contextual depth and reduces hallucination.

Distance-Based Filtering :

Only results with embedding distance < threshold are used.

This ensures:

High relevance

Strong grounding

Reduced irrelevant generation

Hybrid Budget Logic :

Budget is calculated using:

Metadata (avg_price) if available

AI estimation if not available

This combines symbolic data + generative reasoning.

Intelligent Day Detection

Automatically detects:

“5 days”

“five days”

“weekend”

“1 week”

Defaults to 3 days if unspecified.

Google Maps Injection

Each location is converted into:

https://www.google.com/maps/search/{Place}

Clickable buttons are automatically injected into the output.

Hallucination Control

Prompt enforces:

Use ONLY retrieved evidence

No repetition of same areas

Exact number of requested days

Structured format

 LLM Failover Design

Primary:

Gemini Flash

Fallback:

Groq Llama 3

If Gemini fails (timeout, quota, API issue), system switches automatically.

 How It Works (Step-by-Step)
1️ User Input

Example:

Plan a 5-day spiritual and food trip to Tokyo
2️ Detect Days

Regex extracts number of days.

3️ Retrieve Evidence

ChromaDB returns relevant documents.

4️ Filter by Similarity Distance

Irrelevant chunks are removed.

5️ Budget Evaluation

Metadata-based calculation applied.

6️ Strict Prompt Construction

System builds a grounded instruction block.

7️ LLM Generation

Gemini generates itinerary.

8️ Google Maps Link Injection

Place names converted to clickable map buttons.

9️ Final Output Returned

Example Output Format :


DAY 1: Asakusa & Ueno

Morning:
- Senso-ji Temple [Map Button]

Afternoon:
- Ueno Park
- Tokyo National Museum

Evening:
- Ameyoko Street food tour

Estimated Budget:
¥8,000 - ¥12,000

Alexander Roy

AI Engineer | RAG Systems | Intelligent Travel Systems
