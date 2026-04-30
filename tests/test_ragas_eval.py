# tests/test_ragas_eval.py
# ── Sprint 6: RAGAS Evaluation Harness ──
#
# Run on-demand only (requires live NIM cloud API calls):
#   python -m pytest tests/test_ragas_eval.py -m ragas -v -s
#
# Excluded from the normal fast test suite:
#   python -m pytest tests/ -m "not ragas"
#
# Notes:
#   - Uses the NIM cloud endpoint (NVIDIA_API_KEY in .env) as the LLM judge.
#   - Scores RAGAS metrics per-sample to avoid datasets/dill Python 3.14 incompatibility.
#   - NL2SQL test uses cloud LLM directly (nl2sql.py uses ChatNVIDIA which needs on-prem).

import os
import json
import pytest
import sys

# Force cloud mode before any app modules are imported so nodes.py / nl2sql.py
# pick up the cloud base URL instead of the on-prem SSH tunnel.
os.environ["NIM_MODE"] = "cloud"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Mark every test in this module as "ragas" so they are opt-in.
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.ragas


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def eval_data():
    dataset_path = os.path.join(os.path.dirname(__file__), "eval_dataset.json")
    with open(dataset_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def nim_llm():
    """LangChain-compatible LLM wired to the NIM cloud endpoint."""
    from langchain_openai import ChatOpenAI
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY", os.getenv("NIM_API_KEY", ""))
    base_url = os.getenv("NIM_BASE_URL_CLOUD", "https://integrate.api.nvidia.com/v1")
    model = "meta/llama-3.1-70b-instruct"

    return ChatOpenAI(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=0,
    )


@pytest.fixture(scope="module")
def nim_embeddings():
    """Embeddings model for RAGAS (reuse the same HuggingFace model as the app)."""
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


# ---------------------------------------------------------------------------
# Helper: retrieve RAG context and generate a grounded answer via cloud LLM
# ---------------------------------------------------------------------------
def _rag_answer(question: str, llm) -> tuple[str, list[str]]:
    """
    1. Retrieve up to 8 relevant chunks from campus_rag_tool.
    2. Ask the cloud LLM to produce a grounded answer using those chunks.
    Returns (answer_string, [context_chunk_1, context_chunk_2, ...]).
    """
    from src.tools import campus_rag_tool
    from langchain_core.messages import SystemMessage, HumanMessage

    raw_context: str = campus_rag_tool.invoke(question)
    contexts = [c.strip() for c in raw_context.split("\n---\n") if c.strip()]

    prompt = (
        "You are a campus assistant. Answer the question using ONLY the context below. "
        "Quote exact figures (phone numbers, fees, times) verbatim.\n\n"
        f"Context:\n{raw_context}\n\n"
        f"Question: {question}"
    )
    response = llm.invoke([
        SystemMessage(content="Answer only from the provided context."),
        HumanMessage(content=prompt),
    ])
    answer = response.content.strip()
    return answer, contexts


# ---------------------------------------------------------------------------
# Phase 1A — RAG pipeline: RAGAS metrics (per-sample scoring)
# Avoids Dataset.from_list() which is incompatible with Python 3.14 / dill.
# ---------------------------------------------------------------------------
def test_rag_ragas_metrics(eval_data, nim_llm, nim_embeddings):
    """
    Measures faithfulness, answer_relevancy, and context_recall for the
    campus_rag_tool pipeline using the NIM cloud endpoint as the LLM judge.

    Scores each sample individually (no datasets.Dataset wrapper) to work
    around the dill / Python 3.14 serialisation bug.

    Thresholds (mean across all samples):
        faithfulness     >= 0.70
        answer_relevancy >= 0.75
        context_recall   >= 0.70
    """
    from ragas.metrics import faithfulness, answer_relevancy, context_recall
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.dataset_schema import SingleTurnSample
    import asyncio

    ragas_llm = LangchainLLMWrapper(nim_llm)
    ragas_emb = LangchainEmbeddingsWrapper(nim_embeddings)

    # Wire the judge LLM/embeddings into each metric
    faithfulness.llm = ragas_llm
    answer_relevancy.llm = ragas_llm
    answer_relevancy.embeddings = ragas_emb
    context_recall.llm = ragas_llm

    scores = {"faithfulness": [], "answer_relevancy": [], "context_recall": []}

    for item in eval_data["rag"]:
        question = item["question"]
        ground_truth = item["ground_truth"]

        answer, contexts = _rag_answer(question, nim_llm)

        print(f"\n  [RAG] Q: {question[:70]}")
        print(f"        A: {answer[:100]}")
        print(f"        Contexts: {len(contexts)} chunks retrieved")

        sample = SingleTurnSample(
            user_input=question,
            response=answer,
            retrieved_contexts=contexts,
            reference=ground_truth,
        )

        # Score synchronously via asyncio
        loop = asyncio.new_event_loop()
        try:
            f_score = loop.run_until_complete(faithfulness.single_turn_ascore(sample))
            ar_score = loop.run_until_complete(answer_relevancy.single_turn_ascore(sample))
            cr_score = loop.run_until_complete(context_recall.single_turn_ascore(sample))
        finally:
            loop.close()

        scores["faithfulness"].append(f_score)
        scores["answer_relevancy"].append(ar_score)
        scores["context_recall"].append(cr_score)

        print(f"        faithfulness={f_score:.3f}  "
              f"answer_relevancy={ar_score:.3f}  "
              f"context_recall={cr_score:.3f}")

    mean_f  = sum(scores["faithfulness"]) / len(scores["faithfulness"])
    mean_ar = sum(scores["answer_relevancy"]) / len(scores["answer_relevancy"])
    mean_cr = sum(scores["context_recall"]) / len(scores["context_recall"])

    print("\nRAGAS Results (mean across all samples):")
    print(f"   faithfulness     = {mean_f:.3f}  (threshold >= 0.70)")
    print(f"   answer_relevancy = {mean_ar:.3f}  (threshold >= 0.75)")
    print(f"   context_recall   = {mean_cr:.3f}  (threshold >= 0.70)")

    assert mean_f >= 0.70, f"RAG faithfulness too low: {mean_f:.3f} < 0.70"
    assert mean_ar >= 0.75, f"RAG answer_relevancy too low: {mean_ar:.3f} < 0.75"
    assert mean_cr >= 0.70, f"RAG context_recall too low: {mean_cr:.3f} < 0.70"


# ---------------------------------------------------------------------------
# Phase 1B — NL2SQL pipeline: custom accuracy metrics (no LLM judge needed)
# Uses the cloud LLM directly; nl2sql.py's ChatNVIDIA requires on-prem tunnel.
# ---------------------------------------------------------------------------
def test_nl2sql_accuracy(eval_data, nim_llm):
    """
    Measures SQL execution success rate and result-column accuracy for the
    NL2SQL pipeline. Uses the cloud LLM to generate SQL; executes against
    the real SQLite DB.

    Thresholds:
        SQL execution success rate  >= 80%   (4/5)
        Expected column hit rate    >= 80%   (4/5)
    """
    from langchain_core.messages import SystemMessage, HumanMessage
    from src.nl2sql import DB_SCHEMA, execute_sql

    SQL_SYSTEM_PROMPT = f"""You are an expert SQL generator for a campus IoT database.
Given a natural language question, generate a valid SQLite SQL query.

Database Schema:
{DB_SCHEMA}

Rules:
- Only generate SELECT statements
- Use DATE(timestamp) for date comparisons
- Always LIMIT results to 10 unless asked for more
- Return ONLY the SQL query, nothing else
- Do not include markdown or backticks
- For comfort queries use: temperature_c < 24 for cool, noise_db < 50 for quiet
"""

    total = len(eval_data["nl2sql"])
    success_count = 0
    column_hit_count = 0

    for item in eval_data["nl2sql"]:
        question = item["question"]
        expected_cols = [c.lower() for c in item["expected_columns"]]

        # Generate SQL via cloud LLM
        response = nim_llm.invoke([
            SystemMessage(content=SQL_SYSTEM_PROMPT),
            HumanMessage(content=question),
        ])
        sql = response.content.strip()

        print(f"\n  [NL2SQL] Q: {question}")
        print(f"           SQL: {sql}")

        results = execute_sql(sql)

        if results and "error" not in results[0]:
            success_count += 1
            returned_cols = " ".join(results[0].keys()).lower()
            if any(ec in returned_cols for ec in expected_cols):
                column_hit_count += 1
                print(f"           [OK]  Column match in: {list(results[0].keys())}")
            else:
                print(f"           [WARN] No column match. Got: {list(results[0].keys())}, "
                      f"expected any of: {expected_cols}")
        else:
            error = results[0].get("error", "empty result") if results else "empty result"
            print(f"           [FAIL] SQL failed: {error}")

    success_rate = success_count / total
    column_rate = column_hit_count / total

    print(f"\nNL2SQL Results:")
    print(f"   SQL execution success = {success_count}/{total} = {success_rate:.0%}  (threshold >= 80%)")
    print(f"   Column accuracy       = {column_hit_count}/{total} = {column_rate:.0%}  (threshold >= 80%)")

    assert success_rate >= 0.80, (
        f"NL2SQL execution success rate too low: {success_rate:.0%} < 80%"
    )
    assert column_rate >= 0.80, (
        f"NL2SQL column accuracy too low: {column_rate:.0%} < 80%"
    )
