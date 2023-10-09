---
title: ArxivChainLitDemo
emoji: 💻
colorFrom: indigo
colorTo: gray
sdk: docker
pinned: false
license: openrail
---

# Question & Answering on Arxiv papers

This folder is showing how to:

- Ask a user for a PDF file
- Chunk that file and create embeddings 
- Store those embeddings on Chroma
- Answer questions from users as well as showing the sources used to answer.
- How to deploy on HuggingFace Spaces

Video from [Chris Alexiuk](https://twitter.com/c_s_ale): https://www.youtube.com/watch?v=9SBUStfCtmk&ab_channel=ChrisAlexiuk

Note: the code is updated to work with the new async implementation

Title: Arxiv Q&A
Tags: [arxiv, qa, embeddings, chroma, huggingface_spaces]