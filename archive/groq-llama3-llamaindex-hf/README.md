# RAG Chatbot using Llamaindex, Groq Llama3 & Chainlit, deployed on Huggingface Space

## RAG pipeline creation:

- Framework -> [Llamaindex](https://docs.llamaindex.ai/en/stable/index.html) 
- Loader -> [SimpleDirectoryLoader](https://docs.llamaindex.ai/en/stable/module_guides/loading/simpledirectoryreader.html)
- Chunking -> [Sentence Splitter](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/modules/#sentencesplitter)
- Embeddings -> [HF Sentence Transformer Embeddings](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- Vector DB -> [Llamaindex VectorStoreIndex](https://docs.llamaindex.ai/en/stable/module_guides/indexing/vector_store_index.html)
- LLM -> [Groq Llama3](https://docs.llamaindex.ai/en/stable/examples/llm/groq.html#groq)

## Chatbot 
- [Chainlit with Llamaindex](https://docs.chainlit.io/integrations/llama-index)

## To run application locally
```
pip install requirements.txt
chainlit run app.py 
```

## Deployment to HF Spaces 
- [Check Dockerfile](./Dockerfile)

## Blog/Article
- [Follow Medium Link](https://itsjb13.medium.com/building-a-rag-chatbot-using-llamaindex-groq-with-llama3-chainlit-b1709f770f55)