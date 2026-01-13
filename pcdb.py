import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

book_file = "book.md"

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "rag-agent"
index = pc.Index(index_name)
namespace = "purpose-and-profit"

query = "Top business models"

def insert_all_records():
    with open(book_file, "r") as file:
        book = file.read()
    paragraphs = book.split("\n\n")

    records = [
        {
            "id": str(i),
            "text": p,
            "book_title": "Purpose and Profit"
        } for i, p in enumerate(paragraphs)
    ]

    batch_size = 96
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        index.upsert_records(namespace="purpose-and-profit", records=batch)
        print(f"Upserted batch {i//batch_size + 1}: {len(batch)} records")

results = index.search(namespace=namespace, query={
    "top_k": 10,
    "inputs": {
        "text": query
    }},
    rerank={
        "model": "bge-reranker-v2-m3",
        "top_n": 10,
        "rank_fields": ["text"]
    } 
)

for r in results["result"]["hits"]:
    print(f"id: {r['_id']:<5} | score: {round(r['_score'], 2):<5} | book_title: {r['fields']['book_title']:<10} | text: {r['fields']['text']:<50}\n")