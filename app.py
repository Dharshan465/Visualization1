import streamlit as st
import pandas as pd
import altair as alt

# Load Data
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file, sheet_name="UG")  # Ensure UG sheet is loaded
    return df

# Pass/Fail Logic
def determine_pass_fail(df):
    df["Pass"] = df["GRADE"] != "U"
    student_pass_fail = df.groupby("REGNO")["Pass"].all().reset_index()
    student_pass_fail["Status"] = student_pass_fail["Pass"].map({True: "Pass", False: "Fail"})
    return student_pass_fail

# Fail Categories
# Fail Categories
def categorize_failures(df):
    fail_df = df[df["GRADE"] == "U"].copy()

    # Ensure ESEM is treated as a string (to avoid NaN issues)
    fail_df["ESEM"] = fail_df["ESEM"].astype(str).str.strip().str.upper()

    # Assign fail categories directly based on ESEM values
    fail_df["Fail Type"] = fail_df["ESEM"].map({
        "P": "Prevention",
        "M": "Malpractice",
        "A": "Absent"
    }).fillna("Attempted")  # Default to "Attempted" if not P, M, or A

    return fail_df



# Grade Distribution
def grade_distribution(df):
    grade_order = ["O", "A+", "A", "B+", "B", "C", "U"]  # Ensuring correct order
    grade_dist = df.groupby("GRADE")["REGNO"].nunique().reset_index().rename(columns={"REGNO": "Count"})
    grade_dist["GRADE"] = pd.Categorical(grade_dist["GRADE"], categories=grade_order, ordered=True)
    return grade_dist.sort_values("GRADE")

# Subjects Failed per Student
def subjects_failed(df):
    fail_counts = df[df["GRADE"] == "U"].groupby("REGNO")["SUBCODE"].count().value_counts().reset_index()
    fail_counts.columns = ["Subjects Failed", "Student Count"]
    return fail_counts

# Average Marks Calculation
def avg_marks(df):
    df[["SESMARK", "ESEM", "TOTMARK"]] = df[["SESMARK", "ESEM", "TOTMARK"]].apply(pd.to_numeric, errors="coerce")
    avg_data = df[["SESMARK", "ESEM", "TOTMARK"]].mean().reset_index()
    avg_data.columns = ["Mark Type", "Average Marks"]
    return avg_data

# Chart: Pass/Fail Count
# Chart: Pass/Fail Count
def pass_fail_chart(df):
    pass_fail_counts = df["Status"].value_counts().reset_index()
    pass_fail_counts.columns = ["Status", "Count"]

    # Enforce correct order manually
    pass_fail_counts = pass_fail_counts.set_index("Status").reindex(["Pass", "Fail"], fill_value=0).reset_index()

    total = pass_fail_counts["Count"].sum()
    pass_fail_counts["Percentage"] = pass_fail_counts["Count"] / total * 100  # Calculate percentage

    chart = alt.Chart(pass_fail_counts).mark_bar().encode(
        x=alt.X("Status:N", title="Pass/Fail", sort=["Pass", "Fail"]),  # Explicit sorting
        y=alt.Y("Count:Q", title="Number of Students"),
        color=alt.Color("Status:N", scale=alt.Scale(domain=["Pass", "Fail"], range=["lightgreen", "lightcoral"])),
        tooltip=["Status", "Count", alt.Tooltip("Percentage:Q", title="Percentage", format=".1f")]
    ).properties(title=f"Pass/Fail Count (Total: {total})")

    text = chart.mark_text(dy=-10, fontSize=14, fontWeight="bold").encode(text="Count")

    return (chart + text)

# Chart: Fail Categories
def fail_categories_chart(df):
    # Define all possible categories
    fail_types = ["Prevention", "Malpractice", "Absent", "Attempted"]

    # Count fail types
    fail_categories = df["Fail Type"].value_counts().reindex(fail_types, fill_value=0).reset_index()
    fail_categories.columns = ["Category", "Count"]

    # Create the chart
    chart = alt.Chart(fail_categories).mark_bar().encode(
        x=alt.X("Category:N", title="Fail Category", sort=fail_types),
        y=alt.Y("Count:Q", title="Number of Students"),
        color=alt.Color("Category:N"),
        tooltip=["Category", "Count"]
    ).properties(title="Fail Categories Breakdown")

    text = chart.mark_text(dy=-10, fontSize=14, fontWeight="bold").encode(text="Count")

    return (chart + text)

