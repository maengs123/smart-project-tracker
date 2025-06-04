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
STATUS_COLORS = {"Good": "#28a745", "OK": "#ffc107", "Poor": "#dc3545"}
PRIORITY_OPTIONS = ["High", "Medium", "Low"]

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
owners = sorted(set(p['owner'] for p in projects if 'owner' in p))
selected_owner = st.sidebar.selectbox("👤 Filter by Owner", ["All"] + owners)

# ----------------- 📋 PROJECT TRACKER -----------------
if page == "📋 Project Tracker":
    st.title("📋 Project Tracker")

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
            st.write(f"👥 **Team**: {', '.join(p.get('team', []) or [])}")
            st.write(f"📅 **Target**: {p.get('target', '—')}")

            status = p.get("status", "—")
            status_color = STATUS_COLORS.get(status, "#999")
            st.markdown(f"<span style='color:{status_color}; font-weight:bold;'>🟢 Status: {status}</span>", unsafe_allow_html=True)

            if p.get("category") == "Pipeline":
                st.write(f"⚠️ **Priority**: {p.get('priority', '—')}")
            st.write(f"📝 **Notes**: {p.get('notes', '')}")
            st.write(f"🛠️ **Bottlenecks**: {p.get('bottlenecks', '')}")
            st.write(f"**Progress:** {p.get('progress', 0)}%")
            st.progress(p.get("progress", 0) / 100)

            # Manage
            with st.expander("🔐 Manage Project"):
                action = st.radio("Action", ["None", "Edit", "Delete"], key=f"action_{idx}_{p['title']}")
                pw_input = st.text_input("Password", type="password", key=f"pw_proj_{idx}_{p['title']}")
                if action == "Delete" and pw_input == p["password"]:
                    projects.remove(p)
                    with open(PROJECTS_FILE, "w") as f:
                        json.dump(projects, f, indent=2)
                    st.success("Project deleted. Please refresh.")
                elif action == "Edit" and pw_input == p["password"]:
                    st.session_state["edit_mode"] = p
                    st.session_state["edit_idx"] = idx
                    st.success("Edit mode enabled. Scroll down.")

            st.markdown("---")

    # Add/Edit form
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
                team = [t.strip() for t in team_input.split(",") if t.strip()] if team_input else []
                project = {
                    "title": title,
                    "owner": owner,
                    "team": team,
                    "business_function": business_function,
                    "target": target,
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

# ----------------- 📊 SUMMARY VIEW -----------------
elif page == "📊 Summary View":
    st.title("📊 Project Summary")

    if not projects:
        st.info("No projects available.")
    else:
        df = pd.DataFrame([
            {
                "Project Title": p.get("title", ""),
                "Business Function": p.get("business_function", ""),
                "Category": p.get("category", ""),
                "Owner": p.get("owner", ""),
                "Team": ", ".join(p.get("team", []) or []),
                "Target": p.get("target", ""),
                "Status": p.get("status", ""),
                "Progress (%)": p.get("progress", 0)
            }
            for p in projects
        ])

        def style_status(val):
            color = STATUS_COLORS.get(val, "#999")
            return f"color: {color}; font-weight: bold"

        st.dataframe(df.style.applymap(style_status, subset=["Status"]), use_container_width=True)
