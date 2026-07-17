# Verdict AI — AI Evaluation, Monitoring & Observability Platform

An intelligent, high-performance monitoring platform designed to measure AI quality, catch hallucinations, track costs, and evaluate prompt experiments at scale.

Built to solve the observability gap in production AI by capturing every request, evaluating responses dynamically using an LLM-as-a-judge, and powering high-speed analytics dashboards.

## 🎥 Video Demonstration

Watch the complete video walkthrough of the Verdict AI platform:
[**Verdict AI Demo Video**](https://drive.google.com/file/d/1kWbVu2sFSUQF-1HUXienPTMoFKx46Iso/view?usp=sharing)

This comprehensive demonstration covers:
- **Documentation Summary:** A high-level overview of the project's purpose, problem statement, and the unique selling proposition (USP) of building an LLM-as-a-judge observability platform.
- **Codebase Deep Dive:** An architectural walkthrough explaining how the non-blocking SDK tracker, FastAPI ingestion layer, Kafka event pipeline, and ClickHouse analytics engine seamlessly work together.
- **Stress Testing the Final Product:** Live execution of the demo app, pushing various prompts to the pipeline, and watching the dashboard update in real-time as the 70B Judge catches hallucinations and scores responses.

## 🎯 Project Goal
The primary objective of this project is to build an instrument panel for AI systems capable of answering critical observability questions:
- **Quality Trends:** Is the AI's response quality improving or degrading?
- **Hallucination Detection:** Are responses faithful to source documents, or making up facts?
- **Prompt Experimentation:** Which prompt version (A/B testing) performs better in quality, latency, and cost?
- **Regression Testing:** Did a recent prompt change silently break existing use cases?

The system must capture traces without adding latency to the user's AI application, process thousands of events securely, and present real-time insights through observability dashboards.

## 🏗️ System Architecture & High-Level Design
Verdict relies on a high-throughput event pipeline and microservices architecture. Instead of blocking the user's application, it processes everything asynchronously:

- **SDK Tracker:** A lightweight Python decorator that captures prompts, responses, latencies, and tokens entirely in the background.
- **FastAPI Collector:** A high-speed ingestion API that receives traces and immediately drops them onto an event buffer.
- **Kafka Event Pipeline:** A resilient streaming buffer that absorbs traffic spikes, decoupling ingestion from heavy processing and guaranteeing zero data loss.
- **Evaluation Consumer:** A background worker that reads from Kafka, invokes the Groq LLM-as-a-judge to score Faithfulness, Relevance, and Hallucination, and calculates exact token costs.
- **ClickHouse Analytics Storage:** A columnar database designed for lightning-fast aggregations (e.g., P99 latencies) over millions of traces.
- **Postgres Metadata Storage:** A relational database for managing projects, users, and prompt versions.

### Bonus Features Implemented
- **✅ Asynchronous Tracing:** The SDK uses fire-and-forget requests to ensure monitoring adds zero latency to your AI apps.
- **✅ Automated Regression Suite:** Automatically run a benchmark set of known queries against a new prompt version to catch degradations before they hit production.
- **✅ Environment Variables Integration:** Secure API key management using `python-dotenv`.

## 💻 Tech Stack
**Backend (Ingestion & Evaluation)**
- **Framework:** Python, FastAPI
- **LLMs (Judge):** Groq (llama3-70b-8192 for strict, objective grading)
- **Message Broker:** Confluent Kafka & Zookeeper
- **Analytics DB:** ClickHouse
- **Metadata DB:** PostgreSQL, SQLAlchemy

**Observability & Dashboards**
- **Platform:** Grafana
- **Integration:** ClickHouse Grafana Datasource

## 📂 Codebase & Folder Structure
The repository is highly organized for event-driven processing and scalability.

```text
verdict/
├── collector/                # Ingestion API Layer
│   └── main.py               # FastAPI entry point for traces
├── pipeline/                 # Event Streaming Layer
│   ├── producer.py           # Publishes traces to Kafka
│   └── consumer.py           # Reads from Kafka, evaluates, saves to ClickHouse
├── storage/                  # Database Layer
│   ├── clickhouse.py         # Schema and client for trace analytics
│   └── models.py             # SQLAlchemy models for Postgres
├── eval/                     # AI Grading Engine
│   ├── judge.py              # Groq LLM-as-a-judge implementation
│   └── metrics.py            # Latency and cost aggregations
├── sdk/                      # Developer Toolkit
│   └── tracker.py            # Non-blocking @track_llm decorators
├── experiments/              # Testing Frameworks
│   ├── ab.py                 # Prompt A/B comparison logic
│   └── regression.py         # Benchmark suite for prompt changes
├── dashboards/               # Observability configs
│   └── provisioning/         # Default Grafana datasources and providers
├── docker-compose.yml        # Orchestrates Kafka, ClickHouse, Postgres, Grafana
├── mock_ai_app.py            # Demo AI app instrumented with the SDK
├── .env.example              # Environment variables template
└── requirements.txt          # Python dependencies
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Docker Desktop
- Python 3.9+
- Groq API Key

### 2. Infrastructure Setup
Start the underlying services (Kafka, Zookeeper, ClickHouse, Postgres, Grafana) using Docker:
```powershell
docker compose up -d
```

### 3. Backend & Environment Setup
Create and activate a virtual environment:
```powershell
# Windows
python -m venv venv
.\venv\Scripts\activate
```
Install dependencies:
```powershell
pip install -r requirements.txt
```
Configure Environment Variables: Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_key_here
```

### 4. Initialize Data Pipelines
Set up the ClickHouse analytics tables:
```powershell
python -m storage.clickhouse
```

Start the Kafka Consumer (this will evaluate traces and save them):
```powershell
python -m pipeline.consumer
```

### 5. Start the API Collector
Open a new terminal, activate the environment, and start the FastAPI ingestion server:
```powershell
uvicorn collector.main:app --host 0.0.0.0 --port 8000
```

### 6. Run the Demo AI App
In another terminal, run the mock AI application to generate traces:
```powershell
python mock_ai_app.py
```

### 7. View Observability Dashboards
Open your browser and navigate to `http://localhost:3000` (Login: `admin` / `admin`). Connect the ClickHouse datasource to visualize latency, cost, and hallucination metrics!

---
© Copyright 2026. Made with love by Shivang Sharma.
