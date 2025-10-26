import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agent.agent import build_graph
from agent.context.spice import SPICE_CONTEXT
import json
import os
import logging
from pathlib import Path
from datetime import datetime

# === Load environment ===
load_dotenv()


# === Configure Logging ===
def setup_logging():
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create log filename with date
    log_file = log_dir / f"spice_{datetime.now().strftime('%Y%m%d')}.log"

    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Get or create logger
    logger = logging.getLogger("spice")
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler - writes to log file
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Console handler - writes to terminal/console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Initialize logger
logger = setup_logging()
logger.info("=" * 60)
logger.info("SPICE Application Started")
logger.info("=" * 60)


# === Authentication ===
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        app_password = os.getenv("APP_PASSWORD")

        # If no password is set in env, allow access
        if not app_password:
            st.session_state["authenticated"] = True
            logger.warning("APP_PASSWORD not set - Authentication disabled")
            st.warning("⚠️ No APP_PASSWORD set in environment. Authentication disabled.")
            return

        if st.session_state["password"] == app_password:
            st.session_state["authenticated"] = True
            logger.info("User authenticated successfully")
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["authenticated"] = False
            logger.warning("Failed authentication attempt")

    # First run - show login form
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        logger.info("New session started - authentication required")

    # Show login form if not authenticated
    if not st.session_state["authenticated"]:
        st.markdown("# 🔐 Login Required")
        st.markdown("Please enter your password to access the SPICE Outreach System.")

        with st.form("login_form"):
            st.text_input("Password", type="password", key="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                password_entered()

        if (
            st.session_state.get("authenticated") == False
            and "password" not in st.session_state
        ):
            st.error("😕 Password incorrect")

        return False

    return True


# === Default configuration ===
DEFAULT_WEBSITES = {
    "NEA": "https://www.nea.gov.sg/media/news",
    "PUB": "https://www.pub.gov.sg/Resources/News-Room/PressReleases",
    "BCA": "https://www1.bca.gov.sg/about-us/news-and-publications/media-releases",
    "IMDA": "https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches",
}

# === Session State Init ===
st.set_page_config(page_title="SPICE Outreach System", layout="wide")

# Check authentication before showing app
if not check_password():
    st.stop()  # Don't continue if not authenticated

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

    # Logout button at the top
    if st.button("🚪 Logout"):
        st.session_state["authenticated"] = False
        logger.info("User logged out")
        st.rerun()

    st.markdown("---")

    # Agency selection
    agency = st.selectbox("🏛️ Select Agency", list(st.session_state.websites.keys()))
    logger.debug(f"Agency selected: {agency}")

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
                logger.warning("Add agency failed: missing name or URL")
            elif not new_agency_url.startswith("http"):
                st.warning("URL must start with http or https.")
                logger.warning(
                    f"Add agency failed: invalid URL format - {new_agency_url}"
                )
            elif new_agency_name in st.session_state.websites:
                st.warning("This agency already exists.")
                logger.warning(f"Add agency failed: duplicate name - {new_agency_name}")
            else:
                st.session_state.websites[new_agency_name] = new_agency_url
                st.success(f"✅ Added {new_agency_name}")
                logger.info(f"New agency added: {new_agency_name} -> {new_agency_url}")
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
    logger.info("=" * 60)
    logger.info(f"Analysis started for agency: {agency}")
    logger.info(
        f"Browser: {st.session_state.browser}, Headless: {st.session_state.headless}"
    )

    with st.spinner("Fetching and analyzing articles..."):
        scraped_path = Path("all_articles.json")
        logger.info(f"Loading scraped articles from: {scraped_path.resolve()}")

        scraped_articles = (
            json.loads(scraped_path.read_text(encoding="utf-8"))
            if scraped_path.exists()
            else {}
        )
        logger.info(f"Loaded {len(scraped_articles)} previously scraped articles")

        model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        graph = build_graph().compile()
        logger.info("Graph compiled successfully")

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

            logger.info("Invoking graph with inputs...")
            result = graph.invoke(inputs)
            logger.info("Graph execution completed")

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
            logger.info(
                f"Saved {len(result.get('scraped_articles', {}))} articles to {scraped_path}"
            )

            articles = result.get("articles", [])
            if articles:
                relevant_count = sum(1 for a in articles if a.relevance.is_relevant)
                logger.info(
                    f"Found {len(articles)} articles, {relevant_count} relevant"
                )
                st.success(f"✅ Found {len(articles)} relevant article(s).")
                st.session_state.selected_article_index = 0
            else:
                logger.warning("No articles found in result")

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}", exc_info=True)
            st.error(f"❌ Error during analysis:\n\n`{e}`")

    logger.info("Analysis completed")
    logger.info("=" * 60)

# === Article Viewer ===
output = st.session_state.output
if output:
    articles = output.get("articles", [])
    if articles:
        logger.debug(f"Displaying {len(articles)} articles in viewer")
        st.markdown("## 📄 Article Review Panel")
        articles_sorted = sorted(articles, key=lambda a: not a.relevance.is_relevant)

        # Helper to truncate titles
        def truncate_title(title, max_length=100):
            return (
                title if len(title) <= max_length else title[: max_length - 3] + "..."
            )

        # Build labels showing truncated title + relevance in backticks
        labels = [
            f"{i + 1}. {truncate_title(article.title)}  "
            f"{'✅ Relevant' if article.relevance.is_relevant else '❌ Not Relevant'}"
            for i, article in enumerate(articles_sorted)
        ]

        # Streamlit selectbox
        selected_index = st.selectbox(
            "🗂️ Select Article",
            options=range(len(articles_sorted)),
            format_func=lambda i: labels[i],
        )

        # Get the selected article
        article = articles_sorted[selected_index]
        logger.debug(f"User selected article: {article.title[:50]}...")

        # === Relevance
        st.markdown("### 🧠 Relevance Assessment")
        st.markdown(f"- **Relevant:** `{article.relevance.is_relevant}`")
        st.markdown(f"- **Reason:** {article.relevance.reason}")

        # === Article Content
        st.markdown("### 📰 Article Details")
        st.markdown(f"**🧾 Title:** {article.title}")
        st.markdown(
            f"**🔗 URL:** [View Original]({article.url})", unsafe_allow_html=True
        )
        st.markdown("**📃 Content:**")
        st.write(article.body)

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
