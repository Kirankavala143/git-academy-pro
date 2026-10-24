from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from pathlib import Path
import sqlite3, hashlib, secrets, hmac, base64, json, os, time

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv('GIT_ACADEMY_DB', APP_DIR / 'git_academy.db'))
SECRET = os.getenv('GIT_ACADEMY_SECRET', 'CHANGE_THIS_SECRET_BEFORE_DEPLOYING_' + secrets.token_hex(16)).encode()
TOKEN_TTL = 60 * 60 * 24 * 7

app = FastAPI(title='Git Academy API', version='1.0.0', description='Learning platform API for Git Academy')
app.add_middleware(CORSMiddleware, allow_origins=os.getenv('CORS_ORIGINS', 'http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000').split(','), allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

LESSONS = [
 {'id':'git-basics','module':1,'title':'Git foundations','level':'Beginner','minutes':20,'summary':'Understand version control, repositories, snapshots, and the difference between Git and GitHub.','objectives':['Explain why version control matters','Distinguish Git from GitHub','Describe working directory, staging area, and repository history'],'content':[
  {'heading':'What problem does Git solve?','body':'Imagine editing a project and saving files as final, final-v2, and final-really-final. Git replaces that confusion with a history of intentional snapshots. You can inspect changes, compare versions, and return to a known point.'},
  {'heading':'Git and GitHub are different','body':'Git is the version-control tool that runs on your computer. GitHub is an online service that hosts Git repositories and adds collaboration features such as pull requests, issues, reviews, and project discussions.'},
  {'heading':'The three places to remember','body':'Working directory: files you are editing. Staging area: the exact changes selected for the next snapshot. Repository history: commits already saved by Git.'}],
  'commands':['git --version','git status','git log --oneline'],'task':'In your own words, explain the difference between Git and GitHub. Then run git --version in your terminal.'},
 {'id':'first-repo','module':2,'title':'Create your first repository','level':'Beginner','minutes':25,'summary':'Initialize a project, stage changes, create a commit, and read the history.','objectives':['Initialize a local repository','Stage selected changes','Write useful commit messages'],'content':[
  {'heading':'Start in the correct folder','body':'Open a terminal in the project folder you want Git to track. Avoid initializing a parent folder that contains unrelated projects.'},
  {'heading':'Create a repository','body':'Run git init once for a new local project. Git creates a hidden .git directory that stores repository metadata and history.'},
  {'heading':'The everyday three-step workflow','body':'Use git status to inspect changes, git add to select changes for the next snapshot, and git commit to save that snapshot locally. A commit does not automatically upload anything to GitHub.'}],
  'commands':['git init','git status','git add README.md','git commit -m "Add project README"','git log --oneline'],'task':'Create a folder named git-practice, add a README.md file, initialize Git, make your first commit, and inspect it with git log --oneline.'},
 {'id':'github-remotes','module':3,'title':'Connect GitHub and push','level':'Beginner','minutes':25,'summary':'Connect your local repository to GitHub and publish commits.','objectives':['Understand local versus remote repositories','Add and inspect a remote','Push commits to GitHub'],'content':[
  {'heading':'Local and remote repositories','body':'Your local repository and GitHub repository are separate until you connect them. A remote is a named URL pointing to another repository; origin is the common default name.'},
  {'heading':'Connect to an empty GitHub repository','body':'Create an empty repository on GitHub first. Copy its HTTPS URL, then add it as origin. Do not paste a placeholder URL literally.'},
  {'heading':'Push your commit','body':'The first push often uses -u to set the upstream branch. After that, git push is usually enough. Authentication may require a browser sign-in or a personal access token depending on your setup.'}],
  'commands':['git remote add origin https://github.com/USERNAME/REPOSITORY.git','git remote -v','git branch -M main','git push -u origin main'],'task':'Create an empty GitHub repository, connect it to a local project, and push your first commit.'},
 {'id':'branches','module':4,'title':'Branches and collaboration','level':'Intermediate','minutes':30,'summary':'Develop features safely, merge work, and understand pull requests.','objectives':['Create and switch branches','Merge a feature branch','Explain the purpose of a pull request'],'content':[
  {'heading':'Why branches help','body':'A branch is a movable pointer to a line of commits. Work on a feature branch so experiments do not immediately change the main branch.'},
  {'heading':'A simple feature workflow','body':'Create a branch, edit files, commit your changes, switch back to main, and merge the feature branch. Teams often push the branch and open a pull request so others can review it before merging.'},
  {'heading':'Merge conflicts','body':'A conflict means Git cannot automatically reconcile overlapping edits. Open the conflicted file, choose the intended final content, remove conflict markers, test the result, and commit the resolution.'}],
  'commands':['git switch -c feature/navbar','git add .','git commit -m "Add navbar"','git switch main','git merge feature/navbar'],'task':'Create a branch called feature/readme, make a small change, commit it, and merge it back into main.'},
 {'id':'undo','module':5,'title':'Undo mistakes safely','level':'Intermediate','minutes':25,'summary':'Choose the right recovery command for unstaged, staged, and committed changes.','objectives':['Inspect before recovering','Unstage without discarding edits','Use revert for shared history'],'content':[
  {'heading':'Inspect first','body':'Before recovery, run git status and git log --oneline. If you are unsure, make a backup copy of important work before using a destructive command.'},
  {'heading':'Unstage and discard are different','body':'git restore --staged FILE removes a file from the staging area while keeping the working changes. git restore FILE discards unstaged edits to that file, so use it carefully.'},
  {'heading':'Revert versus reset','body':'git revert COMMIT creates a new commit that reverses an earlier commit and is generally safer for shared history. git reset moves the current branch pointer and can make commits harder to find; understand the mode before using it.'}],
  'commands':['git status','git restore --staged README.md','git log --oneline','git revert COMMIT_HASH'],'task':'Stage a file, unstage it while preserving edits, and explain why revert is often safer than rewriting shared history.'},
 {'id':'pages','module':6,'title':'Publish a website with GitHub Pages','level':'Beginner','minutes':20,'summary':'Deploy a static website and troubleshoot common path and publishing issues.','objectives':['Understand what Pages can host','Configure a deployment branch','Check relative asset paths'],'content':[
  {'heading':'What GitHub Pages can host','body':'GitHub Pages can host static HTML, CSS, and client-side JavaScript. It does not run a Python or Node backend. A full-stack app needs a separately hosted API and database.'},
  {'heading':'Publish from a branch','body':'Confirm index.html is in the folder you plan to publish. In repository Settings, open Pages, choose deployment from a branch, select main and the correct folder, and save.'},
  {'heading':'Troubleshoot the live site','body':'Wait for the deployment to finish, open the URL shown in Settings, and check browser developer tools if styling or scripts fail. For project sites, the URL includes the repository name, so asset paths must be correct.'}],
  'commands':['git status','git add .','git commit -m "Prepare site for Pages"','git push'],'task':'Publish a simple HTML/CSS site using GitHub Pages and verify it on both desktop and mobile.'}
]

QUIZ = [
 {'id':1,'question':'What is Git primarily used for?','options':['Hosting websites only','Tracking changes to files over time','Designing user interfaces','Managing email accounts'],'answer':1,'explanation':'Git records project history and helps you compare, branch, and restore versions.'},
 {'id':2,'question':'Which statement about GitHub is correct?','options':['GitHub and Git are exactly the same','GitHub is an online platform that can host Git repositories','GitHub replaces the need for commits','GitHub only works with Python'],'answer':1,'explanation':'Git is the version-control system; GitHub hosts repositories and provides collaboration tools.'},
 {'id':3,'question':'What does git add do?','options':['Uploads files to GitHub immediately','Deletes old commits','Stages selected changes for a commit','Creates a new GitHub account'],'answer':2,'explanation':'git add selects changes for the next local commit; it does not push them online.'},
 {'id':4,'question':'Which command saves a local snapshot?','options':['git commit','git status','git remote -v','git fetch'],'answer':0,'explanation':'git commit records the staged changes in local repository history.'},
 {'id':5,'question':'What does git status show?','options':['Your GitHub password','The current branch and file states','All private repositories on GitHub','Your internet speed'],'answer':1,'explanation':'git status reports the branch and whether files are untracked, modified, staged, or clean.'},
 {'id':6,'question':'What does git push do?','options':['Uploads local commits to a remote','Stages a file','Creates a local commit','Removes a branch automatically'],'answer':0,'explanation':'git push sends local commits to a configured remote repository.'},
 {'id':7,'question':'Why use a feature branch?','options':['To avoid writing commit messages','To work on changes separately from the main line','To delete the remote repository','To make Git work offline only'],'answer':1,'explanation':'Branches let you develop and review changes separately before merging.'},
 {'id':8,'question':'Which is generally safer for reversing a commit already shared with teammates?','options':['git revert','git reset --hard','Delete the .git folder','Force-push without checking'],'answer':0,'explanation':'git revert adds a new commit that reverses an earlier one without rewriting shared history.'}
]

class RegisterIn(BaseModel):
 name: str = Field(min_length=2, max_length=60)
 email: EmailStr
 password: str = Field(min_length=8, max_length=128)
class LoginIn(BaseModel):
 email: EmailStr
 password: str = Field(min_length=1, max_length=128)
class CompleteIn(BaseModel): lesson_id: str
class QuizIn(BaseModel): answers: dict[str, int]


def db():
 conn = sqlite3.connect(DB_PATH)
 conn.row_factory = sqlite3.Row
 return conn

def init_db():
 with db() as c:
  c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, salt TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'student', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
  c.execute('''CREATE TABLE IF NOT EXISTS progress (user_id INTEGER NOT NULL, lesson_id TEXT NOT NULL, completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(user_id, lesson_id), FOREIGN KEY(user_id) REFERENCES users(id))''')
  c.execute('''CREATE TABLE IF NOT EXISTS quiz_attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, score INTEGER NOT NULL, total INTEGER NOT NULL, attempted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))''')
init_db()

def pw_hash(password, salt=None):
 salt = salt or secrets.token_hex(16)
 digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 240000).hex()
 return digest, salt