# Chart: Average Marks
def avg_marks_chart(df):
    # Enforce correct order
    order = ["SESMARK", "ESEM", "TOTMARK"]
    df["Mark Type"] = pd.Categorical(df["Mark Type"], categories=order, ordered=True)

    chart = alt.Chart(df.sort_values("Mark Type")).mark_bar().encode(
        x=alt.X("Mark Type:N", title="Mark Type", 
                axis=alt.Axis(labelExpr="datum.value == 'SESMARK' ? 'Internal' : datum.value == 'ESEM' ? 'External' : 'Total'")),
        y=alt.Y("Average Marks:Q", title="Average Marks"),
        color=alt.Color("Mark Type:N", scale=alt.Scale(domain=order, range=["blue", "orange", "green"])),
        tooltip=["Mark Type", "Average Marks"]
    ).properties(title="Overall Average Marks (Internal, External, Total)")

    text = chart.mark_text(dy=-10, fontSize=14, fontWeight="bold").encode(text=alt.Text("Average Marks:Q", format=".1f"))

    return (chart + text)


# Chart: Subjects Failed Per Student
def subjects_failed_chart(df):
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Subjects Failed:N", title="Subjects Failed"),
        y=alt.Y("Student Count:Q", title="Number of Students"),
        color=alt.Color("Subjects Failed:N", scale=alt.Scale(scheme="category20")),
        tooltip=["Subjects Failed", "Student Count"]
    ).properties(title="Number of Subjects Failed Per Student")

    text = chart.mark_text(dy=-10, fontSize=14, fontWeight="bold").encode(text="Student Count")

    return (chart + text)

# Chart: Grade Distribution
def grade_distribution_chart(df):
    grade_order = ["O", "A+", "A", "B+", "B", "C", "U"]
    df["GRADE"] = pd.Categorical(df["GRADE"], categories=grade_order, ordered=True)

    chart = alt.Chart(df.sort_values("GRADE")).mark_bar().encode(
        x=alt.X("GRADE:N", title="Grade", sort=grade_order),  # Explicit sorting
        y=alt.Y("Count:Q", title="Number of Students"),
        color=alt.Color("GRADE:N", scale=alt.Scale(domain=grade_order, scheme="category20")),
        tooltip=["GRADE", "Count"]
    ).properties(title="Grade Distribution")

    text = chart.mark_text(dy=-10, fontSize=14, fontWeight="bold").encode(text="Count")

    return (chart + text)


DEPT_PREFIX = {
    "Aerospace": "AE", "Automobile": "AU", "Electronics Comm": "EC", "Artificial Intelligence": "AZ",
    "Information Tech": "IT", "Inst Eng": "EI", "Mech": "ME", "Production": "PR", 
    "Robotics": "RO", "Rubber and Plastics": "RP"
}

# Streamlit UI
st.title("Student Performance Analysis")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)

    # Dropdowns
    department_options = ["Overall", "Others (Open Elective)"] + sorted(df["DEPNAME"].unique())
    selected_department = st.selectbox("Select Department", department_options)

    if selected_department == "Others (Open Elective)":
        selected_branch = "All"  # Hide branch selection
        all_prefixes = tuple(DEPT_PREFIX.values())  # Get all department prefixes
        df = df[~df["SUBCODE"].str.startswith(all_prefixes)]
        subject_list = sorted(df["SUBCODE"].unique())  # Subjects only from Open Electives
    else:
        selected_branch = st.selectbox("Select Branch", ["All"] + sorted(df[df["DEPNAME"] == selected_department]["BRNAME"].unique())) if selected_department != "Overall" else "All"

        if selected_department != "Overall":
            df = df[df["DEPNAME"] == selected_department]

        if selected_branch != "All":
            df = df[df["BRNAME"] == selected_branch]

        subject_list = sorted(df["SUBCODE"].unique())

    selected_semester = st.selectbox("Select Semester", ["All", "5", "7"])

    if selected_semester != "All":
        df = df[df["SEM"] == int(selected_semester)]

    selected_subject = st.selectbox("Select Subject", ["All"] + subject_list)

    if selected_subject != "All":
        df = df[df["SUBCODE"] == selected_subject]


    # Generate Data for Charts
    pass_fail_df = determine_pass_fail(df)
    fail_df = categorize_failures(df)
    avg_marks_df = avg_marks(df)
    subjects_failed_df = subjects_failed(df)
    grade_dist_df = grade_distribution(df)

    # Display Charts
    st.subheader("1. Pass/Fail Count")
    st.altair_chart(pass_fail_chart(pass_fail_df), use_container_width=True)

    st.subheader("2. Fail Categories")
    st.altair_chart(fail_categories_chart(fail_df), use_container_width=True)

    st.subheader("3. Average Marks")
    st.altair_chart(avg_marks_chart(avg_marks_df), use_container_width=True)

    # Only show "Subjects Failed" if a subject is NOT selected
    if selected_subject == "All":
        st.subheader("4. Subjects Failed Per Student")
        st.altair_chart(subjects_failed_chart(subjects_failed_df), use_container_width=True)

    st.subheader("5. Grade Distribution")
    st.altair_chart(grade_distribution_chart(grade_dist_df), use_container_width=True)
