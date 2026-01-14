def build_answer_prompt(query, results):
    """Build the prompt for the LLM."""
    return f"""
You are an LLM tasked with answering questions on the book "Purpose and Profit" by Dan Koe.

This is how the author described the book:
```
Transform Your Relationship With Money & Discover Your Life's Work
Money controls most people's lives, but it doesn't have to. Money is only superficial to the superficial. There is, in fact, a way to merge purpose and profit to create a life filled with work you don't want to escape from.
```

I'll give you the search query and the top 5 paragraphs from the book that are most relevant to the user's search query. Your job is to use those 5 paragraphs to answer the user's question as best as you can.

- Do not deviate from the given paragraphs.
- If you don't have an answer, say "I don't know".
- Keep your answer concise and information-dense.

Here is the user's search query:
{query}

Here are the top 5 paragraphs from the book that are most relevant to the user's search query:
{results}
"""


def build_query_prompt(query):
    """Build the prompt for the LLM."""
    return f"""
Your task is to take the user's search query, and then rewrite it to be more specific and focused. 
These search queries will run on the book "Purpose and Profit" by Dan Koe. It is a business mindset, self-help book.

Here is the user's search query:
{query}

1. If the query is not a genuine question related to this book, stop further processing and return "INVALID_QUERY".
2. If the query is a genuine question related to this book, rewrite it to be more specific and focused.

Note that this search query will be used to semantic-search across the entire book and retrieve relevant paragraphs. 

In your output, ONLY RETURN the rewritten query. Do not include any additional text.
"""