def make_token(user_id, role):
 payload = base64.urlsafe_b64encode(json.dumps({'uid':user_id,'role':role,'exp':int(time.time())+TOKEN_TTL}).encode()).decode().rstrip('=')
 sig = hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()
 return payload + '.' + sig

def current_user(authorization: str | None = Header(default=None)):
 if not authorization or not authorization.startswith('Bearer '): raise HTTPException(401, 'Please log in to continue.')
 try:
  payload, sig = authorization[7:].split('.', 1)
  expected = hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()
  if not hmac.compare_digest(sig, expected): raise ValueError()
  data = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload)%4)))
  if data['exp'] < time.time(): raise ValueError()
  with db() as c: user = c.execute('SELECT id,name,email,role FROM users WHERE id=?', (data['uid'],)).fetchone()
  if not user: raise ValueError()
  return dict(user)
 except Exception: raise HTTPException(401, 'Session expired. Please log in again.')

def public_lesson(lesson):
 return {k:v for k,v in lesson.items() if k != 'task'} | {'task':lesson['task']}

@app.get('/api/health')
def health(): return {'status':'ok','service':'Git Academy API'}

@app.post('/api/auth/register')
def register(body: RegisterIn):
 name = body.name.strip()
 if len(name)<2: raise HTTPException(400,'Please enter your name.')
 hashed, salt = pw_hash(body.password)
 try:
  with db() as c:
   cur = c.execute('INSERT INTO users(name,email,password_hash,salt) VALUES(?,?,?,?)',(name,body.email.lower(),hashed,salt))
   uid = cur.lastrowid
 except sqlite3.IntegrityError: raise HTTPException(409,'An account with this email already exists.')
 user={'id':uid,'name':name,'email':body.email.lower(),'role':'student'}
 return {'token':make_token(uid,'student'),'user':user}

