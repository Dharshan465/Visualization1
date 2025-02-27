import streamlit as st
import pandas as pd
import altair as alt

# Streamlit App Title
st.title("📊 Student Performance Analysis")

# File Upload
uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Extract roll number and subject columns
    roll_numbers = df.iloc[:, 1]  # Assuming Roll No is in the second column
    subjects = df.columns[2:]     # Subject codes start from the third column

    # Convert all subject columns to numeric (force conversion)
    df[subjects] = df[subjects].apply(pd.to_numeric, errors="coerce")

    # Create a Pass/Fail DataFrame
    pass_fail_df = df.copy()
    pass_fail_df[subjects] = pass_fail_df[subjects].map(lambda x: 'Pass' if x >= 45 else 'Fail')

    # Overall Pass/Fail Count
    df["Total Passed Subjects"] = (df[subjects] >= 45).sum(axis=1)
    df["Final Result"] = df["Total Passed Subjects"].apply(lambda x: "Pass" if x == len(subjects) else "Fail")

    # Count of Passed and Failed Students
    overall_pass_fail = df["Final Result"].value_counts().reset_index()
    overall_pass_fail.columns = ["Result", "Count"]

    # Subject-wise Pass/Fail Count
    subject_pass_fail = pass_fail_df[subjects].apply(lambda col: col.value_counts()).fillna(0)

    # 📊 Overall Pass/Fail Bar Chart
    st.subheader("📈 Overall Pass vs Fail Count")

    # Define Colors (Light Green & Light Red)
    color_scale = alt.Scale(domain=["Pass", "Fail"], range=["lightgreen", "lightcoral"])

    # Create Bar Chart
    chart1 = alt.Chart(overall_pass_fail).mark_bar(width=80).encode(
        x=alt.X("Result:N", title="Final Result", axis=alt.Axis(labelFontSize=14, titleFontSize=16)),  # Bigger labels
        y=alt.Y("Count:Q", title="Student Count", axis=alt.Axis(labelFontSize=14, titleFontSize=16)),  # Bigger axis text
        color=alt.Color("Result:N", scale=color_scale, legend=alt.Legend(title="Result", labelFontSize=14, titleFontSize=16)),
    ).properties(title=alt.TitleParams("", fontSize=18, fontWeight="bold"))

    # Add Text Labels Above Bars
    text = chart1.mark_text(
        align="center",
        baseline="bottom",
        dy=-5,  # Position above bars
        fontSize=20,  # Increased text size
        fontWeight="bold",
        color="black"
    ).encode(text="Count:Q")

    # Render Chart
    st.altair_chart(chart1 + text, use_container_width=True)


    # 📚 Subject-wise Pass/Fail Grouped Bar Chart
    st.subheader("📊 Subject-wise Pass/Fail Count")

    # Reshape Data for Altair
    subject_df = subject_pass_fail.T.reset_index().melt(id_vars="index", var_name="Result", value_name="Count")

    # Define Colors (Light Green & Light Red)
    color_scale = alt.Scale(domain=["Pass", "Fail"], range=["lightgreen", "lightcoral"])

    # Create Grouped Bar Chart (No Faceting)
    chart3 = alt.Chart(subject_df).mark_bar(width=30).encode(
        x=alt.X("index:N", title="Subjects", axis=alt.Axis(labelAngle=-45, labelFontSize=14, titleFontSize=16)),  # Bigger labels
        y=alt.Y("Count:Q", title="Student Count", axis=alt.Axis(labelFontSize=14, titleFontSize=16)),  # Bigger axis text
        color=alt.Color("Result:N", scale=color_scale, legend=alt.Legend(title="Result", labelFontSize=14, titleFontSize=16)),
        xOffset=alt.X("Result:N")  # Ensures bars are side by side
    ).properties(title=alt.TitleParams("", fontSize=18, fontWeight="bold"))

    # Add Text Labels Above Bars
    text = chart3.mark_text(
        align="center",
        baseline="bottom",
        dy=-5,  # Position above bars
        fontSize=20,  # Increased text size
        fontWeight="bold",
        color="black"
    ).encode(text="Count:Q")

    # Render Chart
    st.altair_chart(chart3 + text, use_container_width=True)





    # 📊 Average Marks per Subject
    st.subheader("📈 Average Marks per Subject")

    # Compute average marks
    subject_avg = df[subjects].mean().reset_index()
    subject_avg.columns = ["Subject", "Average Marks"]

    # Define a darker color palette
    subject_colors = alt.Scale(domain=subject_avg["Subject"].tolist(), range=["#4682B4", "#8B0000", "#228B22", "#FF8C00", "#6A5ACD", "#DC143C", "#2E8B57"])  # SteelBlue, DarkRed, ForestGreen, DarkOrange, SlateBlue, Crimson, SeaGreen

    # Create bar chart
    chart4 = alt.Chart(subject_avg).mark_bar(width=50).encode(
        x=alt.X("Subject:N", title="Subjects", axis=alt.Axis(labelFontSize=14, titleFontSize=16, labelAngle=-45)),
        y=alt.Y("Average Marks:Q", title="Average Marks", axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
        color=alt.Color("Subject:N", scale=subject_colors, legend=None),  # Different dark colors per subject
        tooltip=["Subject", "Average Marks"]
    ).properties(title=alt.TitleParams("", fontSize=18, fontWeight="bold"))

    # Add text labels
    text4 = chart4.mark_text(
        align="center",
        baseline="bottom",
        dy=-5,  # Moves text above bars
        fontSize=16,
        fontWeight="bold",
        color="black"
    ).encode(text="Average Marks:Q")

    # Render chart
    st.altair_chart(chart4 + text4, use_container_width=True)


    # 📉 Number of Subjects Failed per Student
    st.subheader("📉 Number of Subjects failed per student")

    # Compute fail distribution
    df["Subjects Failed"] = (df[subjects] < 45).sum(axis=1)
    fail_distribution = df["Subjects Failed"].value_counts().reset_index()
    fail_distribution.columns = ["Subjects Failed", "Count"]

    # Define a darker color palette for fail bars
    fail_colors = alt.Scale(domain=fail_distribution["Subjects Failed"].tolist(), range=["#B22222", "lightgreen", "#FF4500", "#A52A2A", "#CD5C5C", "#800000", "#DC143C"])  # FireBrick, DarkRed, OrangeRed, Brown, IndianRed, Maroon, Crimson

    # Create bar chart
    chart6 = alt.Chart(fail_distribution).mark_bar(width=50).encode(
        x=alt.X("Subjects Failed:O", title="Number of Subjects Failed", axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
        y=alt.Y("Count:Q", title="Number of Students", axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
        color=alt.Color("Subjects Failed:N", scale=fail_colors, legend=None),  # Different dark colors per bar
        tooltip=["Subjects Failed", "Count"]
    ).properties(title=alt.TitleParams("", fontSize=18, fontWeight="bold"))

    # Add text labels
    text6 = chart6.mark_text(
        align="center",
        baseline="bottom",
        dy=-5,  # Moves text above bars
        fontSize=16,
        fontWeight="bold",
        color="black"
    ).encode(text="Count:Q")

    # Render chart
    st.altair_chart(chart6 + text6, use_container_width=True)



   
