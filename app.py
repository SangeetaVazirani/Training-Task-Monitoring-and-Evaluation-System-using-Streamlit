
import streamlit as st

st.set_page_config(
    page_title="Training Task Monitor",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Training Task Monitoring and Evaluation System")
st.write("Welcome to the Training Task Monitoring and Evaluation System.")

st.divider()

role = st.selectbox(
    "Select Login Type",
    ["Participant Login", "Trainer Login"]
)

if role == "Participant Login":
    st.subheader("Participant Portal")

    name = st.text_input("Participant Name")
    roll_no = st.text_input("Roll Number")
    training_day = st.number_input(
        "Training Day", min_value=1, step=1
    )

    st.info("Your assigned tasks will appear here.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("🟢 Green - Task Completed",
                  use_container_width=True)

    with col2:
        st.button("🔴 Red - Need Help",
                  use_container_width=True)

    with col3:
        st.button("🟡 Yellow - Still Working",
                  use_container_width=True)

elif role == "Trainer Login":
    st.subheader("Trainer Portal")
    st.info("Task assignment and participant evaluation will be added next.")

st.divider()
st.caption("Training Task Monitor | Initial Prototype")
