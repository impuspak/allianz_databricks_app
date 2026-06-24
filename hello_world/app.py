import streamlit as st
import pandas as pd
from databricks.sdk import WorkspaceClient

st.set_page_config(
    page_title="Agent Launcher",
    page_icon="🚀",
    layout="centered",
)

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .launch-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.25rem;
    }
    .launch-sub {
        font-size: 1rem;
        color: #9ca3af;
        text-align: center;
        margin-bottom: 2.5rem;
    }
    div.stButton > button {
        width: 100%;
        height: 90px;
        font-size: 1.2rem;
        font-weight: 600;
        border-radius: 12px;
        border: 2px solid #FF3621;
        background-color: #FF3621;
        color: #ffffff;
        transition: background-color 0.2s ease, transform 0.1s ease;
    }
    div.stButton > button:hover {
        background-color: #cc2a18;
        transform: translateY(-2px);
    }
    div.stButton > button:active {
        transform: translateY(0px);
    }
    /* Brighter/whiter field labels */
    label, .stTextInput label, .stTextArea label, .stSelectbox label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    /* Brighter/whiter table display text */
    .rules-table-header {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem;
    }
    .rules-table-cell {
        color: #f0f0f0 !important;
        font-weight: 500 !important;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state for navigation ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"


def navigate(page_name: str):
    # If navigating to feedback_rules, clear cached data so page refreshes
    if page_name == "feedback_rules":
        st.session_state.pop("feedback_df", None)
        st.session_state.pop("selected_rule_idx", None)
        st.session_state.pop("selected_rule_record", None)
    st.session_state.page = page_name


# ── Page: Home ────────────────────────────────────────────────────────────────
def page_home():
    st.markdown('<p class="launch-title">Agent Launcher</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="launch-sub">Select an agent to launch</p>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("STTM Agent", key="sttm"):
            st.info("Launching STTM Agent...")
    with col2:
        if st.button("DQ Agent", key="dq"):
            navigate("dq_agent")
            st.rerun()


# ── Page: DQ Agent ────────────────────────────────────────────────────────────
def page_dq_agent():
    st.markdown('<p class="launch-title">DQ Agent</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="launch-sub">Choose an action</p>',
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        if st.button("Generate DQ Rules", key="gen_dq_rules"):
            navigate("generate_dq_rules")
            st.rerun()
    with col2:
        if st.button("Give Feedback for Rules", key="feedback_rules"):
            navigate("feedback_rules")
            st.rerun()
    with col3:
        if st.button("Apply DQ Rules", key="apply_dq_rules"):
            navigate("apply_dq_rules")
            st.rerun()

    st.markdown("---")
    if st.button("⬅ Back to Home", key="back_home_dq"):
        navigate("home")
        st.rerun()


# ── Page: Generate DQ Rules ───────────────────────────────────────────────────
def page_generate_dq_rules():
    st.markdown('<p class="launch-title">Generate DQ Rules</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="launch-sub">Provide parameters to trigger the DQ rules generator job</p>',
        unsafe_allow_html=True,
    )

    with st.form("dq_rules_form"):
        source_catalog = st.text_input("Source Catalog", value="")
        source_schema = st.text_input("Source Schema", value="")
        source_table = st.text_input("Source Table", value="")
        columns_to_profile = st.text_input(
            "Columns to Profile", value="", help="Comma-separated column names"
        )
        overwrite = st.selectbox("Overwrite (Y/N)", options=["Y", "N"], index=0)
        user_inputs = st.text_area("User Inputs", value="", height=100)

        submitted = st.form_submit_button("Generate")

    if submitted:
        if not source_catalog or not source_schema or not source_table:
            st.error("Please fill in Source Catalog, Source Schema, and Source Table.")
        else:
            job_params = {
                "source_catalog": source_catalog,
                "source_schema": source_schema,
                "source_table": source_table,
                "columns_to_profile": columns_to_profile,
                "overwrite(Y/N)": overwrite,
                "user_inputs": user_inputs,
            }
            try:
                w = WorkspaceClient()
                run = w.jobs.run_now(
                    job_id=614206750153806,
                    notebook_params=job_params,
                )
                st.success(
                    f"Job triggered successfully! Run ID: {run.run_id}"
                )
            except Exception as e:
                st.error(f"Failed to trigger job: {e}")

    st.markdown("---")
    if st.button("⬅ Back to DQ Agent", key="back_dq_agent"):
        navigate("dq_agent")
        st.rerun()


# ── Page: Apply DQ Rules ──────────────────────────────────────────────────────
def page_apply_dq_rules():
    st.markdown('<p class="launch-title">Apply DQ Rules</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="launch-sub">Provide parameters to apply DQ rules on your data</p>',
        unsafe_allow_html=True,
    )

    with st.form("apply_dq_rules_form"):
        source_table = st.text_input("Source Table", value="")
        source_sql = st.text_input("Source SQL (Optional - For incremental data)", value="")
        target_valid_table = st.text_input("Target Valid Table", value="")
        target_quarantine_table = st.text_input("Target Quarantine Table", value="")
        overwrite_target_tables = st.text_input("Overwrite Target Tables (Y/N)", value="")

        submitted = st.form_submit_button("Apply")

    if submitted:
        if not source_table:
            st.error("Please fill in Source Table.")
        else:
            job_params = {
                "table_for_dq_check": source_table,
                "data_for_dq_check": source_sql,
                "good_data_table": target_valid_table,
                "quarantine_table": target_quarantine_table,
                "overwrite_target_data" : overwrite_target_tables
            }
            try:
                w = WorkspaceClient()
                run = w.jobs.run_now(
                    job_id=424157152675054,
                    notebook_params=job_params,
                )
                st.success(
                    f"Job triggered successfully! Run ID: {run.run_id}"
                )
            except Exception as e:
                st.error(f"Failed to trigger job: {e}")

    st.markdown("---")
    if st.button("⬅ Back to DQ Agent", key="back_dq_agent_apply"):
        navigate("dq_agent")
        st.rerun()


# ── Page: Feedback for Rules ──────────────────────────────────────────────────
def page_feedback_rules():
    st.markdown('<p class="launch-title">Give Feedback for Rules</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="launch-sub">Fetch existing DQ rules and provide feedback</p>',
        unsafe_allow_html=True,
    )

    table_name = st.text_input("Enter table name", value="", key="feedback_table_name")

    if st.button("Fetch Rules", key="fetch_rules"):
        if not table_name:
            st.error("Please enter a table name.")
        else:
            try:
                w = WorkspaceClient()
                warehouses = list(w.warehouses.list())
                if not warehouses:
                    st.error("No SQL warehouse available.")
                else:
                    warehouse_id = warehouses[0].id
                    query = f"SELECT rule_id, column, name, criticality, check FROM allianz_ops.dqx_schema.table_checks WHERE table_name = '{table_name}'"
                    response = w.statement_execution.execute_statement(
                        warehouse_id=warehouse_id,
                        statement=query,
                        wait_timeout="30s",
                    )
                    if response.result and response.manifest:
                        columns = [col.name for col in response.manifest.schema.columns]
                        rows = []
                        for chunk in response.result.data_array:
                            rows.append(chunk)
                        if rows:
                            df = pd.DataFrame(rows, columns=columns)
                            st.session_state.feedback_df = df
                        else:
                            st.warning("No records found for the given table name.")
                            st.session_state.feedback_df = None
                    else:
                        st.warning("No records found for the given table name.")
                        st.session_state.feedback_df = None
            except Exception as e:
                st.error(f"Failed to fetch rules: {e}")
                st.session_state.feedback_df = None

    # Display results in tabular format with radio buttons as first column
    if "feedback_df" in st.session_state and st.session_state.feedback_df is not None:
        df = st.session_state.feedback_df
        st.markdown("---")
        st.markdown("**Fetched Rules:**")

        # Initialize selected row
        if "selected_rule_idx" not in st.session_state:
            st.session_state.selected_rule_idx = 0

        num_data_cols = len(df.columns)
        col_widths = [0.5] + [2] * num_data_cols

        # Render column header row (bright white)
        header_cols = st.columns(col_widths)
        with header_cols[0]:
            st.markdown("")
        for j, col_name in enumerate(df.columns):
            with header_cols[j + 1]:
                st.markdown(f'<span class="rules-table-header">{col_name}</span>', unsafe_allow_html=True)

        # Render each record row with radio button in first column (bright white)
        for i in range(len(df)):
            row_cols = st.columns(col_widths)
            with row_cols[0]:
                if st.button(
                    "🔘" if i == st.session_state.selected_rule_idx else "⚪",
                    key=f"select_row_{i}",
                    use_container_width=True,
                ):
                    # Store selected record and navigate to detail page
                    st.session_state.selected_rule_idx = i
                    st.session_state.selected_rule_record = df.iloc[i].to_dict()
                    navigate("rule_detail")
                    st.rerun()
            for j, col_name in enumerate(df.columns):
                with row_cols[j + 1]:
                    st.markdown(f'<span class="rules-table-cell">{df.iloc[i][col_name]}</span>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("⬅ Back to DQ Agent", key="back_dq_feedback"):
        navigate("dq_agent")
        st.rerun()


# ── Page: Rule Detail (Feedback) ───────────────────────────────────────────
def page_rule_detail():
    st.markdown('<p class="launch-title">Rule Feedback</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="launch-sub">Review the selected rule and provide feedback</p>',
        unsafe_allow_html=True,
    )

    record = st.session_state.get("selected_rule_record", {})
    if not record:
        st.warning("No rule selected. Please go back and select a rule.")
    else:
        # Display pre-filled immutable text fields for each column
        for col_name, col_value in record.items():
            st.text_input(f"{col_name}", value=str(col_value), disabled=True, key=f"detail_{col_name}")

        st.markdown("---")

        # Feedback text input
        feedback = st.text_input("Feedback", value="", key="feedback_input")

        # Modify and Delete buttons
        col1, col2 = st.columns(2, gap="large")
        with col1:
            if st.button("Modify", key="btn_modify"):
                rule_id = str(record.get("rule_id", ""))
                job_params = {
                    "rule_id": rule_id,
                    "feedback": feedback,
                    "modify/delete": "modify",
                }
                try:
                    w = WorkspaceClient()
                    run = w.jobs.run_now(
                        job_id=1038372772557356,
                        notebook_params=job_params,
                    )
                    st.success(f"Modify job triggered! Run ID: {run.run_id}")
                except Exception as e:
                    st.error(f"Failed to trigger job: {e}")
        with col2:
            if st.button("Delete", key="btn_delete"):
                rule_id = str(record.get("rule_id", ""))
                job_params = {
                    "rule_id": rule_id,
                    "feedback": feedback,
                    "modify/delete": "delete",
                }
                try:
                    w = WorkspaceClient()
                    run = w.jobs.run_now(
                        job_id=1038372772557356,
                        notebook_params=job_params,
                    )
                    st.success(f"Delete job triggered! Run ID: {run.run_id}")
                except Exception as e:
                    st.error(f"Failed to trigger job: {e}")

    st.markdown("---")
    if st.button("⬅ Back to Feedback Rules", key="back_feedback_from_detail"):
        navigate("feedback_rules")
        st.rerun()


# ── Router ────────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    page_home()
elif st.session_state.page == "dq_agent":
    page_dq_agent()
elif st.session_state.page == "generate_dq_rules":
    page_generate_dq_rules()
elif st.session_state.page == "apply_dq_rules":
    page_apply_dq_rules()
elif st.session_state.page == "feedback_rules":
    page_feedback_rules()
elif st.session_state.page == "rule_detail":
    page_rule_detail()
else:
    page_home()
