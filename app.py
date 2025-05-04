import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agent.agent import build_graph
from agent.context.spice import SPICE_CONTEXT

# Load .env
load_dotenv()

st.set_page_config(page_title="SPICE Automated Outreach System", layout="wide")
st.title("📡 SPICE Automated Outreach System")

# Initialize session state
if "output" not in st.session_state:
    st.session_state.output = None

# Create two columns
left_col, right_col = st.columns([1, 1])

# --- Left Column: Control Panel ---
with left_col:
    st.markdown("### 🏛️ Select a Government Agency")
    agency = st.selectbox(
        label="Agency",
        options=["NEA - National Environment Agency"],  # Extend this list
        index=0,
        label_visibility="collapsed",
        key="agency_select",
    )

    if st.button("🚀 Run Analysis"):
        with st.spinner("🔍 Analyzing article... please wait"):
            model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            graph = build_graph().compile()
            inputs = {
                "model": model,
                "spice_context": SPICE_CONTEXT,
            }
            st.session_state.output = graph.invoke(inputs)
        st.success("✅ Analysis complete!")

    # --- Right Column: Output Display ---
    output = st.session_state.output
    if output:
        # --- Article Info ---
        st.subheader("📰 Article Information")
        scraped = output.get("scraped_data", {})
        st.markdown(f"**Title:** {scraped.get('title', 'N/A')}")
        st.markdown(f"**Published Date:** {scraped.get('date', 'N/A')}")
        st.markdown(f"[🔗 View Full Article]({scraped.get('url', '#')})")

        # --- Relevance ---
        st.subheader("🔍 Relevance Check")
        rel = output.get("relevance", {})
        st.markdown(f"**Relevant:** `{rel.get('is_relevant', False)}`")
        st.markdown(f"**Reason:** {rel.get('reason', 'No reason provided')}")

        # --- Business Entities ---
        st.subheader("🏢 Business Entities")
        entity_list = output.get("business_entity", [])
        for entity in entity_list:
            st.markdown(f"- **{entity.name}** ({entity.type}): {entity.role}")

        # --- Opportunity ---
        st.subheader("🚀 Collaboration Opportunity")
        st.markdown(f"**Opportunity:** {output.get('opportunity', 'Not available')}")
        st.markdown(
            f"**Justification:** {output.get('justification', 'Not available')}"
        )

with right_col:
    output = st.session_state.output

    if output:
        # --- Email Draft ---
        st.subheader("📧 Email Draft Generator")
        email_map = output.get("email_draft", {})
        if isinstance(email_map, dict) and email_map:
            entity_options = list(email_map.keys())
            selected_entity = st.selectbox(
                "Select Business Entity for Email",
                entity_options,
                index=0,
                key="email_entity_select",
            )
            email_text = email_map[selected_entity]
            st.code(email_text, language="markdown")
        else:
            st.info("No email drafts available.")
