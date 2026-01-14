import re
import math
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import Counter
from typing import NamedTuple


class Chunk(NamedTuple):
    paragraph_id: int
    text: str
    tokens: set[str]


class ChunkTF(NamedTuple):
    paragraph_id: int
    tf: Counter


class ChunkIDF(NamedTuple):
    paragraph_id: int
    idf: float


def preprocess_text(text: str) -> set[str]:
    # Lowercase and remove punctuation
    text = re.sub(r"[^\w\s]", "", text.lower())

    # Tokenize, remove stop words, and stem
    stop_words = set(stopwords.words("english"))
    stemmer = PorterStemmer()

    return set(stemmer.stem(word) for word in text.split() if word not in stop_words)


def search(chunks: list[Chunk], query: str):
    query_tokens = set(preprocess_text(query))

    # 1. Calculate global IDF for query tokens
    n_chunks = len(chunks)
    token_idfs = {
        token: math.log(
            (n_chunks + 1) / (sum(1 for c in chunks if token in c.tokens) + 1)
        )
        for token in query_tokens
    }

    results = []

    # 2. Score each chunk
    for chunk in chunks:
        # TF: count of token in this specific chunk
        chunk_counts = Counter(chunk.tokens)
        score = sum(chunk_counts[token] * token_idfs[token] for token in query_tokens)

        if score > 0:
            results.append(
                {"id": chunk.paragraph_id, "score": score, "text": chunk.text}
            )

    # 3. Sort by relevance
    return sorted(results, key=lambda x: x["score"], reverse=True)