@app.post('/api/auth/login')
def login(body: LoginIn):
 with db() as c: row=c.execute('SELECT * FROM users WHERE email=?',(body.email.lower(),)).fetchone()
 if not row: raise HTTPException(401,'Email or password is incorrect.')
 expected,_=pw_hash(body.password,row['salt'])
 if not hmac.compare_digest(expected,row['password_hash']): raise HTTPException(401,'Email or password is incorrect.')
 user={'id':row['id'],'name':row['name'],'email':row['email'],'role':row['role']}
 return {'token':make_token(row['id'],row['role']),'user':user}

@app.get('/api/me')
def me(user=Depends(current_user)): return {'user':user}

@app.get('/api/lessons')
def get_lessons(): return {'lessons':[public_lesson(x) for x in LESSONS]}

@app.get('/api/quiz')
def get_quiz(): return {'questions':[{'id':q['id'],'question':q['question'],'options':q['options']} for q in QUIZ]}

@app.post('/api/progress/complete')
def complete(body: CompleteIn, user=Depends(current_user)):
 if body.lesson_id not in [x['id'] for x in LESSONS]: raise HTTPException(404,'Lesson not found.')
 with db() as c: c.execute('INSERT OR IGNORE INTO progress(user_id,lesson_id) VALUES(?,?)',(user['id'],body.lesson_id))
 return {'completed':True,'progress':get_progress_for(user['id'])}

