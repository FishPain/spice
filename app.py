import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agent.agent import build_graph
from agent.context.spice import SPICE_CONTEXT
import json
from pathlib import Path

# === Load environment ===
load_dotenv()

# === Default configuration ===
DEFAULT_WEBSITES = {
    "NEA": "https://www.nea.gov.sg/media/news",
    "PUB": "https://www.pub.gov.sg/Resources/News-Room/PressReleases",
    "BCA": "https://www1.bca.gov.sg/about-us/news-and-publications/media-releases",
    "IMDA": "https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches",
}

# === Session State Init ===
st.set_page_config(page_title="SPICE Outreach System", layout="wide")
st.title("📡 SPICE Automated Outreach System")

if "websites" not in st.session_state:
    st.session_state.websites = DEFAULT_WEBSITES.copy()
if "output" not in st.session_state:
    st.session_state.output = None
if "selected_article_index" not in st.session_state:
    st.session_state.selected_article_index = 0

# === Sidebar Controls ===
with st.sidebar:
    st.header("⚙️ Scraper Configuration")

    # Agency selection
    agency = st.selectbox("🏛️ Select Agency", list(st.session_state.websites.keys()))

    # Add new agency
    st.markdown("---")
    st.markdown("➕ **Add a New Agency**")
    with st.form("add_agency_form", clear_on_submit=True):
        new_agency_name = st.text_input("Agency Name")
        new_agency_url = st.text_input("Agency News URL")
        submitted = st.form_submit_button("Add")

        if submitted:
            if not new_agency_name or not new_agency_url:
                st.warning("Please provide both name and URL.")
            elif not new_agency_url.startswith("http"):
                st.warning("URL must start with http or https.")
            elif new_agency_name in st.session_state.websites:
                st.warning("This agency already exists.")
            else:
                st.session_state.websites[new_agency_name] = new_agency_url
                st.success(f"✅ Added {new_agency_name}")
                agency = new_agency_name  # refresh

    st.markdown("---")
    # Scraper settings
    st.markdown("🧪 **Browser Settings**")
    browser_choice = st.selectbox("Browser", ["firefox", "chromium", "webkit"])
    st.session_state.browser = browser_choice

    headless = st.checkbox("Headless Mode", value=True)
    st.session_state.headless = headless

    run_analysis = st.button("🔍 Run Scraper & Analyze Articles")

# === Run Analysis Button ===
st.markdown("## 🚀 Run Scraper & Analyze Articles")
if run_analysis:
    with st.spinner("Fetching and analyzing articles..."):
        scraped_path = Path("all_articles.json")
        scraped_articles = (
            json.loads(scraped_path.read_text(encoding="utf-8"))
            if scraped_path.exists()
            else {}
        )

        model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        graph = build_graph().compile()

        try:
            inputs = {
                "model": model,
                "spice_context": SPICE_CONTEXT,
                "websites": st.session_state.websites,
                "website_selected": agency,
                "max_results": 10,
                "scraped_articles": scraped_articles,
                "headless": st.session_state.headless,
                "browser": st.session_state.browser,
            }

            result = graph.invoke(inputs)
            st.session_state.output = result

            # Save updated article state
            scraped_path.write_text(
                json.dumps(
                    result.get("scraped_articles", scraped_articles),
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            articles = result.get("articles", [])
            if articles:
                st.success(f"✅ Found {len(articles)} relevant article(s).")
                st.session_state.selected_article_index = 0

        except Exception as e:
            st.error(f"❌ Error during analysis:\n\n`{e}`")

# === Article Viewer ===
output = st.session_state.output
if output:
    articles = output.get("articles", [])
    if articles:
        st.markdown("## 📄 Article Review Panel")
        selected_index = st.selectbox(
            "🗂️ Select Article",
            options=range(len(articles)),
            format_func=lambda i: f"{i + 1}. {articles[i].title}",
        )
        article = articles[selected_index]

        # === Article Content
        st.markdown("### 📰 Article Details")
        st.markdown(f"**🧾 Title:** {article.title}")
        st.markdown(
            f"**🔗 URL:** [View Original]({article.url})", unsafe_allow_html=True
        )
        st.markdown("**📃 Content:**")
        st.write(article.body)

        # === Relevance
        st.markdown("### 🧠 Relevance Assessment")
        st.markdown(f"- **Relevant:** `{article.relevance.is_relevant}`")
        st.markdown(f"- **Reason:** {article.relevance.reason}")

        # === Business Entities
        st.markdown("### 🏢 Detected Business Entities")
        if article.business_entities:
            for e in article.business_entities:
                st.markdown(f"- **{e.name}** ({e.type}) — _{e.role}_")
        else:
            st.info("No entities found.")

        # === Opportunity
        st.markdown("### 🚀 Collaboration Opportunity")
        if article.opportunity:
            st.markdown(f"**Opportunity:** {article.opportunity.opportunity}")
            st.markdown(f"**Justification:** {article.opportunity.justification}")
        else:
            st.info("No opportunity identified.")

        # === Email Draft
        st.markdown("### 📧 Outreach Email Draft")
        if article.email_drafts:
            selected_entity = st.selectbox(
                "Choose Entity", list(article.email_drafts.keys())
            )
            st.code(article.email_drafts[selected_entity], language="markdown")
        else:
            st.info("No draft available.")
    else:
        st.warning("⚠️ No relevant articles available.")
