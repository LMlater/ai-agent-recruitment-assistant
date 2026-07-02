# Policy RAG Design

## Scope

Round 3 adds a local, testable policy retrieval baseline for `PolicyAgent`. It does not call a real LLM, DashScope/Bailian, external embedding service, Chroma, FAISS, or any bank-internal system.

本项目制度文档是模拟制度，只用于学习和工程演示，不代表真实银行内部制度。

LLM 后续只能基于检索到的制度依据组织报告，不能编造条款，不能自动审批。

## Architecture

`PolicyDocumentLoader` scans `agent-service/knowledge_base/*.md`, splits markdown by `##` policy sections, extracts clause codes such as `P-001`, `M-001`, `R-001`, and `C-001`, and returns stable `PolicyChunk` objects.

`PolicyRetrievalService` builds an in-process TF-IDF index with `TfidfVectorizer` char n-grams and ranks chunks by cosine similarity. This keeps the current round deterministic, offline, and easy to test. A future vector store can replace this service behind the same `search(query, top_k)` interface.

## Document Format

Each policy document is a mock markdown file with second-level headings:

```markdown
## R-001 Debt-to-Income Ratio Control

Debt-to-income ratio is a key repayment-capacity indicator...
```

The loader stores:

- `chunk_id`: stable `document.md::POLICY-CODE` or slug fallback.
- `document_name`: source markdown file name.
- `section_title`: heading text.
- `text`: heading plus section body.
- `policy_code`: extracted clause code or `null`.

## Retrieval Flow

1. `PolicyAgent` reads the review state: request, risk level, risk score, required materials, compliance warnings, rule reasons, debt-to-income ratio, and ML model signal.
2. It builds a retrieval query that includes purpose, amount, risk indicators, missing materials, overdue/DTI/manual-review wording, and AI/ML guardrails.
3. `PolicyRetrievalService.search()` returns `PolicyReference` objects with `policy_code`, `document_name`, `section_title`, `content`, and `score`.
4. `ReviewReport.policy_references` serializes these references as JSON. The Java backend can continue storing the report JSON string without schema changes.

## Evaluation

The RAG eval set is `data/eval/rag_questions.jsonl`. It includes 12 mock questions covering age eligibility, income proof, work years, amount-to-income pressure, DTI, overdue records, asset proof, missing materials, medium/high-risk manual review, AI non-auto-approval, ML auxiliary signal, audit trace, and privacy boundaries.

Run:

```bash
cd agent-service
python scripts/evaluate_policy_retrieval.py
```

The script writes `data/eval/rag_eval_results.json` with `recall_at_3`, `recall_at_5`, `hit_rate`, and `mrr`. Metrics are computed from current retrieval results and expected clause codes; they are not hand-filled.

## Guardrails

- No real bank policy documents.
- No real customer data, identity card numbers, phone numbers, or secrets.
- No automatic approval path.
- No external model, embedding, or vector database dependency in this round.
- RAG references are evidence for reviewer-facing reports, not final decisions.
