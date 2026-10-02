import streamlit as st
import json
from src.retrieval.retriever import KnowledgeBaseRetriever
from src.retrieval.kb_loader import load_knowledge_base
from src.retrieval.chunker import create_chunks
from src.triage.service import triage_ticket
from src.account_health.service import generate_account_health_brief

st.set_page_config(
    page_title="RiskLens AI – Enhanced TAM & Support Agent",
    page_icon="🛡️",
    layout="wide"
)

# Initialize retriever once
@st.cache_resource
def get_retriever():
    documents = load_knowledge_base()
    chunks = create_chunks(documents)
    return KnowledgeBaseRetriever(chunks)

retriever = get_retriever()

st.title("🛡️ RiskLens AI – Enhanced TAM & Support Agent")
st.markdown("Production-grade AI assistance for Technical Support Triage and Technical Account Management (TAM).")

tab1, tab2 = st.tabs(["🎫 Ticket Triage", "🏢 Account Health Summarizer"])

with tab1:
    st.header("Intelligent Support Ticket Triage")
    st.markdown("Classifies ticket intent, determines priority, validates with RAG, and enforces strict guardrails.")
    
    with st.form("triage_form"):
        subject = st.text_input("Ticket Subject", placeholder="e.g., Multiple users cannot log in via SSO")
        body = st.text_area("Ticket Body", placeholder="Paste the complete customer message here...", height=180)
        
        submitted = st.form_submit_button("Triage Ticket")
        
        if submitted:
            if not subject.strip() or not body.strip():
                st.warning("Please provide both subject and body to triage.")
            else:
                with st.spinner("Triaging ticket through RAG pipeline and priority guardrails..."):
                    try:
                        result = triage_ticket(
                            subject=subject.strip(),
                            body=body.strip(),
                            retriever=retriever,
                            top_k=3
                        )
                        
                        st.success("Triage Analysis Complete!")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Priority", result.priority)
                        col2.metric("Category", result.issue_category)
                        col3.metric("Product Area", result.product_area)
                        col4.metric("Confidence", f"{result.confidence} ({int(result.confidence_score * 100)}%)")

                        if result.flagged_for_human_review:
                            st.warning("⚠️ **Flagged for Human Review**: This prediction triggered a priority guardrail, ambiguity flag, or low confidence threshold.")
                        
                        if result.needs_clarification:
                            st.info("❓ **Clarification Needed**: Ticket lacks critical reproduction details.")
                            for q in result.clarifying_questions:
                                st.markdown(f"- {q}")

                        # Clean separation of facts and reasoning
                        col_facts, col_reason = st.columns(2)
                        with col_facts:
                            st.subheader("📚 Verified Retrieved Facts")
                            if result.retrieved_facts:
                                for fact in result.retrieved_facts:
                                    st.markdown(f"• {fact}")
                            else:
                                st.write("No specific factual citations extracted.")

                        with col_reason:
                            st.subheader("🧠 Model Reasoning")
                            st.write(result.model_reasoning or result.reasoning)

                        st.subheader("💬 Recommended Draft First Response")
                        st.info(result.draft_first_response)

                        if result.knowledge_base_references:
                            st.subheader("📖 Traceable Knowledge Base References")
                            for ref in result.knowledge_base_references:
                                st.markdown(f"- **{ref.document}** (`{ref.path}`): _{ref.relevance_reason}_")

                        with st.expander("🔍 Audit Notes & Raw Output JSON"):
                            st.markdown(f"**Audit Notes:** {result.audit_notes}")
                            st.json(result.model_dump())
                        
                    except Exception as e:
                        st.error(f"Error processing ticket: {str(e)}")

with tab2:
    st.header("TAM Account Health Summarizer")
    st.markdown("Generates deterministic operational metrics, identifies verified risk signals, and drafts executive talking points.")
    
    with st.form("account_health_form"):
        account_id = st.text_input("Account ID", placeholder="e.g., ACC-3336, ACC-002, ACC-3033, ACC-8113, ACC-5748")
        submitted_health = st.form_submit_button("Generate Account Brief")
        
        if submitted_health:
            if not account_id.strip():
                st.warning("Please provide an Account ID.")
            else:
                with st.spinner("Analyzing account history, open tickets, and risk signals..."):
                    try:
                        brief = generate_account_health_brief(account_id=account_id.strip())
                        
                        st.success(f"Brief generated for **{brief.company}** (`{brief.account_id}`)")
                        
                        st.subheader("📋 Executive Summary")
                        st.write(brief.executive_summary)
                        
                        st.subheader("⚠️ Open Risks & Flagged Issues")
                        if brief.open_risks_and_flagged_issues:
                            for issue in brief.open_risks_and_flagged_issues:
                                badge = "🔴 High" if issue.severity == "High" else "🟡 Medium" if issue.severity == "Medium" else "🟢 Low"
                                with st.expander(f"{badge} — {issue.risk_type} (Source: {issue.source})"):
                                    st.write(f"**Reason:** {issue.reason}")
                                    if issue.ticket_id:
                                        st.write(f"**Ticket ID:** `{issue.ticket_id}`")
                                    if issue.evidence_quote:
                                        st.write(f"**Direct Evidence:** _{issue.evidence_quote}_")
                        else:
                            st.write("✅ No active risk indicators detected in recent account history.")
                            
                        st.subheader("💬 Recommended Talking Points for TAM")
                        for idx, point in enumerate(brief.recommended_talking_points, 1):
                            st.markdown(f"{idx}. {point}")

                        with st.expander("🔍 View Raw Output JSON"):
                            st.json(brief.model_dump())
                            
                    except ValueError as ve:
                        st.warning(str(ve))
                    except Exception as e:
                        st.error(f"Error generating brief: {str(e)}")
