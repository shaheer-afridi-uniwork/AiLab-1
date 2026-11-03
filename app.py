"""
Roadmap Generator - a Streamlit app that turns your goal, time budget and
constraints into a realistic, week-by-week learning roadmap using the Gemini API.
"""

import os
from datetime import date

import streamlit as st
from google import genai
from google.genai import types

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
st.set_page_config(page_title="Roadmap Generator", page_icon="🗺️", layout="wide")

DEFAULT_MODEL = "gemini-2.5-flash"  # editable in the sidebar; models get retired over time

LEVELS = [
    "Complete beginner",
    "Beginner (know some basics)",
    "Intermediate",
    "Advanced",
]

STYLES = [
    "Video courses",
    "Reading / documentation",
    "Hands-on projects",
    "Practice problems",
    "Study groups / community",
]

BUDGETS = ["Free resources only", "Mostly free, some paid is OK", "Paid is fine"]

SYSTEM_INSTRUCTION = """You are an experienced mentor who builds realistic learning roadmaps.

Rules:
- Be honest. If the goal cannot realistically be reached in the given time and hours, say so clearly
  and give the best achievable alternative instead of pretending.
- Never invent URLs, certificates, or course details. Recommend resources by well-known NAME only
  (e.g. a course title and author/platform) and add a note that the learner should verify availability.
- Respect the learner's total hours. The sum of weekly hours must not exceed what they have.
- Prefer projects and active practice over passive watching.
- Include review/buffer time. Learners fall behind; plan for it.
- Output clean Markdown only.
"""


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def get_api_key(sidebar_value: str) -> str:
    """Priority: sidebar input -> Streamlit secrets -> environment variable."""
    if sidebar_value.strip():
        return sidebar_value.strip()
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass  # no secrets file locally; that's fine
    return os.environ.get("GEMINI_API_KEY", "")


def build_prompt(d: dict) -> str:
    total_hours = d["weeks"] * d["hours_per_week"]
    grouping = (
        "Group the plan into blocks of 2-4 weeks."
        if d["weeks"] > 16
        else "Give a plan for every single week."
    )
    return f"""Create a learning roadmap for this person.

GOAL: {d['goal']}
FINAL OUTCOME THEY WANT: {d['outcome'] or 'Not specified'}
CURRENT LEVEL: {d['level']}
ALREADY KNOWS: {d['known'] or 'Nothing specified'}
START DATE: {d['start_date'].strftime('%d %b %Y')}
DURATION: {d['weeks']} weeks
TIME AVAILABLE: {d['hours_per_week']} hours/week over {d['days_per_week']} days/week (total about {total_hours} hours)
PREFERRED COURSE / RESOURCES: {d['courses'] or 'No preference - recommend well-known options'}
LEARNING STYLE: {', '.join(d['styles']) or 'No preference'}
BUDGET: {d['budget']}
CONSTRAINTS / NOTES: {d['notes'] or 'None'}

Required structure (use these exact headings):
## 1. Feasibility check
Honest verdict on whether the goal fits the time and hours. State assumptions.
## 2. Prerequisites and gaps
## 3. Phase overview
A table: Phase | Weeks | Focus | Outcome.
## 4. Detailed plan
{grouping} For each: focus, hours, concrete tasks, and one measurable deliverable.
## 5. Projects and milestones
## 6. Resources
Names only, no links. If the learner named a course, build the plan around it and say how to pace it.
## 7. Checkpoints
How to tell if they are on track, with specific signals at roughly 25%, 50%, 75% and 100% of the timeline.
## 8. If you fall behind
What to cut first, and what must never be cut.
"""


def generate_roadmap(api_key: str, model: str, prompt: str) -> str:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.4,
        ),
    )
    if not response.text:
        raise ValueError("The model returned an empty response. Try again or change the model.")
    return response.text


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    key_input = st.text_input(
        "Gemini API key",
        type="password",
        help="Optional if the app owner configured one in Streamlit secrets. "
        "Your key is only used for this session and is not stored.",
    )
    model_name = st.text_input("Model", value=DEFAULT_MODEL)
    st.caption("If you get a 'model not found' error, check Google's current model list and update this field.")

# --------------------------------------------------------------------------
# Main UI
# --------------------------------------------------------------------------
st.title("🗺️ Roadmap Generator")
st.write("Tell me your goal and your real constraints. I'll build a plan that fits your actual time.")

with st.form("roadmap_form"):
    goal = st.text_input("What do you want to learn / achieve? *", placeholder="e.g. Machine learning engineering")
    outcome = st.text_input(
        "What should you be able to DO at the end?",
        placeholder="e.g. Build and deploy 2 ML projects for my portfolio",
    )

    c1, c2 = st.columns(2)
    with c1:
        level = st.selectbox("Current level *", LEVELS)
        weeks = st.number_input("Duration (weeks) *", min_value=1, max_value=104, value=12, step=1)
        start = st.date_input("Start date", value=date.today())
    with c2:
        hours = st.slider("Hours per week *", min_value=1, max_value=60, value=10)
        days = st.slider("Study days per week", min_value=1, max_value=7, value=5)
        budget = st.selectbox("Budget", BUDGETS)

    courses = st.text_area(
        "Course(s) / resources you want to follow (optional)",
        placeholder="e.g. Andrew Ng's ML Specialization, CS50, a university syllabus...",
    )
    known = st.text_area(
        "What do you already know? (optional)",
        placeholder="e.g. Python basics, high-school math",
    )
    styles = st.multiselect("How do you learn best?", STYLES, default=["Hands-on projects"])
    notes = st.text_area(
        "Constraints / anything else (optional)",
        placeholder="e.g. exams in week 6, only a laptop with no GPU, weak at math",
    )

    submitted = st.form_submit_button("Generate roadmap 🚀", use_container_width=True)

if submitted:
    api_key = get_api_key(key_input)
    if not goal.strip():
        st.error("Please enter your goal.")
    elif not api_key:
        st.error("No API key found. Enter one in the sidebar or set GEMINI_API_KEY in Streamlit secrets.")
    else:
        data = {
            "goal": goal.strip(),
            "outcome": outcome.strip(),
            "level": level,
            "weeks": int(weeks),
            "hours_per_week": int(hours),
            "days_per_week": int(days),
            "start_date": start,
            "courses": courses.strip(),
            "known": known.strip(),
            "styles": styles,
            "budget": budget,
            "notes": notes.strip(),
        }
        with st.spinner("Building your roadmap..."):
            try:
                st.session_state["roadmap"] = generate_roadmap(api_key, model_name.strip(), build_prompt(data))
                st.session_state["meta"] = data
            except Exception as e:  # network, quota, bad key, bad model name...
                st.session_state.pop("roadmap", None)
                st.error(f"Generation failed: {e}")

# Results are kept in session_state so the download button doesn't wipe them.
if "roadmap" in st.session_state:
    meta = st.session_state["meta"]
    total = meta["weeks"] * meta["hours_per_week"]

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Duration", f"{meta['weeks']} weeks")
    m2.metric("Hours / week", meta["hours_per_week"])
    m3.metric("Total study hours", total)

    if meta["hours_per_week"] / meta["days_per_week"] > 6:
        st.warning("That is over 6 hours per study day. Be honest with yourself about whether that is sustainable.")

    st.markdown(st.session_state["roadmap"])

    st.download_button(
        "⬇️ Download as Markdown",
        data=st.session_state["roadmap"],
        file_name="roadmap.md",
        mime="text/markdown",
    )
    st.caption("AI-generated plan. Verify resource names and availability before committing.")
