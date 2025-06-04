import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

PROJECTS_FILE = "projects.json"
COMMENTS_FILE = "comments.json"

# Load data
projects = json.load(open(PROJECTS_FILE)) if os.path.exists(PROJECTS_FILE) else []
comments_db = json.load(open(COMMENTS_FILE)) if os.path.exists(COMMENTS_FILE) else {}

st.set_page_config(page_title="Smart Project Tracker", layout="wide")

# Constants
CATEGORIES = ["Team Projects", "Active Projects", "Pipeline", "Non-MAS Projects"]
BUSINESS_FUNCTIONS = ["MAS PM", "Index Management", "ETF Research", "Trading and Ops"]
STATUS_OPTIONS = ["OK", "Good", "Poor"]
PRIORITY_OPTIONS = ["High", "Medium", "Low"]

# Quarter options
def generate_quarter_options():
    now = datetime.now()
    year = now.year
    month = now.month
    current_q = (month - 1) // 3 + 1
    quarters = []
    for i in range(3):
        q = current_q + i
        y = year
        if q > 4:
            q -= 4
            y += 1
        quarters.append(f"{q}Q{y}")
    quarters.append("TBD")
    return quarters

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["📋 Project Tracker", "📊 Summary View"])

# Filter setup
owners = sorted(set(p['owner'] for p in projects if 'owner' in p))
selected_owner = st.sidebar.selectbox("👤 Filter by Owner", ["All"] + owners)

# ---------------------------- 📋 PROJECT TRACKER ----------------------------
if page == "📋 Project Tracker":
    st.title("📋 Smart Project Tracker")

    # Group projects
    grouped = {cat: [] for cat in CATEGORIES}
    for proj in projects:
        if selected_owner == "All" or proj.get("owner") == selected_owner:
            grouped[proj.get("category", "Other")].append(proj)

    edit_mode = st.session_state.get("edit_mode")
    edit_idx = st.session_state.get("edit_idx")

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

            # Progress bar (read-only view)
            st.write(f"**Progress:** {p.get('progress', 0)}%")
            st.progress(p.get("progress", 0) / 100)

            # if edit_mode and edit_idx == idx:
            #     p["progress"] = st.slider("📊 Project Progress", 0, 100, value=p.get("progress", 0), key=f"progress_{idx}")
            #     with open(PROJECTS_FILE, "w") as f:
            #         json.dump(projects, f, indent=2)
            # else:
            #     st.write(f"**Progress:** {p.get('progress', 0)}%")
            #     st.progress(p.get("progress", 0) / 100)

            # Comment section
            st.markdown("#### 💬 Comments")
            for cidx, c in enumerate(comments_db.get(p['title'], [])):
                st.info(f"**{c['user']}** ({c['timestamp']}): {c['comment']}")
                if "replies" in c:
                    for r in c["replies"]:
                        st.markdown(f"<div style='margin-left: 20px;'>↪️ <b>{r['user']}</b> ({r['timestamp']}): {r['comment']}</div>", unsafe_allow_html=True)
                with st.expander("💬 Reply or 🗑️ Delete this comment"):
                    reply_user = st.text_input(f"Reply Name {idx}_{cidx}")
                    reply_text = st.text_area(f"Reply Message {idx}_{cidx}")
                    reply_submit = st.button(f"Post Reply {idx}_{cidx}")
                    if reply_submit and reply_user and reply_text:
                        c.setdefault("replies", []).append({
                            "user": reply_user,
                            "comment": reply_text,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        with open(COMMENTS_FILE, "w") as f:
                            json.dump(comments_db, f, indent=2)
                        st.success("Reply posted. Please refresh.")
                    del_pw = st.text_input("Password to delete comment", type="password", key=f"delpw_{idx}_{cidx}")
                    if st.button("Delete Comment", key=f"delbtn_{idx}_{cidx}"):
                        if del_pw == c["password"]:
                            comments_db[p['title']].pop(cidx)
                            with open(COMMENTS_FILE, "w") as f:
                                json.dump(comments_db, f, indent=2)
                            st.success("Comment deleted. Please refresh.")
                        else:
                            st.error("Incorrect password.")

            with st.form(f"form_comment_{idx}_{p['title']}"):
                user = st.text_input("Your Name")
                comment = st.text_area("Your Comment")
                pw = st.text_input("Password to delete this comment", type="password")
                submit = st.form_submit_button("Post Comment")
                if submit and user and comment and pw:
                    comments_db.setdefault(p['title'], []).append({
                        "user": user,
                        "comment": comment,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "password": pw,
                        "replies": []
                    })
                    with open(COMMENTS_FILE, "w") as f:
                        json.dump(comments_db, f, indent=2)
                    st.success("Comment posted. Please refresh.")

            # Edit/Delete
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

    # Form to add or edit project
    st.subheader("➕ Add or Edit Project")
    edit_mode = st.session_state.get("edit_mode")
    with st.form("project_form", clear_on_submit=not edit_mode):
        title = st.text_input("Project Title", value=edit_mode["title"] if edit_mode else "")
        owner = st.text_input("Owner", value=edit_mode["owner"] if edit_mode else "")
        team_input = st.text_input("Team (comma-separated)", value=", ".join(edit_mode["team"]) if edit_mode else "")
        business_function = st.selectbox("Business Function", BUSINESS_FUNCTIONS,
                                         index=BUSINESS_FUNCTIONS.index(edit_mode["business_function"]) if edit_mode else 0)
        target = st.selectbox("Target Completion", generate_quarter_options(),
                              index=generate_quarter_options().index(edit_mode["target"]) if edit_mode and edit_mode["target"] in generate_quarter_options() else len(generate_quarter_options()) - 1)
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
                project = {
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

                if edit_mode:
                    projects[edit_idx] = project
                    del st.session_state["edit_mode"]
                    del st.session_state["edit_idx"]
                    st.success("✅ Project updated. Please refresh.")
                else:
                    projects.append(project)
                    st.success("✅ Project added. Please refresh.")

                with open(PROJECTS_FILE, "w") as f:
                    json.dump(projects, f, indent=2)

# ---------------------------- 📊 SUMMARY VIEW ----------------------------
if page == "📊 Summary View":
    st.title("📊 Project Summary")

    if not projects:
        st.info("No projects to summarize.")
    else:
        df = pd.DataFrame([
            {
                "Business Function": p.get("business_function", ""),
                "Category": p.get("category", ""),
                "Owner": p.get("owner", ""),
                "Team": ", ".join(p.get("team", [])),
                "Target": p.get("target", ""),
                "Status": p.get("status", ""),
                "Progress (%)": p.get("progress", 0)
            }
            for p in projects
        ])
        st.dataframe(df, use_container_width=True)
