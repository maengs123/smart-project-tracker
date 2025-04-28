
import streamlit as st
import json
import os
from datetime import datetime

PROJECTS_FILE = "projects.json"
COMMENTS_FILE = "comments.json"

# Load Projects
if os.path.exists(PROJECTS_FILE):
    with open(PROJECTS_FILE, "r") as f:
        projects = json.load(f)
else:
    projects = {}

# Load Comments
if os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, "r") as f:
        comments_db = json.load(f)
else:
    comments_db = {}

st.set_page_config(page_title="Project Tracker Portal", layout="wide")
st.title("📋 Smart Project Tracker Dashboard")

changes_made = False

for project_name, data in projects.items():
    with st.container():
        st.subheader(f"📁 {project_name}  _(Target: {data['target_period']})_")

        subtask_progresses = []
        for idx, subtask in enumerate(data["subtasks"]):
            st.markdown(f"**{subtask['name']}**")
            new_progress = st.slider(
                f"Progress for {subtask['name']}",
                0, 100,
                value=subtask["progress"],
                key=f"{project_name}_{idx}"
            )
            if new_progress != subtask["progress"]:
                data["subtasks"][idx]["progress"] = new_progress
                changes_made = True
            subtask_progresses.append(new_progress)

        overall_progress = sum(subtask_progresses) / len(subtask_progresses)
        st.write("**Overall Project Progress:**")
        st.progress(overall_progress / 100)
        st.write(f"Total Progress: **{overall_progress:.0f}%**")

        new_notes = st.text_area(f"📝 Notes for {project_name}", value=data.get("notes", ""))
        new_details = st.text_area(f"🔍 Full Details for {project_name}", value=data.get("details", ""))

        if new_notes != data.get("notes", "") or new_details != data.get("details", ""):
            data["notes"] = new_notes
            data["details"] = new_details
            changes_made = True

        st.markdown("---")

        st.write("💬 **Team Comments:**")
        project_comments = comments_db.get(project_name, [])
        for c in project_comments:
            st.info(f"**{c['user']}** (📅 {c['timestamp']}): {c['comment']}")

        with st.form(f"comment_form_{project_name}"):
            user = st.text_input("Your Name")
            comment_text = st.text_area("Your Comment")
            submitted = st.form_submit_button("Post Comment")

            if submitted and user and comment_text:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_comment = {"user": user, "timestamp": timestamp, "comment": comment_text}
                project_comments.append(new_comment)
                comments_db[project_name] = project_comments
                with open(COMMENTS_FILE, "w") as f:
                    json.dump(comments_db, f, indent=2)
                st.success("✅ Comment posted! Please refresh the page manually to see the update.")
                
        st.markdown("-----")

if changes_made:
    with open(PROJECTS_FILE, "w") as f:
        json.dump(projects, f, indent=2)
    st.success("✅ Changes saved automatically!")
