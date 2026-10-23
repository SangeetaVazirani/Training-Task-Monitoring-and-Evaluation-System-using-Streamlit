

import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Training Monitoring and Evaluation",
    page_icon="🎯",
    layout="wide"
)

st.title("Training Monitoring and Evaluation System")
st.caption("Participant Task Monitoring and Performance Assessment")

st.divider()

# Login selection
login_type = st.selectbox(
    "Select Login Type",
    [
        "Participant Login",
        "Lead Master Trainer Login"
    ]
)

# --------------------------------------------------
# PARTICIPANT LOGIN
# --------------------------------------------------

if login_type == "Participant Login":

    st.header("Participant Login")

    with st.form("participant_form"):

        participant_name = st.text_input("Participant Name")
        roll_no = st.text_input("Roll No")

        training_day = st.number_input(
            "Training Day",
            min_value=1,
            step=1
        )

        training_date = st.date_input(
            "Training Date",
            value=date.today()
        )

        trade = st.selectbox(
            "Trade",
            [
                "Electronics Mechanic",
                "Electrician",
                "Other"
            ]
        )

        submitted = st.form_submit_button(
            "View My Tasks",
            use_container_width=True
        )

    if submitted:
        if not participant_name.strip() or not roll_no.strip():
            st.error("Please enter Participant Name and Roll No.")
        else:
            st.success("Participant details entered successfully.")

            st.subheader("Task Status")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(
                    "GREEN - Completed",
                    use_container_width=True
                ):
                    st.session_state["task_status"] = "Completed"

            with col2:
                if st.button(
                    "RED - Need Help",
                    use_container_width=True
                ):
                    st.session_state["task_status"] = "Need Help"

            with col3:
                if st.button(
                    "YELLOW - In Progress",
                    use_container_width=True
                ):
                    st.session_state["task_status"] = "In Progress"

            if "task_status" in st.session_state:
                st.info(
                    "Current task status: "
                    + st.session_state["task_status"]
                )

# --------------------------------------------------
# LEAD MASTER TRAINER LOGIN
# --------------------------------------------------

elif login_type == "Lead Master Trainer Login":

    st.header("Lead Master Trainer Login")

    st.subheader("Task Assignment and Evaluation")

    with st.form("evaluation_form"):

        st.markdown("### Participant Details")

        participant_name = st.text_input("Participant Name")
        roll_no = st.text_input("Roll No")

        trade = st.selectbox(
            "Trade",
            [
                "Electronics Mechanic",
                "Electrician",
                "Other"
            ],
            key="trainer_trade"
        )

        st.markdown("### Training and Task Details")

        training_day = st.number_input(
            "Day of Training",
            min_value=1,
            step=1,
            key="trainer_day"
        )

        training_date = st.date_input(
            "Training Date",
            value=date.today(),
            key="trainer_date"
        )

        task_details = st.text_area(
            "Details of Task Assigned",
            placeholder="Enter practical task, instructions and expected outcome..."
        )

        st.markdown("### Performance Evaluation")

        st.caption(
            "Enter the marks awarded for each criterion. "
            "The total will be calculated out of 60."
        )

        c1, c2 = st.columns(2)

        with c1:
            housekeeping = st.number_input(
                "Workplace housekeeping (out of 10)",
                min_value=0,
                max_value=10,
                value=0
            )

            safety = st.number_input(
                "Safety consciousness (out of 10)",
                min_value=0,
                max_value=10,
                value=0
            )

            materials = st.number_input(
                "Economic use of materials (out of 5)",
                min_value=0,
                max_value=5,
                value=0
            )

            knowledge = st.number_input(
                "Application of knowledge (out of 10)",
                min_value=0,
                max_value=10,
                value=0
            )

        with c2:
            tools = st.number_input(
                "Skills to handle tools and equipment (out of 10)",
                min_value=0,
                max_value=10,
                value=0
            )

            speed = st.number_input(
                "Speed of doing work (out of 5)",
                min_value=0,
                max_value=5,
                value=0
            )

            workmanship = st.number_input(
                "Quality in workmanship (out of 10)",
                min_value=0,
                max_value=10,
                value=0
            )

        total = (
            housekeeping
            + safety
            + materials
            + knowledge
            + tools
            + speed
            + workmanship
        )

        st.divider()

        st.metric(
            label="TOTAL MARKS",
            value=f"{total} / 60",
            delta=f"{(total / 60) * 100:.1f}%"
        )

        remarks = st.text_area(
            "Lead Master Trainer Remarks",
            placeholder="Enter strengths, areas for improvement, or feedback..."
        )

        save_evaluation = st.form_submit_button(
            "Submit Evaluation",
            use_container_width=True
        )

    if save_evaluation:
        if not participant_name.strip() or not roll_no.strip():
            st.error("Please enter Participant Name and Roll No.")
        elif not task_details.strip():
            st.error("Please enter the task details.")
        else:
            st.success("Evaluation calculated successfully.")

            st.write("### Evaluation Summary")

            st.write(f"**Participant:** {participant_name}")
            st.write(f"**Roll No:** {roll_no}")
            st.write(f"**Trade:** {trade}")
            st.write(f"**Training Day:** {training_day}")
            st.write(f"**Training Date:** {training_date}")
            st.write(f"**Task:** {task_details}")
            st.write(f"**Workplace housekeeping:** {housekeeping}/10")
            st.write(f"**Safety consciousness:** {safety}/10")
            st.write(f"**Economic use of materials:** {materials}/5")
            st.write(f"**Application of knowledge:** {knowledge}/10")
            st.write(f"**Skills to handle tools and equipment:** {tools}/10")
            st.write(f"**Speed of doing work:** {speed}/5")
            st.write(f"**Quality in workmanship:** {workmanship}/10")

            st.subheader(f"Final Score: {total}/60")
            st.write(f"**Trainer Remarks:** {remarks}")

st.divider()

st.caption(
    "Training Monitoring and Evaluation System | Initial Version"
)
