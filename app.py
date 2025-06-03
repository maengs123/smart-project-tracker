# Smart Project Tracker - Final Clean Version
# All previous functionality + new fields: category, team, status, confirmed, priority
# Neat layout, grouped by category

import streamlit as st
import json
import os
from datetime import datetime

PROJECTS_FILE = "projects.json"
COMMENTS_FILE = "comments.json"

# Load or initialize projects and comments
projects = json.load(open(PROJECTS_FILE)) if os.path.exists(PROJECTS_FILE) else []
comments_db = json.load(open(COMMENTS_FILE)) if os.path.exists(COMMENTS_FILE) else {}

st.set_page_config(page_title="Smart Project Tracker", layout="wide")
st.title("📋 Smart Project Tracker")

# Project Categories
CATEGORIES = ["Team Projects", "Active Projects", "Pipeline", "Non-MAS Projects"]
STATUS_OPTIONS = ["OK", "Good", "Poor"]
PRIORITY_OPTIONS = ["High", "Medium", "Low"]

# Filters
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
        st.markdown(f"**🔹 {p['title']}**")
        st.write(f"👤 **Owner**: {p['owner']}")
        st.write(f"👥 **Team**: {', '.join(p.get('team', [])) if p.get('team') else '—'}")
        st.write(f"📅 **Target**: {p.get('target')} | ✅ **Confirmed**: {'Yes' if p.get('confirmed') else 'No'}")
        st.write(f"🟢 **Status**: {p.get('status', '—')}")
        if p.get("category") == "Pipeline":
            st.write(f"⚠️ **Priority**: {p.get('priority', '—')}")
        st.markdown("---")

# Add new project form
st.subheader("➕ Add New Project")
with st.form("new_project_form"):
    title = st.text_input("Project Title")
    owner = st.text_input("Owner Name")
    team_input = st.text_input("Project Team (comma-separated)")
    target = st.text_input("Target Completion Date (e.g., '3Q25', 'June 2025')")
    confirmed = st.radio("Confirmed?", ["Yes", "No"])
    status = st.selectbox("Project Status", STATUS_OPTIONS)
    category = st.selectbox("Project Category", CATEGORIES)
    priority = None
    if category == "Pipeline":
        priority = st.selectbox("Priority", PRIORITY_OPTIONS)
    notes = st.text_area("Notes")
    # details = st.text_area("Details")
    details = st.text_area("Bottlenecks or Concerns")
    password = st.text_input("Password to manage this project", type="password")
    submitted = st.form_submit_button("Add Project")

    if submitted and title and owner and password:
        new_proj = {
            "title": title,
            "owner": owner,
            "team": [name.strip() for name in team_input.split(",") if name.strip()],
            "target": target,
            "confirmed": confirmed == "Yes",
            "status": status,
            "category": category,
            "priority": priority,
            "notes": notes,
            "details": details,
            "password": password
        }
        projects.append(new_proj)
        with open(PROJECTS_FILE, "w") as f:
            json.dump(projects, f, indent=2)
        st.success("✅ Project added!")
