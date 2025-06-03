import streamlit as st
import json
import os
from datetime import datetime

PROJECTS_FILE = "projects.json"
COMMENTS_FILE = "comments.json"

# Load or initialize project data
projects = json.load(open(PROJECTS_FILE)) if os.path.exists(PROJECTS_FILE) else []

st.set_page_config(page_title="Smart Project Tracker", layout="wide")
st.markdown("<h1 style='color:#333;'>📋 Smart Project Tracker Portal</h1>", unsafe_allow_html=True)

# Add new project form
st.markdown("### ➕ Create a New Project")
with st.form("new_project_form"):
    title = st.text_input("Project Title")
    owner = st.text_input("Owner Name")
    team_input = st.text_input("Project Team (comma-separated)")
    target = st.text_input("Target Completion (e.g., Q3 2025)")
    status = st.selectbox("Status", ["OK", "Good", "Poor"])
    confirmed = st.radio("Confirmed?", ["Yes", "No"])
    category = st.selectbox("Project Category", ["Team Projects", "Active Projects", "Pipeline", "Non-MAS Projects"])
    priority = None
    if category == "Pipeline":
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    notes = st.text_area("Notes")
    bottlenecks = st.text_area("Bottlenecks or Concerns")
    password = st.text_input("Password to manage this project", type="password")

    st.markdown("#### Subtasks")
    num_tasks = st.number_input("Number of Subtasks", min_value=1, max_value=20, value=1)
    subtasks = []
    for i in range(int(num_tasks)):
        name = st.text_input(f"Subtask {i+1} Name", key=f"task_name_{i}")
        due = st.text_input(f"Subtask {i+1} Target Date", key=f"task_due_{i}")
        subtasks.append({"name": name, "progress": 0, "target": due})

    submit = st.form_submit_button("Save Project")
    if submit and title and owner and password:
        team = [t.strip() for t in team_input.split(",") if t.strip()]
        project = {
            "title": title,
            "owner": owner,
            "team": team,
            "target": target,
            "status": status,
            "confirmed": confirmed == "Yes",
            "category": category,
            "priority": priority,
            "notes": notes,
            "bottlenecks": bottlenecks,
            "password": password,
            "subtasks": subtasks
        }
        projects.append(project)
        with open(PROJECTS_FILE, "w") as f:
            json.dump(projects, f, indent=2)
        st.success("✅ Project saved successfully!")

# Display projects
if not projects:
    st.markdown("😕 <i>No projects yet. Add one above.</i>", unsafe_allow_html=True)
else:
    for proj in projects:
        st.markdown(f"<h3 style='margin-top:40px;'>🔹 {proj['title']}</h3>", unsafe_allow_html=True)
        st.write(f"👤 Owner: {proj['owner']}")
        st.write(f"👥 Team: {', '.join(proj.get('team', [])) if proj.get('team') else '—'}")
        st.write(f"📅 Target: {proj['target']} | ✅ Confirmed: {'Yes' if proj['confirmed'] else 'No'}")
        st.write(f"🟢 Status: {proj.get('status', '—')}")
        if proj.get("category") == "Pipeline":
            st.write(f"⚠️ Priority: {proj.get('priority', '—')}")
        st.write(f"📝 Notes: {proj.get('notes', '')}")
        st.write(f"🛠️ Bottlenecks: {proj.get('bottlenecks', '')}")
        
        # Subtask progress
        if proj.get("subtasks"):
            st.markdown("##### 📌 Subtasks")
            total_progress = 0
            for task in proj["subtasks"]:
                st.markdown(f"- **{task['name']}** (Due: {task['target']})")
                pct = task.get("progress", 0)
                st.progress(pct / 100)
                total_progress += pct
            overall = total_progress / len(proj["subtasks"])
            st.write(f"**Overall Progress:** {overall:.0f}%")
            st.progress(overall / 100)
        st.markdown("---")
