import pickle
import numpy as np
import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from groq import Groq

MAX_LENGTH = 100
sentiment_decoder = {0: "Negative", 1: "Neutral", 2: "Positive"}

try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Groq API Key missing. Error: {e}")
    st.stop()

@st.cache_resource
def load_ai_assets():
    model = load_model("youtube_production_model.keras")
    with open('final_production_tokenizer.pkl', 'rb') as handle:
        tokenizer = pickle.load(handle)
        return model, tokenizer

try:
    prod_model, prod_tokenizer = load_ai_assets()
except Exception as e:
    st.error(f"Failed to load AI assets.Error: {e}")
    st.stop()

def analyze_comment(text):
    seq = prod_tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding='post', truncating='post')
    predictions = prod_model.predict(padded, verbose=0)

    raw_sentiment_int = int(np.argmax(predictions[0][0]))
    is_sarcastic = bool(predictions[1][0][0] > 0.60)

    final_sentiment_int = 0 if is_sarcastic else raw_sentiment_int

    return {
        "is_sarcastic": is_sarcastic,
        "final_sentiment": sentiment_decoder[final_sentiment_int]
    }

def generate_llm_summary(pos_list, neg_list, neu_list):
    p_text = [c['text'] for c in pos_list[:10]]
    n_text = [c['text'] for c in neg_list[:10]]
    u_text = [c['text'] for c in neu_list[:10]]

    prompt = f"""
You are a senior audience research analyst. Your task is to synthesize raw YouTube comment data into a precise, specific executive summary of viewer sentiment.

COMMENT DATA (Pre-labeled by a sentiment classifier — treat labels as unreliable hints, not ground truth):
- SET A (Tentatively Positive): {p_text}
- SET B (Tentatively Negative/Sarcastic): {n_text}
- SET C (Tentatively Neutral): {u_text}

ANALYSIS PROTOCOL:
1. RECLASSIFY first. Re-read each comment independently. Override any label that doesn't match the comment's actual meaning or intent.
2. EXTRACT specifics. Anchor every claim to concrete details — name the exact feature, timestamp, creator decision, or phrase that viewers repeatedly react to. Never use vague descriptors like "the content" or "the video."
3. DETECT disguised sentiment. Flag irony or sarcasm where apparent praise masks criticism. Note the specific rhetorical pattern (e.g., mock-congratulatory, deadpan exaggeration).
4. IDENTIFY consensus vs. outliers. Distinguish views shared across multiple commenters from isolated opinions. Do not treat a single comment as a trend.
5. DETECT direct video verdicts. Identify comments where viewers explicitly judge the video overall — e.g., "waste of time," "best video on this topic," "didn't finish it." Distinguish these holistic verdicts from feedback on specific moments.
6. SYNTHESIZE into 3–4 sentences. Each sentence must carry a distinct, non-overlapping insight.

OUTPUT RULES:
- Professional and neutral tone throughout.
- Be specific: name themes, not categories. ("Viewers objected to the 10-minute ad read at the midpoint" not "Viewers disliked the monetization.")
- No meta-commentary. Do not reference the comments, the data, or this analysis process.
- No filler openers. Begin directly with the insight.
- Do not include any title, heading, or label before the summary. Start directly with the first sentence.
"""
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.2,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Warning: Could not generate LLM summary. {e}"