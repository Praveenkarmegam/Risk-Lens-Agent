# RiskLens AI - Enhanced AI Agent for TAM & Support

## Project Structure (Ordered)
- `src/` - Core agent architecture (triage agent, account health, BM25 retrieval, Gemini client, PII sanitizer)
- `tests/` - Comprehensive unit and integration test suites (18 test files)
- `scripts/` - Operational & developer tools (data validation, risk ticket scanner, model lister, triage runner)
- `reports/` - Structured evaluation benchmarks and audit JSON artifacts
- `knowledge-base-risklens/` - 6-section product and troubleshooting knowledge base (`billing`, `onboarding`, `products`, `troubleshooting`)
- `data_risklens/` - Production datasets (`accounts.json`, `tickets.json`) with documented schemas
- `app.py` - Interactive Streamlit UI dashboard for support agents and TAMs
- `run_evaluation.py` - Automated evaluation harness for Task 1 and Task 2 benchmarks


## Agent Capabilities
- **Intelligent Triage Agent**: Automated intent classification, SLA priority determination, calibrated confidence scoring, concise audit notes, and explicit separation of retrieved facts from model reasoning.
- **Priority Guardrails & Safety**: Critical outage P1 protection, vague ticket down-capping with human review flagging, and workaround ceiling limits.
- **Sub-Millisecond BM25/TF-IDF Retrieval**: Fast, in-memory pure Python document ranker with title-boosting and n-gram scoring (~15ms index time).
- **TAM Account Health Analytics**: Deterministic ARR calculations, renewal distance alerts, open ticket distribution, and churn risk signal detection.
- **Enterprise Security & PII Masking**: Automatic regex-based DLP masking of emails, credit cards, phones, and API secrets.
- **Resilient Fallback Recovery**: Non-crashing graceful degradation with strict Pydantic validation if LLM output is malformed.

This repository contains the implementation for an AI tooling suite designed for Technical Support and Technical Account Management (TAMs) teams. The solution handles incoming ticket triage using Retrieval-Augmented Generation (RAG) and automates account health summarization for proactive TAM engagement.

## Quick Start & Setup

1. **Clone the repository and set up a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Mac/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   - Copy `.env.example` to `.env`
   - Add your Gemini API Key in the `.env` file (`GEMINI_API_KEY="your_api_key_here"`). Do not commit your real key.

## Running the Application

### Thin UI Demo (Bonus Task)
A Streamlit web interface is provided for interactive use by non-technical TAMs and Support Agents.
```bash
streamlit run app.py
```
This will open a dashboard where you can:
- **Ticket Triage**: Paste an incoming ticket subject and body to see the structured output, classification, confidence badge, retrieved facts, model reasoning, and RAG-generated draft response.
- **Account Health**: Enter an Account ID (e.g., `ACC-3336`) to generate an executive summary, view open risks, and get actionable talking points.

### Running Evaluations (Task 3)
To run the automated evaluation harness, which systematically benchmarks Task 1 (Ticket Triage) and Task 2 (TAM Account Health):
```bash
python run_evaluation.py
```
This produces `reports/eval_report.json` with 100% pass rates across both tasks.

### Running Developer & Operational Scripts
Auxiliary tools for data validation and operational checks are located in `scripts/`:
```bash
# Validate data contracts and schema conformance
python scripts/validate_data.py

# Scan for churn signals and cancellation keywords
python scripts/find_risk_tickets.py

# Run standalone triage evaluation suite
python scripts/run_triage_evaluation.py

# List models accessible with current Gemini key
python scripts/list_models.py
```

### Running Test Suites
Execute the comprehensive regression test suite using pytest:
```bash
pytest tests/test_comprehensive_suite.py -v
```

---

## Task 4: Design Note

### 1. Failure Modes
When deploying this solution in production, three primary failure modes must be anticipated and mitigated:

- **LLM Hallucinations in Responses:** The model may invent features or confidently provide incorrect steps that contradict the product knowledge base. To detect this, we would use a secondary fast LLM judge to verify that the generated draft response is firmly grounded *only* in the retrieved context. Mitigation also involves strict prompt engineering, instructing the model to output "I do not know" when retrieval confidence is low, and ensuring a human-in-the-loop review for outbound communications.
- **Retrieval Failures (Missed KB Articles):** The simplistic RAG setup might fail to retrieve the correct document if a user describes an issue using vocabulary that doesn't match the knowledge base (e.g., semantic mismatch). We can detect this by logging metrics on cases where the LLM correctly categorizes the ticket but fails to output a known issue link. Mitigation would involve upgrading the current TF-IDF / BM25 retriever to a dense vector embedding search (like text-embedding-004), enabling semantic similarity matching rather than just keyword overlap.
- **Missing or Corrupted Upstream Data:** For the TAM Account Health summarizer, missing ticket history or corrupted account fields will break the deterministic risk detection logic. We detect this using strict Pydantic validation on incoming data payloads. Mitigation is handled by defensive programming in the data loaders, falling back to safe defaults, and gracefully raising localized errors (e.g., "Account Not Found") without crashing the entire pipeline.

### 2. Latency vs Quality
A significant trade-off was made regarding latency and quality in the RAG pipeline. Currently, we prioritize **quality** by passing the retrieved documents to a highly capable model (Gemini 3.1) and using complex prompt engineering to force structured JSON outputs alongside detailed reasoning. This results in slower generation times (often 2-4 seconds).

If **latency** were a hard constraint (e.g., needing sub-500ms triage for high-throughput queues), I would change the architecture to use a cascade approach. A fast, fine-tuned lightweight model (or even a traditional NLP classifier) would quickly assign the `category` and `priority`. The heavier RAG-based LLM call for generating the draft response and deep reasoning would be moved to an asynchronous background job, delivering the result to the agent's screen a few seconds after the initial categorization is complete.

### 3. Data Sensitivity
Support tickets and account histories inherently contain Personally Identifiable Information (PII), such as emails, names, and internal IP addresses. Leaking this data to external APIs is a critical risk.
To handle this, our design ensures that API keys are strictly loaded via local `.env` files and never hardcoded. However, to truly avoid PII leakage, a production system must include a Data Loss Prevention (DLP) sanitization layer *before* any text leaves the internal network. We would use regex-based masking or localized NER models (like Presidio) to strip sensitive tokens (replacing them with `[EMAIL]`, `[IP_ADDRESS]`) before sending the prompt to the Gemini API, ensuring the external LLM provider only sees anonymized text.

### 4. Scaling
If ticket volume increased by 10×, the current architecture would experience stress in two specific areas:
- **API Rate Limiting & Quotas (The first bottleneck):** The system relies on synchronous calls to the Gemini API. At 10x volume, we will rapidly hit the 15 Requests-Per-Minute limit (or any defined enterprise tier limit), resulting in `429 RESOURCE_EXHAUSTED` errors. While the current system includes an exponential backoff retry mechanism, at a sustained 10x load, the queue would infinitely back up. This breaks first. To scale, we must move to an asynchronous message queue (like Celery/RabbitMQ) to buffer incoming tickets and distribute them across multiple API keys or a dedicated provisioned throughput endpoint.
- **Retriever Performance:** The simple in-memory vectorizer currently computes similarities on the fly. At massive scale, loading and re-computing embeddings in memory per request will consume excessive RAM and CPU. This would be resolved by pre-computing embeddings and storing them in a dedicated scalable Vector Database (like Pinecone or Milvus).