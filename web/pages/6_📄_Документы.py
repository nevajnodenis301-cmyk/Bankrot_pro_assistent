import streamlit as st
st.set_page_config(page_title="Документы", page_icon="📄", layout="wide")

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import require_auth, get_auth_headers, show_user_sidebar

# Require authentication
require_auth()

import httpx
from datetime import datetime

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def get_headers():
    return get_auth_headers()


st.title("📄 Документы")

# Show user in sidebar
show_user_sidebar()


@st.cache_data(ttl=30)
def get_document_types():
    """Fetch available document types from API."""
    try:
        response = httpx.get(f"{API_URL}/api/documents/types", headers=get_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Ошибка при загрузке типов документов: {str(e)}")
        return []


@st.cache_data(ttl=30)
def get_cases():
    """Fetch user's cases from API."""
    try:
        response = httpx.get(f"{API_URL}/api/cases", headers=get_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Ошибка при загрузке дел: {str(e)}")
        return []


def get_case_documents(case_id: int):
    """Fetch documents for a specific case."""
    try:
        response = httpx.get(
            f"{API_URL}/api/documents/cases/{case_id}/files",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Ошибка при загрузке документов дела: {str(e)}")
        return []


def generate_document(case_id: int, document_type: str):
    """Generate a document for a case."""
    try:
        response = httpx.post(
            f"{API_URL}/api/documents/cases/{case_id}/generate",
            json={"document_type": document_type},
            headers=get_headers(),
            timeout=60.0
        )
        response.raise_for_status()
        return response.json(), None
    except httpx.HTTPStatusError as e:
        error_detail = "Ошибка генерации документа"
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except Exception:
            pass
        return None, error_detail
    except Exception as e:
        return None, f"Ошибка: {str(e)}"


def download_document(case_id: int, file_name: str):
    """Download a document file."""
    try:
        response = httpx.get(
            f"{API_URL}/api/documents/cases/{case_id}/files/{file_name}",
            headers=get_headers(),
            timeout=60.0
        )
        response.raise_for_status()
        return response.content, None
    except Exception as e:
        return None, f"Ошибка скачивания: {str(e)}"


# Document type labels in Russian
DOCUMENT_TYPE_LABELS = {
    "bankruptcy_petition": "Заявление о банкротстве (полное)",
    "bankruptcy_application": "Заявление о банкротстве (базовое)",
}

# Document type icons
DOCUMENT_TYPE_ICONS = {
    "bankruptcy_petition": "📝",
    "bankruptcy_application": "📋",
}

# Tabs for different sections
tab_generate, tab_history = st.tabs(["🆕 Создать документ", "📁 Сгенерированные документы"])

# ===== TAB 1: Generate New Document =====
with tab_generate:
    st.subheader("Создание документа")

    # Get document types
    document_types = get_document_types()

    if not document_types:
        st.warning("Шаблоны документов не найдены")
    else:
        # Get cases
        cases = get_cases()

        if not cases:
            st.warning("У вас нет дел. Сначала создайте дело в разделе '➕ Новое дело'")
        else:
            # Display document type selection
            st.write("**Шаг 1: Выберите тип документа**")

            # Create selection cards for document types
            doc_type_options = {}
            for doc in document_types:
                doc_type = doc["document_type"]
                label = DOCUMENT_TYPE_LABELS.get(doc_type, doc["label"])
                icon = DOCUMENT_TYPE_ICONS.get(doc_type, "📄")
                doc_type_options[doc_type] = f"{icon} {label}"

            selected_doc_type = st.selectbox(
                "Тип документа",
                options=list(doc_type_options.keys()),
                format_func=lambda x: doc_type_options[x],
                key="doc_type_select"
            )

            # Show description for selected document type
            selected_doc = next((d for d in document_types if d["document_type"] == selected_doc_type), None)
            if selected_doc and selected_doc.get("description"):
                st.info(f"ℹ️ {selected_doc['description']}")

            st.divider()

            # Case selection
            st.write("**Шаг 2: Выберите дело**")

            # Format case options
            case_options = {
                case["id"]: f"{case['case_number']} — {case['full_name']}"
                for case in cases
            }

            selected_case_id = st.selectbox(
                "Дело",
                options=list(case_options.keys()),
                format_func=lambda x: case_options[x],
                key="case_select"
            )

            # Show case info
            selected_case = next((c for c in cases if c["id"] == selected_case_id), None)
            if selected_case:
                with st.expander("📋 Информация о деле", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ФИО:** {selected_case.get('full_name', '—')}")
                        st.write(f"**Номер дела:** {selected_case.get('case_number', '—')}")
                        debt = selected_case.get("total_debt")
                        st.write(f"**Общий долг:** {float(debt or 0):,.0f} руб." if debt else "**Общий долг:** не указан")
                    with col2:
                        st.write(f"**Кредиторов:** {selected_case.get('creditors_count', 0)}")
                        status_map = {
                            "new": "Новое",
                            "in_progress": "В работе",
                            "court": "В суде",
                            "completed": "Завершено"
                        }
                        status = status_map.get(selected_case.get("status"), selected_case.get("status", "—"))
                        st.write(f"**Статус:** {status}")

            st.divider()

            # Generate button
            st.write("**Шаг 3: Сгенерируйте документ**")

            col1, col2 = st.columns([1, 3])
            with col1:
                generate_clicked = st.button(
                    "📄 Сгенерировать",
                    type="primary",
                    use_container_width=True
                )

            if generate_clicked:
                with st.spinner("Генерация документа..."):
                    result, error = generate_document(selected_case_id, selected_doc_type)

                    if error:
                        st.error(f"❌ {error}")
                    elif result:
                        st.success(f"✅ Документ успешно создан: {result['file_name']}")

                        # Offer download
                        file_content, download_error = download_document(
                            selected_case_id,
                            result["file_name"]
                        )

                        if download_error:
                            st.error(f"❌ {download_error}")
                        elif file_content:
                            st.download_button(
                                label="⬇️ Скачать документ",
                                data=file_content,
                                file_name=result["file_name"],
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                type="primary"
                            )

                        # Clear cache to refresh document list
                        st.cache_data.clear()

# ===== TAB 2: Document History =====
with tab_history:
    st.subheader("Сгенерированные документы")

    # Get cases
    cases = get_cases()

    if not cases:
        st.warning("У вас нет дел")
    else:
        # Case filter
        case_filter_options = {"all": "Все дела"}
        case_filter_options.update({
            case["id"]: f"{case['case_number']} — {case['full_name']}"
            for case in cases
        })

        selected_filter_case = st.selectbox(
            "Фильтр по делу",
            options=list(case_filter_options.keys()),
            format_func=lambda x: case_filter_options[x],
            key="filter_case_select"
        )

        # Refresh button
        if st.button("🔄 Обновить", key="refresh_docs"):
            st.cache_data.clear()
            st.rerun()

        st.divider()

        # Determine which cases to show
        cases_to_show = cases if selected_filter_case == "all" else [c for c in cases if c["id"] == selected_filter_case]

        total_documents = 0

        for case in cases_to_show:
            documents = get_case_documents(case["id"])

            if documents:
                total_documents += len(documents)

                with st.expander(f"📁 {case['case_number']} — {case['full_name']} ({len(documents)} док.)", expanded=True):
                    for doc in documents:
                        col1, col2, col3 = st.columns([3, 2, 1])

                        with col1:
                            doc_type = doc.get("document_type", "")
                            icon = DOCUMENT_TYPE_ICONS.get(doc_type, "📄")
                            label = DOCUMENT_TYPE_LABELS.get(doc_type, doc_type or "Документ")
                            st.write(f"{icon} **{doc['file_name']}**")
                            st.caption(label)

                        with col2:
                            # Format size
                            size_bytes = doc.get("size_bytes", 0)
                            if size_bytes > 1024 * 1024:
                                size_str = f"{size_bytes / (1024 * 1024):.1f} МБ"
                            elif size_bytes > 1024:
                                size_str = f"{size_bytes / 1024:.1f} КБ"
                            else:
                                size_str = f"{size_bytes} Б"

                            # Format date
                            modified_at = doc.get("modified_at", "")
                            if modified_at:
                                try:
                                    dt = datetime.fromisoformat(modified_at.replace('Z', '+00:00'))
                                    date_str = dt.strftime("%d.%m.%Y %H:%M")
                                except Exception:
                                    date_str = modified_at[:16] if len(modified_at) > 16 else modified_at
                            else:
                                date_str = "—"

                            st.caption(f"📅 {date_str}")
                            st.caption(f"📦 {size_str}")

                        with col3:
                            # Download button
                            file_content, error = download_document(case["id"], doc["file_name"])
                            if file_content:
                                st.download_button(
                                    label="⬇️",
                                    data=file_content,
                                    file_name=doc["file_name"],
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key=f"download_{case['id']}_{doc['file_name']}"
                                )

                        st.divider()

        if total_documents == 0:
            st.info("📭 Документов пока нет. Создайте первый документ во вкладке 'Создать документ'")
        else:
            st.caption(f"Всего документов: {total_documents}")
