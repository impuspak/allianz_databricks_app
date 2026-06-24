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
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state for navigation ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"


def navigate(page_name: str):
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
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("Generate DQ Rules", key="gen_dq_rules"):
            navigate("generate_dq_rules")
            st.rerun()
    with col2:
        if st.button("Give Feedback for Rules", key="feedback_rules"):
            navigate("feedback_rules")
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
                    query = f"SELECT * FROM allianz_ops.dqx_schema.table_checks WHERE table_name = '{table_name}'"
                    st.info(query)
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

    # Display results with radio buttons
    if "feedback_df" in st.session_state and st.session_state.feedback_df is not None:
        df = st.session_state.feedback_df
        st.markdown("---")
        st.markdown("**Fetched Rules:**")
        options = [f"Row {i+1}" for i in range(len(df))]
        selected = st.radio("Select a rule:", options, key="rule_selection")
        selected_idx = options.index(selected)

        display_df = df.copy()
        display_df.insert(0, "Select", ["🔘" if i == selected_idx else "⚪" for i in range(len(df))])
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    if st.button("⬅ Back to DQ Agent", key="back_dq_feedback"):
        navigate("dq_agent")
        st.rerun()


# ── Router ────────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    page_home()
elif st.session_state.page == "dq_agent":
    page_dq_agent()
elif st.session_state.page == "generate_dq_rules":
    page_generate_dq_rules()
elif st.session_state.page == "feedback_rules":
    page_feedback_rules()
else:
    page_home()
