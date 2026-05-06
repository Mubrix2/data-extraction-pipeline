# frontend/app.py
import json
import pandas as pd
import streamlit as st
from api_client import check_health, extract_file, extract_text, get_schemas

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Extraction Pipeline",
    page_icon="🔍",
    layout="wide",
)

# ── Constants ─────────────────────────────────────────────────────────────────
ACCEPTED_FILE_TYPES = ["pdf", "docx", "txt"]

CONTENT_TYPE_MAP = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
}

SCHEMA_ICONS = {
    "job_posting": "💼",
    "invoice": "🧾",
    "contact_info": "📇",
    "news_article": "📰",
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def render_extracted_data(data: dict, schema_type: str):
    """Render extracted data as formatted sections based on schema type."""

    if schema_type == "job_posting":
        st.markdown(f"### 💼 {data.get('job_title', 'Unknown Title')}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Company", data.get("company_name") or "Not mentioned")
        with col2:
            st.metric("Location", data.get("location") or "Not mentioned")
        with col3:
            st.metric("Type", data.get("employment_type") or "Not mentioned")

        col4, col5 = st.columns(2)
        with col4:
            st.metric("Experience", data.get("experience_required") or "Not mentioned")
        with col5:
            st.metric("Salary", data.get("salary_range") or "Not mentioned")

        if data.get("summary"):
            st.info(data["summary"])

        if data.get("requirements"):
            st.markdown("**Requirements:**")
            for req in data["requirements"]:
                badge = "✅" if req.get("is_required") else "⭕"
                st.markdown(f"{badge} {req.get('requirement', '')}")

        if data.get("responsibilities"):
            st.markdown("**Responsibilities:**")
            for r in data["responsibilities"]:
                st.markdown(f"• {r}")

        if data.get("benefits"):
            st.markdown("**Benefits:**")
            for b in data["benefits"]:
                st.markdown(f"• {b}")

        if data.get("application_deadline"):
            st.caption(f"📅 Application deadline: {data['application_deadline']}")

    elif schema_type == "invoice":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Vendor:** {data.get('vendor_name') or 'Unknown'}")
            st.markdown(f"**Invoice #:** {data.get('invoice_number') or 'N/A'}")
            st.markdown(f"**Date:** {data.get('invoice_date') or 'N/A'}")
        with col2:
            st.markdown(f"**Client:** {data.get('client_name') or 'Unknown'}")
            st.markdown(f"**Due Date:** {data.get('due_date') or 'N/A'}")
            st.markdown(f"**Payment Terms:** {data.get('payment_terms') or 'N/A'}")

        if data.get("line_items"):
            st.markdown("**Line Items:**")
            rows = []
            for item in data["line_items"]:
                rows.append({
                    "Description": item.get("description", ""),
                    "Quantity": item.get("quantity", ""),
                    "Unit Price": item.get("unit_price", ""),
                    "Total": item.get("total", ""),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric("Subtotal", data.get("subtotal") or "N/A")
        with col4:
            st.metric("Tax", data.get("tax_amount") or "N/A")
        with col5:
            st.metric("Total", data.get("total_amount") or "N/A")

    elif schema_type == "contact_info":
        contacts = data.get("contacts", [])
        st.markdown(f"**{data.get('total_contacts_found', 0)} contact(s) found**")

        for i, contact in enumerate(contacts, 1):
            with st.expander(
                f"👤 {contact.get('name') or f'Contact {i}'} "
                f"— {contact.get('title') or contact.get('organisation') or ''}",
                expanded=True,
            ):
                col1, col2 = st.columns(2)
                with col1:
                    if contact.get("email"):
                        st.markdown(f"📧 {contact['email']}")
                    if contact.get("phone"):
                        st.markdown(f"📞 {contact['phone']}")
                    if contact.get("organisation"):
                        st.markdown(f"🏢 {contact['organisation']}")
                with col2:
                    if contact.get("address"):
                        st.markdown(f"📍 {contact['address']}")
                    if contact.get("linkedin"):
                        st.markdown(f"🔗 {contact['linkedin']}")
                    if contact.get("website"):
                        st.markdown(f"🌐 {contact['website']}")

        if data.get("organisations"):
            st.markdown("**Organisations mentioned:**")
            for org in data["organisations"]:
                st.markdown(f"• {org}")

    elif schema_type == "news_article":
        st.markdown(f"### 📰 {data.get('headline', 'No headline')}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"📅 {data.get('publication_date') or 'Date unknown'}")
        with col2:
            st.caption(f"✍️ {data.get('author') or 'Author unknown'}")
        with col3:
            sentiment = data.get("sentiment", "neutral")
            badge = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}.get(sentiment, "⚪")
            st.caption(f"{badge} Sentiment: {sentiment.title()}")

        if data.get("summary"):
            st.info(data["summary"])

        if data.get("key_facts"):
            st.markdown("**Key Facts:**")
            for fact in data["key_facts"]:
                st.markdown(f"• {fact}")

        if data.get("key_entities"):
            st.markdown("**Key Entities:**")
            cols = st.columns(3)
            for i, entity in enumerate(data["key_entities"]):
                with cols[i % 3]:
                    st.markdown(
                        f"`{entity.get('entity_type', '')}` {entity.get('name', '')}"
                    )

        if data.get("topics"):
            st.markdown(
                " ".join([f"`{t}`" for t in data["topics"]])
            )


def to_excel_bytes(data: dict) -> bytes:
    """Convert extracted data dict to Excel bytes for download."""
    rows = []
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    row = {"field": key}
                    row.update(item)
                    rows.append(row)
                else:
                    rows.append({"field": key, "value": str(item)})
        else:
            rows.append({"field": key, "value": str(value) if value else ""})

    df = pd.DataFrame(rows)
    output = pd.ExcelWriter.__new__(pd.ExcelWriter)

    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Extracted Data")
    return buffer.getvalue()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔍 Data Extractor")
    st.caption("Structured extraction from unstructured text")

    st.divider()

    is_healthy = check_health()
    if is_healthy:
        st.success("API connected", icon="🟢")
    else:
        st.error("API unreachable", icon="🔴")
        st.caption("Start the server: `uvicorn app.main:app --reload`")

    st.divider()

    # Schema selector
    st.subheader("1. Choose Schema")
    schemas_result = get_schemas()
    if schemas_result["success"]:
        schema_options = {
            f"{SCHEMA_ICONS.get(s['schema_type'], '📄')} {s['schema_type'].replace('_', ' ').title()}": s["schema_type"]
            for s in schemas_result["data"]["schemas"]
        }
    else:
        schema_options = {"job_posting": "job_posting"}

    selected_label = st.selectbox(
        "Extraction schema",
        options=list(schema_options.keys()),
        help="Choose what type of document you are extracting from",
    )
    selected_schema = schema_options[selected_label]

    st.divider()

    # Input method
    st.subheader("2. Choose Input Method")
    input_method = st.radio(
        "How do you want to provide the text?",
        options=["Paste text", "Upload file"],
        horizontal=True,
    )

    st.divider()
    st.caption("Supported files: PDF, DOCX, TXT")
    st.caption("Max file size: 10MB")
    st.caption("Max text length: 50,000 characters")


# ── Main area ─────────────────────────────────────────────────────────────────
st.title("Data Extraction Pipeline")
st.caption(
    "Extract structured data from any unstructured text or document. "
    "Choose a schema, provide your input, and get clean JSON instantly."
)

if not is_healthy:
    st.warning("⚠️ Backend API is not reachable. Start your FastAPI server first.")
    st.stop()

st.divider()

# ── Input area ────────────────────────────────────────────────────────────────
result = None

if input_method == "Paste text":
    text_input = st.text_area(
        "Paste your text here",
        height=250,
        placeholder="Paste a job description, invoice text, article, or any business text...",
    )
    if st.button("Extract", type="primary", disabled=not text_input.strip()):
        with st.spinner("Extracting structured data..."):
            result = extract_text(
                text=text_input,
                schema_type=selected_schema,
            )

else:
    uploaded_file = st.file_uploader(
        "Upload your document",
        type=ACCEPTED_FILE_TYPES,
        help="PDF, DOCX, or TXT files up to 10MB",
    )
    if uploaded_file:
        st.caption(f"📎 {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

    if st.button(
        "Extract",
        type="primary",
        disabled=uploaded_file is None,
    ):
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
        content_type = CONTENT_TYPE_MAP.get(ext, "text/plain")

        with st.spinner("Parsing file and extracting data..."):
            result = extract_file(
                file_bytes=uploaded_file.read(),
                filename=uploaded_file.name,
                content_type=content_type,
                schema_type=selected_schema,
            )

# ── Results ───────────────────────────────────────────────────────────────────
if result:
    if result["success"]:
        data = result["data"]
        extracted = data["extracted_data"]

        st.success(
            f"✅ Extraction complete — "
            f"{data['character_count']:,} characters processed"
        )

        st.divider()

        # Tabs — formatted view and raw JSON side by side
        tab1, tab2 = st.tabs(["📋 Formatted View", "{ } Raw JSON"])

        with tab1:
            render_extracted_data(extracted, selected_schema)

        with tab2:
            st.json(extracted)

        st.divider()

        # Download buttons
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="⬇️ Download JSON",
                data=json.dumps(extracted, indent=2),
                file_name=f"extracted_{selected_schema}.json",
                mime="application/json",
            )
        with col2:
            st.download_button(
                label="⬇️ Download Excel",
                data=to_excel_bytes(extracted),
                file_name=f"extracted_{selected_schema}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    else:
        st.error(f"❌ {result['error']}")