def get_progress_for(uid):
 with db() as c:
  rows=c.execute('SELECT lesson_id,completed_at FROM progress WHERE user_id=? ORDER BY completed_at',(uid,)).fetchall()
  attempts=c.execute('SELECT score,total,attempted_at FROM quiz_attempts WHERE user_id=? ORDER BY id DESC LIMIT 5',(uid,)).fetchall()
 return {'completed_lesson_ids':[r['lesson_id'] for r in rows], 'completed_count':len(rows), 'total_lessons':len(LESSONS), 'percent':round(len(rows)/len(LESSONS)*100), 'quiz_attempts':[dict(r) for r in attempts]}

@app.get('/api/progress')
def progress(user=Depends(current_user)): return get_progress_for(user['id'])

@app.post('/api/quiz/submit')
def submit_quiz(body: QuizIn, user=Depends(current_user)):
 score=0
 for q in QUIZ:
  if body.answers.get(str(q['id'])) == q['answer']: score += 1
 with db() as c: c.execute('INSERT INTO quiz_attempts(user_id,score,total) VALUES(?,?,?)',(user['id'],score,len(QUIZ)))
 return {'score':score,'total':len(QUIZ),'percent':round(score/len(QUIZ)*100),'results':[{'id':q['id'],'correct':body.answers.get(str(q['id']))==q['answer'],'answer':q['answer'],'explanation':q['explanation']} for q in QUIZ]}

@app.get('/api/leaderboard')
def leaderboard():
 with db() as c:
  rows=c.execute('''SELECT u.name, COUNT(p.lesson_id) AS completed, COALESCE(MAX(q.score*1.0/q.total),0) AS best_quiz FROM users u LEFT JOIN progress p ON p.user_id=u.id LEFT JOIN quiz_attempts q ON q.user_id=u.id GROUP BY u.id ORDER BY completed DESC, best_quiz DESC, u.name ASC LIMIT 20''').fetchall()
 return {'students':[{'name':r['name'],'completed':r['completed'],'best_quiz_percent':round(r['best_quiz']*100)} for r in rows]}

@app.get('/api/admin/students')
def admin_students(user=Depends(current_user)):
 if user['role']!='admin': raise HTTPException(403,'Admin access required.')
 with db() as c:
  rows=c.execute('''SELECT u.id,u.name,u.email,u.created_at,COUNT(DISTINCT p.lesson_id) completed,COUNT(DISTINCT q.id) quiz_attempts FROM users u LEFT JOIN progress p ON p.user_id=u.id LEFT JOIN quiz_attempts q ON q.user_id=u.id GROUP BY u.id ORDER BY u.created_at DESC''').fetchall()
 return {'students':[dict(r) for r in rows]}
