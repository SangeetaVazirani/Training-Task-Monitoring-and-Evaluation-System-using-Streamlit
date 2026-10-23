
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
from io import BytesIO

st.set_page_config(
    page_title="Training Monitoring and Evaluation",
    page_icon="🎯",
    layout="wide"
)

DB_FILE = "training_records.db"

# ---------------- DATABASE ----------------

def get_connection():
    return sqlite3.connect(DB_FILE)

def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trainer_name TEXT,
                training_day INTEGER,
                training_date TEXT,
                trade TEXT,
                assigned_roll_no TEXT,
                task_details TEXT,
                created_at TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_name TEXT,
                roll_no TEXT,
                training_day INTEGER,
                training_date TEXT,
                trade TEXT,
                task_id INTEGER,
                task_details TEXT,
                housekeeping INTEGER,
                safety INTEGER,
                materials INTEGER,
                knowledge INTEGER,
                tools INTEGER,
                speed INTEGER,
                workmanship INTEGER,
                total INTEGER,
                trainer_remarks TEXT,
                evaluated_by TEXT,
                evaluated_at TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS participant_status (
                status_id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_name TEXT,
                roll_no TEXT,
                training_day INTEGER,
                training_date TEXT,
                trade TEXT,
                task_id INTEGER,
                status TEXT,
                updated_at TEXT
            )
        """)

initialize_database()

TRADES = [
    "Electronic Mechanic",
    "Electrician",
    "COPA"
    "Welder"
    "Fitter"
    "Machinist"
]

def save_task(trainer, day, task_date, trade, roll, details):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO tasks (
                trainer_name, training_day, training_date,
                trade, assigned_roll_no, task_details, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            trainer, day, str(task_date), trade, roll.strip(),
            details.strip(), datetime.now().isoformat(timespec="seconds")
        ))

def get_tasks(day, trade, roll_no=None):
    with get_connection() as conn:
        if roll_no:
            return pd.read_sql_query("""
                SELECT * FROM tasks
                WHERE training_day = ? AND trade = ?
                AND (assigned_roll_no = '' OR assigned_roll_no = ?)
                ORDER BY task_id DESC
            """, conn, params=(day, trade, roll_no.strip()))

        return pd.read_sql_query("""
            SELECT * FROM tasks
            WHERE training_day = ? AND trade = ?
            ORDER BY task_id DESC
        """, conn, params=(day, trade))

def save_status(name, roll, day, task_date, trade, task_id, status):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO participant_status (
                participant_name, roll_no, training_day,
                training_date, trade, task_id, status, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, roll, day, str(task_date), trade,
            task_id, status,
            datetime.now().isoformat(timespec="seconds")
        ))

def save_evaluation(data):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO evaluations (
                participant_name, roll_no, training_day,
                training_date, trade, task_id, task_details,
                housekeeping, safety, materials, knowledge,
                tools, speed, workmanship, total,
                trainer_remarks, evaluated_by, evaluated_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, data)

def make_excel():
    output = BytesIO()

    with get_connection() as conn:
        tasks = pd.read_sql_query(
            "SELECT * FROM tasks ORDER BY task_id", conn
        )
        marks = pd.read_sql_query(
            "SELECT * FROM evaluations ORDER BY evaluation_id", conn
        )
        statuses = pd.read_sql_query(
            "SELECT * FROM participant_status ORDER BY status_id", conn
        )

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        tasks.to_excel(writer, sheet_name="Task Assignments", index=False)
        marks.to_excel(writer, sheet_name="Performance Marks", index=False)
        statuses.to_excel(writer, sheet_name="Participant Status", index=False)

    output.seek(0)
    return output

# ---------------- APPLICATION ----------------

st.title("🎯 Training Monitoring and Evaluation System")
st.caption("Participant Task Monitoring | Lead Master Trainer Assessment")
st.divider()

login_type = st.selectbox(
    "Select Login Type",
    ["Participant Login", "Lead Master Trainer Login"]
)

# ==================================================
# PARTICIPANT PORTAL
# ==================================================

if login_type == "Participant Login":

    st.header("Participant Login")

    with st.form("participant_details"):
        name = st.text_input("Participant Name")
        roll = st.text_input("Roll No")
        day = st.number_input("Training Day", min_value=1, step=1)
        training_date = st.date_input("Training Date", value=date.today())
        trade = st.selectbox("Trade", TRADES)

        view_tasks = st.form_submit_button("View Assigned Tasks")

    if view_tasks:
        if not name.strip() or not roll.strip():
            st.error("Please enter Participant Name and Roll No.")
        else:
            st.session_state["participant"] = {
                "name": name.strip(),
                "roll": roll.strip(),
                "day": int(day),
                "date": training_date,
                "trade": trade
            }

    participant = st.session_state.get("participant")

    if participant:
        st.subheader("My Assigned Tasks")

        task_list = get_tasks(
            participant["day"],
            participant["trade"],
            participant["roll"]
        )

        if task_list.empty:
            st.info(
                "No tasks have been assigned for this training day "
                "and trade yet."
            )
        else:
            for _, task in task_list.iterrows():
                with st.container(border=True):
                    st.markdown(f"### Task {int(task['task_id'])}")
                    st.write(task["task_details"])
                    st.caption(
                        f"Training Day: {task['training_day']} | "
                        f"Date: {task['training_date']} | "
                        f"Trade: {task['trade']}"
                    )

                    task_id = int(task["task_id"])

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        if st.button(
                            "🟢 Green - Completed",
                            key=f"green_{task_id}",
                            use_container_width=True
                        ):
                            save_status(
                                participant["name"], participant["roll"],
                                participant["day"], participant["date"],
                                participant["trade"], task_id, "Completed"
                            )
                            st.success("Completion status recorded.")

                    with c2:
                        if st.button(
                            "🔴 Red - Need Help",
                            key=f"red_{task_id}",
                            use_container_width=True
                        ):
                            save_status(
                                participant["name"], participant["roll"],
                                participant["day"], participant["date"],
                                participant["trade"], task_id, "Need Help"
                            )
                            st.warning("Help request recorded.")

                    with c3:
                        if st.button(
                            "🟡 Yellow - In Progress",
                            key=f"yellow_{task_id}",
                            use_container_width=True
                        ):
                            save_status(
                                participant["name"], participant["roll"],
                                participant["day"], participant["date"],
                                participant["trade"], task_id, "In Progress"
                            )
                            st.info("Progress status recorded.")

# ==================================================
# LEAD MASTER TRAINER PORTAL
# ==================================================

elif login_type == "Lead Master Trainer Login":

    st.header("Lead Master Trainer Login")

    tab1, tab2, tab3 = st.tabs([
        "Assign Task",
        "Evaluate Participant",
        "Excel Records"
    ])

    # ---------------- ASSIGN TASK ----------------

    with tab1:
        st.subheader("Assign Practical Task")

        with st.form("assign_task_form"):
            trainer_name = st.text_input("Lead Master Trainer Name")

            task_day = st.number_input(
                "Day of Training", min_value=1, step=1
            )

            task_date = st.date_input(
                "Training Date", value=date.today(), key="task_date"
            )

            task_trade = st.selectbox(
                "Trade", TRADES, key="task_trade"
            )

            assignment_type = st.radio(
                "Assign Task To",
                ["Entire batch", "Individual participant"]
            )

            assigned_roll = ""
            if assignment_type == "Individual participant":
                assigned_roll = st.text_input(
                    "Participant Roll No"
                )

            task_details = st.text_area(
                "Details of Task Assigned",
                placeholder=(
                    "Example: Assemble the water-level monitoring "
                    "circuit, check the connections, test both levels "
                    "and demonstrate the buzzer operation."
                ),
                height=150
            )

            assign = st.form_submit_button(
                "Publish Task",
                use_container_width=True
            )

        if assign:
            if not trainer_name.strip() or not task_details.strip():
                st.error("Enter the trainer name and task details.")
            elif (
                assignment_type == "Individual participant"
                and not assigned_roll.strip()
            ):
                st.error("Enter the participant Roll No.")
            else:
                save_task(
                    trainer_name, int(task_day), task_date,
                    task_trade, assigned_roll, task_details
                )
                st.success(
                    "Task published successfully. It is now available "
                    "in the matching participant portal."
                )

        st.markdown("### Previously Assigned Tasks")
        all_tasks = None

        with get_connection() as conn:
            all_tasks = pd.read_sql_query(
                "SELECT * FROM tasks ORDER BY task_id DESC", conn
            )

        if all_tasks.empty:
            st.info("No tasks have been assigned yet.")
        else:
            st.dataframe(
                all_tasks[[
                    "task_id", "training_day", "training_date",
                    "trade", "assigned_roll_no", "task_details"
                ]],
                use_container_width=True,
                hide_index=True
            )

    # ---------------- EVALUATE PARTICIPANT ----------------

    with tab2:
        st.subheader("Participant Performance Evaluation")

        with get_connection() as conn:
            available_tasks = pd.read_sql_query(
                "SELECT * FROM tasks ORDER BY task_id DESC", conn
            )

        if available_tasks.empty:
            st.warning("Please assign a task before evaluating a participant.")
        else:
            task_options = {
                f"Task {int(row['task_id'])} | Day {row['training_day']} | "
                f"{row['trade']} | {str(row['task_details'])[:65]}":
                row
                for _, row in available_tasks.iterrows()
            }

            selected_task_label = st.selectbox(
                "Select Assigned Task",
                list(task_options.keys())
            )
            selected_task = task_options[selected_task_label]

            with st.form("evaluation_form"):
                st.markdown("### Participant Details")

                p_name = st.text_input("Participant Name")
                p_roll = st.text_input("Roll No")

                p_day = st.number_input(
                    "Day of Training",
                    min_value=1,
                    value=int(selected_task["training_day"]),
                    step=1
                )

                p_date = st.date_input(
                    "Training Date", value=date.today(),
                    key="evaluation_date"
                )

                p_trade = st.selectbox(
                    "Trade",
                    TRADES,
                    index=TRADES.index(selected_task["trade"])
                    if selected_task["trade"] in TRADES else 0,
                    key="evaluation_trade"
                )

                st.text_area(
                    "Assigned Task Details",
                    value=selected_task["task_details"],
                    disabled=True
                )

                st.markdown("### Marks Awarded")

                c1, c2 = st.columns(2)

                with c1:
                    housekeeping = st.number_input(
                        "Workplace housekeeping (out of 10)",
                        0, 10, 0
                    )
                    safety = st.number_input(
                        "Safety consciousness (out of 10)",
                        0, 10, 0
                    )
                    materials = st.number_input(
                        "Economic use of materials (out of 5)",
                        0, 5, 0
                    )
                    knowledge = st.number_input(
                        "Application of knowledge (out of 10)",
                        0, 10, 0
                    )

                with c2:
                    tools = st.number_input(
                        "Skills to handle tools and equipment (out of 10)",
                        0, 10, 0
                    )
                    speed = st.number_input(
                        "Speed of doing work (out of 5)",
                        0, 5, 0
                    )
                    workmanship = st.number_input(
                        "Quality in workmanship (out of 10)",
                        0, 10, 0
                    )

                total = (
                    housekeeping + safety + materials + knowledge
                    + tools + speed + workmanship
                )

                st.metric(
                    "Total Marks",
                    f"{total} / 60",
                    f"{total / 60 * 100:.1f}%"
                )

                remarks = st.text_area("Lead Master Trainer Remarks")
                evaluator = st.text_input("Evaluated By (Lead Master Trainer)")

                submit_evaluation = st.form_submit_button(
                    "Save Evaluation",
                    use_container_width=True
                )

            if submit_evaluation:
                if not p_name.strip() or not p_roll.strip():
                    st.error("Enter participant name and roll number.")
                elif not evaluator.strip():
                    st.error("Enter the Lead Master Trainer name.")
                else:
                    save_evaluation((
                        p_name.strip(), p_roll.strip(), int(p_day),
                        str(p_date), p_trade, int(selected_task["task_id"]),
                        selected_task["task_details"],
                        int(housekeeping), int(safety), int(materials),
                        int(knowledge), int(tools), int(speed),
                        int(workmanship), int(total), remarks,
                        evaluator.strip(),
                        datetime.now().isoformat(timespec="seconds")
                    ))

                    st.success(
                        f"Evaluation saved successfully. Total: {total}/60"
                    )

    # ---------------- EXCEL EXPORT ----------------

    with tab3:
        st.subheader("Performance Records and Excel Export")

        with get_connection() as conn:
            marks_df = pd.read_sql_query(
                "SELECT * FROM evaluations ORDER BY evaluation_id DESC",
                conn
            )
            tasks_df = pd.read_sql_query(
                "SELECT * FROM tasks ORDER BY task_id DESC", conn
            )
            status_df = pd.read_sql_query(
                "SELECT * FROM participant_status ORDER BY status_id DESC",
                conn
            )

        st.metric("Evaluations Recorded", len(marks_df))
        st.metric("Tasks Assigned", len(tasks_df))

        if not marks_df.empty:
            st.markdown("### Marks Overview")
            st.dataframe(marks_df, use_container_width=True, hide_index=True)
        else:
            st.info("No evaluation records have been saved yet.")

        excel_file = make_excel()

        st.download_button(
            "📥 Download All Records as Excel",
            data=excel_file,
            file_name=f"Training_Performance_{date.today()}.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True
        )

st.divider()
st.caption("Training Monitoring and Evaluation System")
