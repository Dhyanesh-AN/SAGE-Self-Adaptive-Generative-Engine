# SAGE (Self-Adaptive Generative Engine)

A production-grade self-correcting Retrieval-Augmented Generation (RAG) system that evaluates its own retrieval quality, rewrites queries when necessary, and retries retrieval before generating answers.

## 🚀 Features

- PDF ingestion pipeline
- Recursive text chunking
- Hybrid Retrieval (Upcoming)
- LangGraph agent workflow (Upcoming)
- Reflection-based query rewriting (Upcoming)
- RAGAS & DeepEval benchmarking (Upcoming)

## 🏗️ Tech Stack

- FastAPI
- LangGraph
- LangChain
- Qdrant
- PostgreSQL
- Ollama
- BGE Embeddings
- Docker
- Next.js

## 📂 Project Structure

backend/
frontend/
infrastructure/

## Development Progress

- [x] FastAPI Backend
- [x] PDF Upload
- [x] Text Extraction
- [x] Cleaning Pipeline
- [x] Recursive Chunking
- [ ] Embeddings
- [ ] Qdrant
- [ ] Basic RAG
- [ ] Hybrid Retrieval
- [ ] Reflection Agent
- [ ] Evaluation

## Project Goal

Build a production-ready Agentic RAG system while understanding every architectural decision from first principles.