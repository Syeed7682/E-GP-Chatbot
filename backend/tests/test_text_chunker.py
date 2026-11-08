from app.services.text_chunker import split_text_with_overlap


def test_overlap_chunks_start_at_word_boundaries():
    words = ["committee", "evaluation", "technical", "member"] * 30
    text = " ".join(words)

    chunks = split_text_with_overlap(text, chunk_size=75, chunk_overlap=25)

    assert len(chunks) > 1
    assert all(chunk.split()[0] in words for chunk in chunks)
