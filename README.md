# AiLab-1

# 🗺️ Roadmap Generator

A Streamlit web app that turns your goal, available time, current level and preferred courses into a realistic, week-by-week learning roadmap, powered by the Google Gemini API.

## What it does

You fill in a form:

| Input | Why it matters |
|---|---|
| Goal and desired outcome | Defines what "done" means |
| Current level and what you already know | Avoids wasting time on things you know |
| Duration (weeks), hours per week, study days per week | The roadmap must fit your *real* time |
| Start date | Plan is anchored to actual dates |
| Preferred course(s) / resources | Plan is built around them instead of ignoring them |
| Learning style and budget | Filters recommendations |
| Constraints (exams, hardware, weak areas) | Makes the plan realistic |

The app builds a structured prompt from those inputs and asks Gemini to produce:

1. Feasibility check (honest verdict on whether the goal fits your time)
2. Prerequisites and gaps
3. Phase overview table
4. Detailed week-by-week (or block-by-block for long plans) plan
5. Projects and milestones
6. Resources (names only, never invented links)
7. Checkpoints to know if you're on track
8. What to cut if you fall behind

You can download the result as a Markdown file.

## How it works (architecture)

```
Streamlit form  ->  build_prompt()  ->  Gemini API  ->  Markdown roadmap  ->  display + download
```

- `app.py`: the whole app (UI, prompt building, API call)
- `requirements.txt`: dependencies
- Results are stored in `st.session_state` so clicking the download button doesn't erase the roadmap.
- API key priority: sidebar input, then Streamlit secrets, then the `GEMINI_API_KEY` environment variable.

### Honest limitations

- The roadmap is **AI-generated**. It can be wrong or outdated. Verify course names and availability.
- The app does not browse the web, so it cannot confirm that a course still exists.
- Model names change over time. If you see a "model not found" error, update the **Model** field in the sidebar (and `DEFAULT_MODEL` in `app.py`) using Google's current model list.

---

## Run locally

1. **Install Python 3.10+** and Git.
2. Clone or download this repo, then in the project folder:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   ```
3. **Get a Gemini API key** from Google AI Studio (aistudio.google.com). Free tier availability and limits change, so check the current terms.
4. Provide the key in **one** of these ways:
   - Paste it into the app's sidebar (simplest), or
   - Create `.streamlit/secrets.toml` in the project folder:
     ```toml
     GEMINI_API_KEY = "your-key-here"
     ```
5. Run:
   ```bash
   streamlit run app.py
   ```
   It opens at `http://localhost:8501`.

---

## Push to GitHub (step by step)

1. Create a `.gitignore` file in the project folder containing:
   ```
   venv/
   __pycache__/
   .streamlit/secrets.toml
   .env
   ```
   **This is critical.** It stops your API key from being uploaded.
2. Go to github.com, click **New repository**, name it (e.g. `roadmap-generator`), and create it. Public is required for the free Streamlit Community Cloud tier unless you connect a private repo with permission.
3. In your project folder run:
   ```bash
   git init
   git add app.py requirements.txt README.md .gitignore
   git commit -m "Initial commit: roadmap generator"
   git branch -M main
   git remote add origin https://github.com/<your-username>/roadmap-generator.git
   git push -u origin main
   ```
4. Open the repo on GitHub and confirm that `app.py`, `requirements.txt` and `README.md` are there, and that `secrets.toml` is **not**.

> If you ever accidentally commit a key, deleting the file is not enough because it stays in git history. Revoke the key in Google AI Studio and create a new one.

---

## Deploy on Streamlit Community Cloud (step by step)

Menu labels may change slightly over time, but the flow is the same.

1. Go to **share.streamlit.io** and sign in with your GitHub account. Authorize Streamlit to access your repositories.
2. Click **Create app** (or **New app**) and choose **Deploy a public app from GitHub**.
3. Fill in:
   - **Repository:** `<your-username>/roadmap-generator`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** pick a custom subdomain if you like.
4. Click **Advanced settings** and:
   - Choose a **Python version** (3.11 or 3.12 is a safe choice).
   - In the **Secrets** box, paste:
     ```toml
     GEMINI_API_KEY = "your-key-here"
     ```
5. Click **Deploy**. The first build installs everything from `requirements.txt` and takes a minute or two.
6. Your app is live at `https://<your-subdomain>.streamlit.app`. Every `git push` to `main` redeploys it automatically.

### Update secrets later
Open your app dashboard on share.streamlit.io, go to the app's **Settings**, then **Secrets**, edit, and save.

### Important: protect your quota
If you put **your** API key in secrets, anyone with the link can use your quota. Options:
- Leave the secret empty and make users paste their own key in the sidebar (the app already supports this).
- Keep the app private/restricted to specific viewers in the sharing settings.
- Set a quota or budget limit in your Google Cloud / AI Studio account.

---

## Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| `ModuleNotFoundError: google` | `google-genai` missing. Check `requirements.txt` is in the repo root and spelled correctly, then reboot the app. |
| "No API key found" | Secret name must be exactly `GEMINI_API_KEY`, or paste a key in the sidebar. |
| "model not found" / 404 | The model was renamed or retired. Update the Model field in the sidebar and `DEFAULT_MODEL` in `app.py`. |
| 429 / quota errors | Rate limit or quota hit. Wait, or use a different key/plan. |
| App not updating after push | Open the app menu and choose **Reboot app**, and confirm you pushed to the branch the app watches. |

## Ideas to extend it

- Export to PDF or a Notion-ready format
- Save/load roadmaps (needs a database or file storage)
- Progress tracker with checkboxes per week
- A second pass that critiques its own plan for realism

## License

MIT. Use it, modify it, learn from it.
