import streamlit as st
import json
import os
from datetime import datetime

PROJECTS_FILE = "projects.json"
COMMENTS_FILE = "comments.json"

# Load or initialize data
projects = json.load(open(PROJECTS_FILE)) if os.path.exists(PROJECTS_FILE) else []
comments_db = json.load(open(COMMENTS_FILE)) if os.path.exists(COMMENTS_FILE) else {}

st.set_page_config(page_title="Smart Project Tracker", layout="wide")
st.title("📋 Smart Project Tracker Portal")

# Setup filters and constants
CATEGORIES = ["Team Projects", "Active Projects", "Pipeline", "Non-MAS Projects"]
STATUS_OPTIONS = ["OK", "Good", "Poor"]
PRIORITY_OPTIONS = ["High", "Medium", "Low"]
owners = sorted(set(p['owner'] for p in projects if 'owner' in p))
selected_owner = st.selectbox("👤 Filter by Owner", ["All"] + owners)

# Group projects
grouped = {cat: [] for cat in CATEGORIES}
for proj in projects:
    if selected_owner == "All" or proj.get("owner") == selected_owner:
        grouped[proj.get("category", "Other")].append(proj)

# Render project cards
for category, items in grouped.items():
    if not items:
        continue
    st.subheader(f"📁 {category}")
    for idx, p in enumerate(items):
        st.markdown(f"### 🔹 {p['title']}")
        st.write(f"👤 **Owner**: {p['owner']}")
        st.write(f"👥 **Team**: {', '.join(p.get('team', [])) if p.get('team') else '—'}")
        st.write(f"📅 **Target**: {p.get('target', '—')} | ✅ **Confirmed**: {'Yes' if p.get('confirmed') else 'No'}")
        st.write(f"🟢 **Status**: {p.get('status', '—')}")
        if p.get("category") == "Pipeline":
            st.write(f"⚠️ **Priority**: {p.get('priority', '—')}")
        st.write(f"📝 **Notes**: {p.get('notes', '')}")
        st.write(f"🛠️ **Bottlenecks**: {p.get('bottlenecks', '')}")

        # Subtasks & progress
        if p.get("subtasks"):
            st.markdown("#### 📌 Subtasks")
            total = 0
            for tidx, task in enumerate(p["subtasks"]):
                st.write(f"**{task['name']}** (Due: {task['target']})")
                progress = st.slider("Progress", 0, 100, value=task['progress'], key=f"prog_{idx}_{tidx}")
                p["subtasks"][tidx]["progress"] = progress
                total += progress
                st.progress(progress / 100)
            overall = total / len(p["subtasks"])
            st.write(f"**Overall Progress:** {overall:.0f}%")
            st.progress(overall / 100)

        # Comments
        st.markdown("#### 💬 Comments")
        for cidx, c in enumerate(comments_db.get(p['title'], [])):
            st.info(f"**{c['user']}** ({c['timestamp']}): {c['comment']}")
            with st.expander("🗑️ Delete this comment"):
                pw = st.text_input("Enter password", type="password", key=f"pw_{idx}_{cidx}")
                if st.button("Delete Comment", key=f"delcom_{idx}_{cidx}"):
                    if pw == c['password']:
                        comments_db[p['title']].pop(cidx)
                        with open(COMMENTS_FILE, "w") as f:
                            json.dump(comments_db, f, indent=2)
                        st.success("Comment deleted.")
                        st.experimental_rerun()
                    else:
                        st.error("Incorrect password.")

        with st.form(f"comment_form_{idx}"):
            user = st.text_input("Your Name")
            comment = st.text_area("Your Comment")
            pw = st.text_input("Password to delete this comment", type="password")
            submit = st.form_submit_button("Post Comment")
            if submit and user and comment and pw:
                comments_db.setdefault(p['title'], []).append({
                    "user": user,
                    "comment": comment,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "password": pw
                })
                with open(COMMENTS_FILE, "w") as f:
                    json.dump(comments_db, f, indent=2)
                st.success("Comment posted.")
                st.experimental_rerun()

        # Project management
        with st.expander("🔐 Manage This Project"):
            action = st.radio("Action", ["None", "Edit", "Delete"], key=f"action_{idx}")
            pw_input = st.text_input("Enter project password", type="password", key=f"pw_proj_{idx}")
            if action == "Delete" and pw_input == p["password"]:
                projects.remove(p)
                with open(PROJECTS_FILE, "w") as f:
                    json.dump(projects, f, indent=2)
                st.success("Project deleted.")
                st.experimental_rerun()
            elif action == "Edit" and pw_input == p["password"]:
                st.info("Editing not implemented in this version. (Can be added later)")

        st.markdown("---")

# Add new project form
st.subheader("➕ Add New Project")
with st.form("new_project_form"):
    title = st.text_input("Project Title")
    owner = st.text_input("Owner Name")
    team_input = st.text_input("Project Team (comma-separated)")
    target = st.text_input("Target Completion")
    confirmed = st.radio("Confirmed?", ["Yes", "No"])
    status = st.selectbox("Project Status", STATUS_OPTIONS)
    category = st.selectbox("Project Category", CATEGORIES)
    priority = None
    if category == "Pipeline":
        priority = st.selectbox("Priority", PRIORITY_OPTIONS)
    notes = st.text_area("Notes")
    bottlenecks = st.text_area("Bottlenecks or Concerns")
    password = st.text_input("Password to manage this project", type="password")
    
    num_tasks = st.number_input("Number of Subtasks", min_value=1, max_value=10, step=1)
    subtasks = []
    for i in range(int(num_tasks)):
        name = st.text_input(f"Subtask {i+1} Name", key=f"task_name_{i}")
        due = st.text_input(f"Subtask {i+1} Target Date", key=f"task_due_{i}")
        subtasks.append({"name": name, "target": due, "progress": 0})

    submitted = st.form_submit_button("Add Project")
    if submitted and title and owner and password:
        team = [t.strip() for t in team_input.split(",") if t.strip()]
        project = {
            "title": title,
            "owner": owner,
            "team": team,
            "target": target,
            "confirmed": confirmed == "Yes",
            "status": status,
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
        st.success("✅ Project added successfully.")
        st.experimental_rerun()
