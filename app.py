import streamlit as st
import json
import os
from datetime import datetime

PROJECTS_FILE = "projects.json"
COMMENTS_FILE = "comments.json"

# Load data
projects = json.load(open(PROJECTS_FILE)) if os.path.exists(PROJECTS_FILE) else []
comments_db = json.load(open(COMMENTS_FILE)) if os.path.exists(COMMENTS_FILE) else {}

st.set_page_config(page_title="Smart Project Tracker", layout="wide")
st.title("📋 Smart Project Tracker Portal")

CATEGORIES = ["Team Projects", "Active Projects", "Pipeline", "Non-MAS Projects"]
BUSINESS_FUNCTIONS = ["MAS PM", "Index Management", "ETF Research", "Trading and Ops"]
STATUS_OPTIONS = ["OK", "Good", "Poor"]
PRIORITY_OPTIONS = ["High", "Medium", "Low"]

# Filter
owners = sorted(set(p['owner'] for p in projects if 'owner' in p))
selected_owner = st.selectbox("👤 Filter by Owner", ["All"] + owners)

# Group projects
grouped = {cat: [] for cat in CATEGORIES}
for proj in projects:
    if selected_owner == "All" or proj.get("owner") == selected_owner:
        grouped[proj.get("category", "Other")].append(proj)

# Display projects
for category, items in grouped.items():
    if not items:
        continue
    st.subheader(f"📁 {category}")
    for idx, p in enumerate(items):
        st.markdown(f"### 🔹 {p['title']}")
        st.write(f"👤 **Owner**: {p['owner']}")
        st.write(f"🏢 **Business Function**: {p.get('business_function', '—')}")
        st.write(f"👥 **Team**: {', '.join(p.get('team', [])) if p.get('team') else '—'}")
        st.write(f"📅 **Target**: {p.get('target', '—')} | ✅ **Confirmed**: {'Yes' if p.get('confirmed') else 'No'}")
        st.write(f"🟢 **Status**: {p.get('status', '—')}")
        if p.get("category") == "Pipeline":
            st.write(f"⚠️ **Priority**: {p.get('priority', '—')}")
        st.write(f"📝 **Notes**: {p.get('notes', '')}")
        st.write(f"🛠️ **Bottlenecks**: {p.get('bottlenecks', '')}")

        # Progress Bar
        st.write(f"**Progress:** {p.get('progress', 0)}%")
        p["progress"] = st.slider("📊 Project Progress", 0, 100, value=p.get("progress", 0), key=f"progress_{idx}")
        st.progress(p["progress"] / 100)
        with open(PROJECTS_FILE, "w") as f:
            json.dump(projects, f, indent=2)

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
                        st.success("Comment deleted. Please refresh.")
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
                st.success("Comment posted. Please refresh.")

        # Edit/Delete Project
        with st.expander("🔐 Manage This Project"):
            action = st.radio("Action", ["None", "Edit", "Delete"], key=f"action_{idx}")
            pw_input = st.text_input("Enter project password", type="password", key=f"pw_proj_{idx}")
            if action == "Delete" and pw_input == p["password"]:
                projects.remove(p)
                with open(PROJECTS_FILE, "w") as f:
                    json.dump(projects, f, indent=2)
                st.success("Project deleted. Please refresh.")
            elif action == "Edit" and pw_input == p["password"]:
                st.session_state["edit_mode"] = p
                st.session_state["edit_idx"] = idx
                st.success("Edit mode activated. Scroll to bottom.")
        st.markdown("---")

# Add or Edit Project
st.subheader("➕ Add or Edit Project")
edit_mode = st.session_state.get("edit_mode")
with st.form("new_project_form", clear_on_submit=not edit_mode):
    title = st.text_input("Project Title", value=edit_mode["title"] if edit_mode else "")
    owner = st.text_input("Owner Name", value=edit_mode["owner"] if edit_mode else "")
    team_input = st.text_input("Project Team (comma-separated)",
                               value=", ".join(edit_mode["team"]) if edit_mode else "")
    business_function = st.selectbox("Business Function", BUSINESS_FUNCTIONS,
                                     index=BUSINESS_FUNCTIONS.index(edit_mode["business_function"])
                                     if edit_mode else 0)
    target = st.text_input("Target Completion", value=edit_mode["target"] if edit_mode else "")
    confirmed = st.radio("Confirmed?", ["Yes", "No"], index=0 if edit_mode and edit_mode["confirmed"] else 1)
    status = st.selectbox("Status", STATUS_OPTIONS,
                          index=STATUS_OPTIONS.index(edit_mode["status"]) if edit_mode else 0)
    category = st.selectbox("Category", CATEGORIES,
                            index=CATEGORIES.index(edit_mode["category"]) if edit_mode else 0)
    priority = st.selectbox("Priority", PRIORITY_OPTIONS,
                            index=PRIORITY_OPTIONS.index(edit_mode["priority"]) if edit_mode and edit_mode["category"] == "Pipeline" else 0) if category == "Pipeline" else None
    progress = st.slider("Progress (%)", 0, 100, value=edit_mode["progress"] if edit_mode else 0)
    notes = st.text_area("Notes", value=edit_mode["notes"] if edit_mode else "")
    bottlenecks = st.text_area("Bottlenecks or Concerns", value=edit_mode["bottlenecks"] if edit_mode else "")
    password = st.text_input("Password to manage this project", type="password")

    submitted = st.form_submit_button("Submit Project")
    if submitted:
        if not title or not owner or not password:
            st.warning("Please fill in required fields.")
        else:
            team = [t.strip() for t in team_input.split(",") if t.strip()]
            new_proj = {
                "title": title,
                "owner": owner,
                "team": team,
                "business_function": business_function,
                "target": target,
                "confirmed": confirmed == "Yes",
                "status": status,
                "category": category,
                "priority": priority,
                "progress": progress,
                "notes": notes,
                "bottlenecks": bottlenecks,
                "password": password
            }

            if "edit_mode" in st.session_state:
                projects[st.session_state["edit_idx"]] = new_proj
                del st.session_state["edit_mode"]
                del st.session_state["edit_idx"]
                st.success("✅ Project updated! Please refresh.")
            else:
                projects.append(new_proj)
                st.success("✅ Project added! Please refresh.")
            with open(PROJECTS_FILE, "w") as f:
                json.dump(projects, f, indent=2)
