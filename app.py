
import streamlit as st
import json
import os
from datetime import datetime

PROJECTS_FILE = "projects.json"
COMMENTS_FILE = "comments.json"

if os.path.exists(PROJECTS_FILE):
    with open(PROJECTS_FILE, "r") as f:
        projects = json.load(f)
else:
    projects = []

if os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, "r") as f:
        comments_db = json.load(f)
else:
    comments_db = {}

st.set_page_config(page_title="Smart Project Tracker", layout="wide")
st.title("📋 Smart Project Tracker Portal")

edit_index = st.session_state.get("edit_index", None)

owners = sorted(set(proj['owner'] for proj in projects if 'owner' in proj))
if not owners:
    owners = []
selected_owner = st.selectbox("🔍 Filter by Owner", ["All"] + owners)

filtered_projects = [p for p in projects if selected_owner == "All" or p['owner'] == selected_owner]

# Temporary session variable for password-validated edit
if "edit_unlocked_index" not in st.session_state:
    st.session_state["edit_unlocked_index"] = None

for idx, project in enumerate(filtered_projects):
    st.markdown(f"### 📁 {project['title']}")
    st.markdown(f"👤 **Owner:** {project['owner']} &nbsp;&nbsp; 🎯 **Target Period:** {project['target_period']}")
    st.markdown(f"📝 **Notes:** {project['notes']}")
    st.markdown(f"🔍 **Details:** {project['details']}")

    st.markdown("#### 📌 Subtasks")
    total = 0
    for tidx, task in enumerate(project['subtasks']):
        st.write(f"**{task['name']}** (Due: {task['target_date']})")
        progress = st.slider("Progress", 0, 100, value=task['progress'], key=f"prog_{idx}_{tidx}")
        project['subtasks'][tidx]['progress'] = progress
        total += progress
        st.progress(progress / 100)

    avg_progress = total / len(project['subtasks']) if project['subtasks'] else 0
    st.markdown(f"**Overall Progress:** {avg_progress:.0f}%")
    st.progress(avg_progress / 100)

    st.markdown("#### 💬 Comments")
    for cidx, c in enumerate(comments_db.get(project['title'], [])):
        with st.expander(f"🗨️ {c['user']} ({c['timestamp']})"):
            st.write(c["comment"])
            with st.form(f"del_comment_form_{idx}_{cidx}"):
                password_input = st.text_input("Enter comment password to delete", type="password", key=f"pw_{idx}_{cidx}")
                submit_delete = st.form_submit_button("Delete Comment")
                if submit_delete:
                    if password_input == c['password']:
                        comments_db[project['title']].pop(cidx)
                        with open(COMMENTS_FILE, "w") as f:
                            json.dump(comments_db, f, indent=2)
                        st.success("Comment deleted. Please refresh the page.")
                    else:
                        st.error("Incorrect password.")

    with st.form(f"form_comment_{idx}"):
        user = st.text_input("Your Name")
        comment = st.text_area("Your Comment")
        pw = st.text_input("Password to manage this comment", type="password")
        submit = st.form_submit_button("Post Comment")
        if submit and user and comment and pw:
            new_c = {
                "user": user,
                "comment": comment,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "password": pw
            }
            comments_db.setdefault(project['title'], []).append(new_c)
            with open(COMMENTS_FILE, "w") as f:
                json.dump(comments_db, f, indent=2)
            st.success("Comment posted.")

    with st.expander("🔐 Manage This Project"):
        action = st.radio("Choose an action:", ["None", "Edit", "Delete"], key=f"action_{idx}")
        pw_input = st.text_input("Enter project password", type="password", key=f"project_pw_{idx}")
        if action == "Delete" and pw_input == project["password"]:
            projects.remove(project)
            with open(PROJECTS_FILE, "w") as f:
                json.dump(projects, f, indent=2)
            st.success("Project deleted. Please refresh the page.")
            st.stop()
        elif action == "Edit" and pw_input == project["password"]:
            st.session_state["edit_unlocked_index"] = idx

    with open(PROJECTS_FILE, "w") as f:
        json.dump(projects, f, indent=2)

# Display inline edit form if password was validated
edit_idx = st.session_state.get("edit_unlocked_index")
if edit_idx is not None and edit_idx < len(projects):
    st.markdown("## ✏️ Edit Project")
    proj = projects[edit_idx]
    with st.form("edit_project_form"):
        proj["title"] = st.text_input("Project Title", value=proj["title"])
        proj["owner"] = st.text_input("Owner Name", value=proj["owner"])
        proj["target_period"] = st.text_input("Target Period", value=proj["target_period"])
        proj["notes"] = st.text_area("Notes", value=proj["notes"])
        proj["details"] = st.text_area("Full Description", value=proj["details"])
        for i, task in enumerate(proj["subtasks"]):
            task["name"] = st.text_input(f"Task Name {i+1}", value=task["name"], key=f"edit_task_name_{i}")
            date_obj = datetime.strptime(task["target_date"], "%Y-%m-%d").date()
            task["target_date"] = st.date_input(f"Target Date {i+1}", value=date_obj, key=f"edit_task_date_{i}").strftime("%Y-%m-%d")
        submit_edit = st.form_submit_button("Save Changes")
        if submit_edit:
            with open(PROJECTS_FILE, "w") as f:
                json.dump(projects, f, indent=2)
            st.success("✅ Project updated! Please manually refresh the page to see changes.")
            st.session_state["edit_unlocked_index"] = None

# Add New Project Form
st.markdown("---")
st.markdown("## ➕ Add New Project")
with st.form("new_project_form"):
    title = st.text_input("Project Title")
    owner = st.text_input("Owner Name")
    target_period = st.text_input("Target Period (e.g., 1Q25)")
    notes = st.text_area("Notes")
    details = st.text_area("Full Description")
    pw = st.text_input("Password to manage this project", type="password")
    
    task_count = st.number_input("How many subtasks?", min_value=1, max_value=20, step=1)
    subtasks = []
    for i in range(int(task_count)):
        st.markdown(f"#### Subtask {i+1}")
        name = st.text_input(f"Task Name {i+1}", key=f"task_name_{i}")
        due = st.date_input(f"Target Date {i+1}", key=f"task_date_{i}")
        subtasks.append({"name": name, "progress": 0, "target_date": due.strftime("%Y-%m-%d")})

    
    if submit and title and owner and pw:
        new_proj = {
            "title": title,
            "owner": owner,
            "target_period": target_period,
            "notes": notes,
            "details": details,
            "password": pw,
            "subtasks": subtasks
        }
        projects.append(new_proj)
        with open(PROJECTS_FILE, "w") as f:
            json.dump(projects, f, indent=2)
        st.success("✅ Project added! Please manually refresh the page to view it.")
    pw = st.text_input("Password to manage this project", type="password")
    submit = st.form_submit_button("Create Project")
    if submit and title and owner and pw:
        new_proj = {
            "title": title,
            "owner": owner,
            "target_period": target_period,
            "notes": notes,
            "details": details,
            "password": pw,
            "subtasks": subtasks
        }
        projects.append(new_proj)
        with open(PROJECTS_FILE, "w") as f:
            json.dump(projects, f, indent=2)
        st.success("✅ Project added! Please manually refresh the page to view it.")

