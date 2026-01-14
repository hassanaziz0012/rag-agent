from lib.keyword_search import preprocess_text, Chunk, search

book_file = "data/book.md"

with open(book_file, "r") as file:
    book = file.read()

paragraphs = book.split("\n\n")

preprocessed_paragraphs = [
    Chunk(i, p, preprocess_text(p)) for i, p in enumerate(paragraphs)
]

print(search(preprocessed_paragraphs, "entrepreneurship")[:5])
