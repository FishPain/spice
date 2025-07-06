import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agent.agent import build_graph
from agent.context.spice import SPICE_CONTEXT
import json
from pathlib import Path

# Load .env
load_dotenv()

# === Configuration ===
websites = {
    "NEA": "https://www.nea.gov.sg/media/news",
    "PUB": "https://www.pub.gov.sg/Resources/News-Room/PressReleases",
    "BCA": "https://www1.bca.gov.sg/about-us/news-and-publications/media-releases",
    "IMDA": "https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches",
}

st.set_page_config(page_title="SPICE Automated Outreach System", layout="wide")
st.title("📡 SPICE Automated Outreach System")

# === Session State ===
if "output" not in st.session_state:
    st.session_state.output = None
if "selected_article_index" not in st.session_state:
    st.session_state.selected_article_index = 0

left_col, right_col = st.columns([1, 1])

# === Left Column: Input Panel ===
with left_col:
    st.markdown("### 🏛️ Select a Government Agency")
    agency = st.selectbox(
        "Agency", options=websites.keys(), index=0, label_visibility="collapsed"
    )

    if st.button("🚀 Run Analysis"):
        with st.spinner("🔍 Analyzing article(s)... please wait"):
            scraped_articles_path = Path("all_articles.json")
            scraped_articles = (
                json.loads(scraped_articles_path.read_text(encoding="utf-8"))
                if scraped_articles_path.exists()
                else {}
            )

            model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            graph = build_graph().compile()

            # try:
            inputs = {
                "model": model,
                "spice_context": SPICE_CONTEXT,
                "websites": websites,
                "website_selected": agency,
                "max_results": 10,
                "scraped_articles": scraped_articles,
            }
            result = graph.invoke(inputs)
            st.session_state.output = result

            # Save merged articles
            scraped_articles_path.write_text(
                json.dumps(
                    result.get("scraped_articles", scraped_articles),
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            if not result.get("scraped_data"):
                st.warning("No new articles were found from this agency.")
            else:
                st.success("✅ Analysis complete!")

            st.session_state.selected_article_index = 0

            # except Exception as e:
            #     st.error(f"❌ An error occurred during analysis: {e}")

# === Right Column: Results Panel ===
output = st.session_state.output
if output:
    scraped_data = output.get("scraped_data", [])
    if not scraped_data:
        st.info("🕵️‍♀️ No relevant articles to display.")
    else:
        st.markdown("### 📑 Select and Review Articles")

        titles = [a.get("title", f"Article {i+1}") for i, a in enumerate(scraped_data)]
        selected_index = st.selectbox(
            "Select Article",
            options=range(len(titles)),
            format_func=lambda i: titles[i],
        )
        selected_article = scraped_data[selected_index]

        # === Article Metadata ===
        st.subheader("📰 Article Information")
        st.markdown(f"**Title:** {selected_article.get('title', 'N/A')}")
        st.markdown(f"[🔗 View Full Article]({selected_article.get('url', '#')})")

        st.markdown("#### 📄 Full Text")
        st.markdown(selected_article.get("body", "No content found."))

        # === Relevance ===
        rel = output.get("relevance", {}).get(str(selected_index), {})
        st.subheader("🔍 Relevance Check")
        st.markdown(f"**Relevant:** `{rel.get('is_relevant', False)}`")
        st.markdown(f"**Reason:** {rel.get('reason', 'No justification provided.')}`")

        # === Entities ===
        entities = output.get("business_entity", {}).get(str(selected_index), [])
        st.subheader("🏢 Business Entities")
        if entities:
            for entity in entities:
                st.markdown(
                    f"- **{entity['name']}** ({entity['type']}): {entity['role']}"
                )
        else:
            st.info("No business entities identified.")

        # === Opportunity ===
        st.subheader("🚀 Collaboration Opportunity")
        st.markdown(
            f"**Opportunity:** {output.get('opportunity', {}).get(str(selected_index), 'Not available.')}"
        )
        st.markdown(
            f"**Justification:** {output.get('justification', {}).get(str(selected_index), 'Not available.')}"
        )

        # === Email Draft ===
        st.subheader("📧 Email Draft Generator")
        email_map = output.get("email_draft", {}).get(str(selected_index), {})
        if email_map:
            entity_options = list(email_map.keys())
            selected_entity = st.selectbox(
                "Select Business Entity for Email", entity_options
            )
            st.code(email_map[selected_entity], language="markdown")
        else:
            st.info("No email drafts available.")
