# Git Academy — Learn by building

A responsive Git and GitHub learning platform starter with a polished learning workspace, structured lessons, a safe command simulator, quizzes, learner accounts, saved progress, a community leaderboard, and a FastAPI + SQLite backend.

## What's included

- Responsive dark UI with desktop sidebar and mobile navigation
- Six structured learning modules with objectives, explanations, commands, and practice tasks
- Registration and login with password hashing and signed session tokens
- Database-backed lesson completion and quiz attempts
- Interactive 8-question quiz with explanations and saved scores
- Safe Git command simulator (does **not** execute commands on your computer)
- Command guide grouped by everyday basics, remotes, branches, and recovery
- Curated YouTube search links for beginner Git, add/commit/push, branches, and GitHub Pages
- Learner board showing public display names and progress
- FastAPI endpoints, SQLite database, and an admin-only student-list API

## Project structure

```text
git-academy-pro/
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── config.js
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## Run locally on Windows

### 1. Start the backend

Install Python 3.10+ if needed. Open a terminal in the `backend` folder:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive API docs are at `http://127.0.0.1:8000/docs`.

### 2. Start the frontend

Open a **second terminal** in the `frontend` folder. In VS Code, use the Live Server extension and open `index.html`. It commonly serves at `http://127.0.0.1:5500`.

The frontend API URL is in `frontend/config.js`:

```js
window.GIT_ACADEMY_API = 'http://127.0.0.1:8000/api';
```

If your backend runs elsewhere, change this URL and restart/refresh the frontend.

### 3. Try the platform

1. Create an account using a valid email and a password with at least 8 characters.
2. Open **Learning path** and select a lesson.
3. Mark a lesson complete. Your progress is stored in SQLite.
4. Take the knowledge check. Quiz attempts are stored for your account.
5. Use **Practice lab** to simulate commands such as `git status`, `git add README.md`, and `git log --oneline`.
6. Check the learner board. Display names and progress are visible to other visitors; choose a display name you are comfortable sharing.

## Database

The backend creates `backend/git_academy.db` automatically on first run. It stores user profiles, password hashes and salts, lesson completion, and quiz attempts. Back up the database file before making schema changes.

## Important deployment notes

This is a functional starter, not a fully audited production service. Before opening registration to the public:

- Set `GIT_ACADEMY_SECRET` to a long, random secret in the backend hosting environment. Do not rely on the development default or commit secrets.
- Set `CORS_ORIGINS` to the exact deployed frontend origin(s), not `*`.
- Use HTTPS for both frontend and backend.
- Use a managed database and backups for production; SQLite is suitable for local development and small demos but is not the best choice for a high-concurrency service.
- Add rate limiting, email verification, password reset, account deletion/export, moderation/reporting, and security testing before a public launch.
- The current frontend stores the session token in browser local storage. For a hardened production deployment, prefer secure, HttpOnly, SameSite cookies and a CSRF strategy.
- YouTube cards open search results rather than embedding or guaranteeing a particular video. Choose current, reputable videos before recommending them to learners.
- GitHub Pages only hosts the static frontend. It does not run FastAPI or SQLite. Host the API separately and set `frontend/config.js` to its HTTPS URL.

## Admin API

An admin-only endpoint exists at `GET /api/admin/students`. New registrations are students by default. There is not yet a user-facing admin dashboard or admin-promotion workflow in this starter. Do not promote an account without authenticating the administrator out of band. For local testing only, you can update a trusted account's role in the SQLite `users` table to `admin`; never expose arbitrary role editing to public users.

## Main API endpoints

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/me`
- `GET /api/lessons`
- `POST /api/progress/complete` (authenticated)
- `GET /api/progress` (authenticated)
- `GET /api/quiz`
- `POST /api/quiz/submit` (authenticated)
- `GET /api/leaderboard`
- `GET /api/admin/students` (admin only)

## Tech stack

HTML, CSS, JavaScript, Python, FastAPI, SQLite, and REST APIs. The frontend uses no build step, so it is easy to inspect and modify while learning.
