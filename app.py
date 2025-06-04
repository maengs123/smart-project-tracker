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

# Constants
CATEGORIES = ["Team Projects", "Active Projects", "Pipeline", "Non-MAS Projects"]
BUSINESS_FUNCTIONS = ["MAS PM", "Index Management", "ETF Research", "Trading and Ops"]
STATUS_OPTIONS = ["OK", "Good", "Poor"]
PRIORITY_OPTIONS = ["High", "Medium", "Low"]

owners = sorted(set(p['owner'] for p in projects if 'owner' in p))
selected_owner = st.selectbox("👤 Filter by Owner", ["All"] + owners)

# Group by category
grouped = {cat: [] for cat in CATEGORIES}
for proj in projects:
    if selected_owner == "All" or proj.get("owner") == selected_owner:
        grouped[proj.get("category", "Other")].append(proj)

# Display grouped projects
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

        # Project-level progress bar
        prog = st.slider("📊 Project Progress", 0, 100, value=p.get("progress", 0), key=f"progress_{idx}")
        p["progress"] = prog
        st.progress(prog / 100)

        # Save progress immediately
        with open(PROJECTS_FILE, "w") as f:
            json.dump(projects, f, indent=2)

        st.markdown("---")

# Add new project form
st.subheader("➕ Add New Project")
with st.form("new_project_form", clear_on_submit=True):
    title = st.text_input("Project Title")
    owner = st.text_input("Owner Name")
    team_input = st.text_input("Project Team (comma-separated)")
    business_function = st.selectbox("Business Function", BUSINESS_FUNCTIONS)
    target = st.text_input("Target Completion Date (e.g., Q3 2025)")
    confirmed = st.radio("Confirmed?", ["Yes", "No"])
    status = st.selectbox("Project Status", STATUS_OPTIONS)
    category = st.selectbox("Project Category", CATEGORIES)
    priority = st.selectbox("Priority", PRIORITY_OPTIONS) if category == "Pipeline" else None
    progress = st.slider("Project Progress", 0, 100, value=0)
    notes = st.text_area("Notes")
    bottlenecks = st.text_area("Bottlenecks or Concerns")
    password = st.text_input("Password to manage this project", type="password")
    submit = st.form_submit_button("Submit Project")

    if submit:
        if not title or not owner or not password:
            st.warning("❗ Please fill in all required fields: Title, Owner, Password.")
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
            projects.append(new_proj)
            with open(PROJECTS_FILE, "w") as f:
                json.dump(projects, f, indent=2)
            st.success("✅ Project added! Please refresh the page to view it.")
