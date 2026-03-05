import os, re, json
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify)
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

try:
    import PyPDF2;  PDF_SUPPORT  = True
except ImportError: PDF_SUPPORT  = False
try:
    import docx as python_docx; DOCX_SUPPORT = True
except ImportError:             DOCX_SUPPORT = False

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
app.config["UPLOAD_FOLDER"]       = os.path.join("static", "uploads")
app.config["MAX_CONTENT_LENGTH"]  = 10 * 1024 * 1024
ALLOWED_EXT = {"pdf", "doc", "docx"}
bcrypt = Bcrypt(app)

# ── MongoDB ───────────────────────────────────────────────────────────────────
MONGO_URI = "mongodb+srv://manaswinisanan9:manaswini5566@cluster0.migsvxg.mongodb.net/resumevis?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database("resumevis")

students_col     = db["students"]
resumes_col      = db["resumes"]
skills_col       = db["skills"]
certs_col        = db["certificates"]
quizzes_col      = db["quizzes"]
quiz_results_col = db["quiz_results"]
trust_scores_col = db["trust_scores"]
recruiters_col   = db["recruiters"]
jobs_col         = db["jobs"]
applications_col = db["applications"]

# ── Seed quizzes ──────────────────────────────────────────────────────────────
def seed_quizzes():
    if quizzes_col.count_documents({}) == 0:
        sample = [
            {"skill_name":"Python","question":"What is the output of print(type([]))?",
             "optionA":"<class 'list'>","optionB":"<class 'tuple'>","optionC":"<class 'dict'>","optionD":"<class 'set'>","correctAnswer":"A"},
            {"skill_name":"Python","question":"Which keyword defines a function in Python?",
             "optionA":"func","optionB":"define","optionC":"def","optionD":"function","correctAnswer":"C"},
            {"skill_name":"Python","question":"What does len([1,2,3]) return?",
             "optionA":"2","optionB":"3","optionC":"4","optionD":"1","correctAnswer":"B"},
            {"skill_name":"Python","question":"Which is used to handle exceptions in Python?",
             "optionA":"catch","optionB":"except","optionC":"error","optionD":"handle","correctAnswer":"B"},
            {"skill_name":"Python","question":"What does 'import os' do?",
             "optionA":"Imports operating system module","optionB":"Opens a file","optionC":"Installs os package","optionD":"Creates os object","correctAnswer":"A"},
            {"skill_name":"JavaScript","question":"Which method converts JSON string to object?",
             "optionA":"JSON.stringify()","optionB":"JSON.parse()","optionC":"JSON.convert()","optionD":"JSON.decode()","correctAnswer":"B"},
            {"skill_name":"JavaScript","question":"What does '===' check?",
             "optionA":"Value only","optionB":"Type only","optionC":"Value and type","optionD":"Reference","correctAnswer":"C"},
            {"skill_name":"JavaScript","question":"Which is NOT a JS data type?",
             "optionA":"String","optionB":"Boolean","optionC":"Float","optionD":"Symbol","correctAnswer":"C"},
            {"skill_name":"JavaScript","question":"What does 'typeof null' return?",
             "optionA":"null","optionB":"undefined","optionC":"object","optionD":"string","correctAnswer":"C"},
            {"skill_name":"JavaScript","question":"Which method adds an element to end of array?",
             "optionA":"push()","optionB":"pop()","optionC":"shift()","optionD":"append()","correctAnswer":"A"},
            {"skill_name":"SQL","question":"Which SQL command retrieves data?",
             "optionA":"GET","optionB":"FETCH","optionC":"SELECT","optionD":"READ","correctAnswer":"C"},
            {"skill_name":"SQL","question":"Which clause filters rows?",
             "optionA":"HAVING","optionB":"WHERE","optionC":"GROUP BY","optionD":"ORDER BY","correctAnswer":"B"},
            {"skill_name":"SQL","question":"What does PRIMARY KEY ensure?",
             "optionA":"Uniqueness","optionB":"Not Null","optionC":"Both uniqueness and not null","optionD":"Foreign reference","correctAnswer":"C"},
            {"skill_name":"SQL","question":"Which JOIN returns all rows from left table?",
             "optionA":"INNER JOIN","optionB":"RIGHT JOIN","optionC":"LEFT JOIN","optionD":"CROSS JOIN","correctAnswer":"C"},
            {"skill_name":"SQL","question":"Which function counts rows?",
             "optionA":"SUM()","optionB":"COUNT()","optionC":"MAX()","optionD":"AVG()","correctAnswer":"B"},
            {"skill_name":"Machine Learning","question":"Which algorithm is used for classification?",
             "optionA":"Linear Regression","optionB":"K-Means","optionC":"Random Forest","optionD":"PCA","correctAnswer":"C"},
            {"skill_name":"Machine Learning","question":"What does overfitting mean?",
             "optionA":"Model too simple","optionB":"Model memorizes training data","optionC":"High bias","optionD":"Low variance","correctAnswer":"B"},
            {"skill_name":"Machine Learning","question":"Which metric is used for classification?",
             "optionA":"RMSE","optionB":"R²","optionC":"F1-Score","optionD":"MAE","correctAnswer":"C"},
            {"skill_name":"Machine Learning","question":"What is the purpose of train-test split?",
             "optionA":"Speed up training","optionB":"Evaluate model on unseen data","optionC":"Reduce dataset size","optionD":"Normalize features","correctAnswer":"B"},
            {"skill_name":"Machine Learning","question":"Which technique reduces dimensionality?",
             "optionA":"SVM","optionB":"PCA","optionC":"KNN","optionD":"Decision Tree","correctAnswer":"B"},
            {"skill_name":"Data Analysis","question":"Which library is used for data manipulation?",
             "optionA":"NumPy","optionB":"Pandas","optionC":"Matplotlib","optionD":"Seaborn","correctAnswer":"B"},
            {"skill_name":"Data Analysis","question":"What does a boxplot show?",
             "optionA":"Correlation","optionB":"Distribution quartiles","optionC":"Time series","optionD":"Pie chart","correctAnswer":"B"},
            {"skill_name":"Data Analysis","question":"What is the median of [1,2,3,4,5]?",
             "optionA":"2","optionB":"3","optionC":"4","optionD":"2.5","correctAnswer":"B"},
            {"skill_name":"Data Analysis","question":"Which pandas method shows first 5 rows?",
             "optionA":".tail()","optionB":".info()","optionC":".head()","optionD":".describe()","correctAnswer":"C"},
            {"skill_name":"Data Analysis","question":"What does df.dropna() do?",
             "optionA":"Fills missing values","optionB":"Removes rows with NaN","optionC":"Renames columns","optionD":"Sorts data","correctAnswer":"B"},
        ]
        quizzes_col.insert_many(sample)
        print("✅ Sample quizzes seeded.")

seed_quizzes()

# ── Certificate validation ─────────────────────────────────────────────────────
CERT_PATTERNS = {
    "coursera":   r'^[A-Z0-9]{12}$',
    "aws":        r'^AWS-[0-9]{9}$|^[A-Z0-9]{12,16}$',
    "google":     r'^[a-f0-9]{32}$|^[0-9]{6}$',
    "microsoft":  r'^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$',
    "nptel":      r'^NPTEL[A-Z0-9]{8,15}$',
    "ibm":        r'^[A-Z0-9]{10,16}$',
    "meta":       r'^[A-Z0-9]{10,14}$',
}

def validate_cert(cert_name, cert_number):
    name_lower = cert_name.lower()
    cert_upper = cert_number.upper().strip()
    for provider, pattern in CERT_PATTERNS.items():
        if provider in name_lower:
            return "verified" if re.match(pattern, cert_upper) else "unverified", provider
    # Generic: 10-32 alphanumeric with optional hyphens
    if re.match(r'^[A-Z0-9][A-Z0-9\-]{8,30}[A-Z0-9]$', cert_upper):
        return "verified", "generic"
    return "unverified", "unknown"

# ── Resume parsing ─────────────────────────────────────────────────────────────
SKILL_KEYWORDS = [
    "Python","JavaScript","Java","C++","C#","SQL","HTML","CSS","React","Angular",
    "Vue","Node.js","Django","Flask","Machine Learning","Deep Learning","Data Analysis",
    "TensorFlow","PyTorch","AWS","Azure","GCP","Docker","Kubernetes","Git","Linux",
    "MongoDB","PostgreSQL","MySQL","REST API","GraphQL","TypeScript","Scala","R",
    "Excel","Power BI","Tableau","Pandas","NumPy","Scikit-learn","NLP","Computer Vision",
]

def extract_text(path):
    ext = path.rsplit(".", 1)[-1].lower()
    text = ""
    if ext == "pdf" and PDF_SUPPORT:
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages: text += page.extract_text() or ""
        except: pass
    elif ext in ("doc","docx") and DOCX_SUPPORT:
        try:
            doc = python_docx.Document(path)
            for p in doc.paragraphs: text += p.text + "\n"
        except: pass
    return text

def parse_resume(text):
    education, experience, skills, certs = [], [], [], []
    for sk in SKILL_KEYWORDS:
        if re.search(r'\b' + re.escape(sk) + r'\b', text, re.IGNORECASE):
            skills.append(sk)
    lines = text.split("\n"); current = None
    for line in lines:
        line = line.strip()
        if not line: continue
        low = line.lower()
        if any(k in low for k in ["education","academic","degree","university","college"]): current = "edu"
        elif any(k in low for k in ["experience","employment","work history","career"]): current = "exp"
        elif any(k in low for k in ["certification","certificate","license"]): current = "cert"
        else:
            if current == "edu"  and len(line) > 5: education.append(line)
            elif current == "exp" and len(line) > 5: experience.append(line)
            elif current == "cert" and len(line) > 5: certs.append(line)
    return list(dict.fromkeys(education))[:10], list(dict.fromkeys(experience))[:10], skills, certs

# ── Trust score ────────────────────────────────────────────────────────────────
def recalculate_trust(sid):
    score = 0
    resume = resumes_col.find_one({"student_id": sid})
    if resume and resume.get("education"): score += 40
    vc = certs_col.count_documents({"student_id": sid, "verified_status": "verified"})
    score += min(vc * 20, 40)
    vs = skills_col.count_documents({"student_id": sid, "verified_status": "verified"})
    score += min(vs * 10, 20)
    trust_scores_col.update_one({"student_id": sid},
        {"$set": {"score": score, "updated_at": datetime.utcnow()}}, upsert=True)
    return score

# ── Auth decorators ────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def d(*a, **kw):
        if "student_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("student_login"))
        return f(*a, **kw)
    return d

def recruiter_required(f):
    @wraps(f)
    def d(*a, **kw):
        if "recruiter_id" not in session:
            flash("Recruiter login required.", "warning")
            return redirect(url_for("recruiter_login"))
        return f(*a, **kw)
    return d

def allowed_file(fn):
    return "." in fn and fn.rsplit(".",1)[1].lower() in ALLOWED_EXT

# ═════════════════════════════════════════════════════════════════════════════
#  INDEX
# ═════════════════════════════════════════════════════════════════════════════
@app.route("/")
def index():
    return render_template("index.html")

# ═════════════════════════════════════════════════════════════════════════════
#  STUDENT AUTH
# ═════════════════════════════════════════════════════════════════════════════
@app.route("/student/register", methods=["GET","POST"])
def student_register():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        if not name or not email or not password:
            flash("All fields are required.", "danger"); return redirect(url_for("student_register"))
        if students_col.find_one({"email": email}):
            flash("Email already registered.", "danger"); return redirect(url_for("student_register"))
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        r = students_col.insert_one({"name":name,"email":email,"password":hashed,
            "resume_path":None,"headline":"","location":"","created_at":datetime.utcnow()})
        session["student_id"] = str(r.inserted_id); session["student_name"] = name
        flash("Account created!", "success"); return redirect(url_for("student_dashboard"))
    return render_template("student_register.html")

@app.route("/student/login", methods=["GET","POST"])
def student_login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        s = students_col.find_one({"email": email})
        if s and bcrypt.check_password_hash(s["password"], password):
            session["student_id"] = str(s["_id"]); session["student_name"] = s["name"]
            flash(f"Welcome back, {s['name']}!", "success"); return redirect(url_for("student_dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("student_login.html")

@app.route("/student/logout")
def student_logout():
    session.pop("student_id",None); session.pop("student_name",None)
    return redirect(url_for("index"))

# ═════════════════════════════════════════════════════════════════════════════
#  STUDENT DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
@app.route("/student/dashboard")
@login_required
def student_dashboard():
    sid = session["student_id"]
    student  = students_col.find_one({"_id": ObjectId(sid)})
    resume   = resumes_col.find_one({"student_id": sid})
    skills   = list(skills_col.find({"student_id": sid}))
    certs    = list(certs_col.find({"student_id": sid}))
    ts_doc   = trust_scores_col.find_one({"student_id": sid})
    trust_score = ts_doc["score"] if ts_doc else 0

    # All jobs (for job board)
    all_jobs = list(jobs_col.find({"status": "open"}).sort("created_at", -1))
    for j in all_jobs:
        j["_id"] = str(j["_id"])
        app_doc = applications_col.find_one({"student_id": sid, "job_id": j["_id"]})
        j["applied"]     = bool(app_doc)
        j["app_status"]  = app_doc.get("status","") if app_doc else ""
        j["quiz_done"]   = app_doc.get("quiz_done", False) if app_doc else False

    # Applications
    my_apps = list(applications_col.find({"student_id": sid}))
    for a in my_apps:
        job = jobs_col.find_one({"_id": ObjectId(a["job_id"])})
        a["job"] = job

    return render_template("student_dashboard.html",
        student=student, resume=resume, skills=skills, certs=certs,
        trust_score=trust_score, all_jobs=all_jobs, my_apps=my_apps,
        skill_names=json.dumps([s["skill_name"] for s in skills]),
        skill_scores=json.dumps([s.get("quiz_score",0) for s in skills]),
        skill_status=json.dumps([s.get("verified_status","unverified") for s in skills]),
    )

# ── Resume upload ─────────────────────────────────────────────────────────────
@app.route("/student/upload_resume", methods=["POST"])
@login_required
def upload_resume():
    sid = session["student_id"]
    if "resume" not in request.files:
        flash("No file selected.", "danger"); return redirect(url_for("student_dashboard"))
    f = request.files["resume"]
    if not f.filename or not allowed_file(f.filename):
        flash("Only PDF/DOCX allowed.", "danger"); return redirect(url_for("student_dashboard"))
    filename = secure_filename(f"{sid}_{f.filename}")
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    f.save(save_path)
    text = extract_text(save_path)
    edu, exp, sk_found, c_found = parse_resume(text)
    students_col.update_one({"_id": ObjectId(sid)}, {"$set": {"resume_path": filename}})
    resumes_col.update_one({"student_id": sid},
        {"$set": {"student_id":sid,"education":edu,"experience":exp,
                  "skills":sk_found,"certificates":c_found,
                  "raw_text":text[:2000],"uploaded_at":datetime.utcnow()}}, upsert=True)
    for sk in sk_found:
        if not skills_col.find_one({"student_id": sid, "skill_name": sk}):
            skills_col.insert_one({"student_id":sid,"skill_name":sk,
                "verified_status":"unverified","quiz_score":0,"created_at":datetime.utcnow()})
    recalculate_trust(sid)
    flash(f"Resume uploaded! Found {len(sk_found)} skills.", "success")
    return redirect(url_for("student_dashboard"))

# ── Certificate management ────────────────────────────────────────────────────
@app.route("/student/add_cert", methods=["POST"])
@login_required
def add_cert():
    sid = session["student_id"]
    cert_name = request.form.get("cert_name","").strip()
    cert_num  = request.form.get("cert_number","").strip()
    if not cert_name or not cert_num:
        flash("Certificate name and ID are required.", "danger")
        return redirect(url_for("student_dashboard"))
    status, provider = validate_cert(cert_name, cert_num)
    certs_col.insert_one({"student_id":sid,"cert_name":cert_name,
        "cert_number":cert_num,"verified_status":status,
        "provider":provider,"added_at":datetime.utcnow()})
    recalculate_trust(sid)
    icon = "✅" if status == "verified" else "⚠️"
    flash(f"Certificate {icon} {status.capitalize()} ({provider})", "success" if status=="verified" else "warning")
    return redirect(url_for("student_dashboard"))

# ── Job application ───────────────────────────────────────────────────────────
@app.route("/student/apply/<job_id>", methods=["POST"])
@login_required
def apply_job(job_id):
    sid = session["student_id"]
    if applications_col.find_one({"student_id": sid, "job_id": job_id}):
        flash("Already applied.", "info"); return redirect(url_for("student_dashboard"))
    job = jobs_col.find_one({"_id": ObjectId(job_id)})
    if not job:
        flash("Job not found.", "danger"); return redirect(url_for("student_dashboard"))
    applications_col.insert_one({"student_id":sid,"job_id":job_id,
        "job_title":job.get("title",""),"status":"applied",
        "quiz_done":False,"quiz_score":0,"trust_score":0,
        "applied_at":datetime.utcnow()})
    flash(f"Applied for {job['title']}! Take the skill quiz to boost your Trust Score.", "success")
    return redirect(url_for("student_dashboard"))

# ── Skill quiz (context-aware: generic or job-specific) ──────────────────────
@app.route("/student/quiz/<skill_name>")
@app.route("/student/quiz/<skill_name>/<job_id>")
@login_required
def skill_quiz(skill_name, job_id=None):
    questions = list(quizzes_col.find(
        {"skill_name": {"$regex": f"^{re.escape(skill_name)}$", "$options":"i"}}))[:5]
    if not questions:
        flash(f"No quiz for '{skill_name}' yet.", "warning")
        return redirect(url_for("student_dashboard"))
    for q in questions: q["_id"] = str(q["_id"])
    return render_template("quiz.html", skill_name=skill_name,
                           questions=questions, job_id=job_id)

@app.route("/student/quiz/<skill_name>/submit", methods=["POST"])
@app.route("/student/quiz/<skill_name>/<job_id>/submit", methods=["POST"])
@login_required
def submit_quiz(skill_name, job_id=None):
    sid = session["student_id"]
    questions = list(quizzes_col.find(
        {"skill_name": {"$regex": f"^{re.escape(skill_name)}$", "$options":"i"}}))[:5]
    correct = sum(1 for q in questions
                  if request.form.get(f"q_{str(q['_id'])}","").upper() == q["correctAnswer"].upper())
    total = len(questions)
    score_pct = round(correct / total * 100) if total else 0
    passed    = score_pct >= 70
    status    = "verified" if passed else "unverified"

    skills_col.update_one(
        {"student_id":sid,"skill_name":{"$regex":f"^{re.escape(skill_name)}$","$options":"i"}},
        {"$set":{"verified_status":status,"quiz_score":score_pct}})
    quiz_results_col.insert_one({"student_id":sid,"skill_name":skill_name,
        "score":score_pct,"status":status,"correct":correct,"total":total,
        "job_id":job_id,"taken_at":datetime.utcnow()})

    if job_id:
        ts = recalculate_trust(sid)
        applications_col.update_one(
            {"student_id":sid,"job_id":job_id},
            {"$set":{"quiz_done":True,"quiz_score":score_pct,"trust_score":ts,
                     "quiz_skill":skill_name,"status":"quiz_completed"}})

    recalculate_trust(sid)
    return render_template("quiz_result.html", skill_name=skill_name,
        score=score_pct, correct=correct, total=total, passed=passed, job_id=job_id)

# ═════════════════════════════════════════════════════════════════════════════
#  RECRUITER AUTH
# ═════════════════════════════════════════════════════════════════════════════
@app.route("/recruiter/register", methods=["GET","POST"])
def recruiter_register():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        company = request.form.get("company","").strip()
        password = request.form.get("password","")
        if not name or not email or not password:
            flash("All fields required.","danger"); return redirect(url_for("recruiter_register"))
        if recruiters_col.find_one({"email":email}):
            flash("Email already registered.","danger"); return redirect(url_for("recruiter_register"))
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        r = recruiters_col.insert_one({"name":name,"email":email,"company":company,
            "password":hashed,"created_at":datetime.utcnow()})
        session["recruiter_id"] = str(r.inserted_id); session["recruiter_name"] = name
        session["recruiter_company"] = company
        flash("Account created!","success"); return redirect(url_for("recruiter_dashboard"))
    return render_template("recruiter_register.html")

@app.route("/recruiter/login", methods=["GET","POST"])
def recruiter_login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        rec = recruiters_col.find_one({"email":email})
        if rec and bcrypt.check_password_hash(rec["password"],password):
            session["recruiter_id"] = str(rec["_id"]); session["recruiter_name"] = rec["name"]
            session["recruiter_company"] = rec.get("company","")
            flash(f"Welcome, {rec['name']}!","success"); return redirect(url_for("recruiter_dashboard"))
        flash("Invalid credentials.","danger")
    return render_template("recruiter_login.html")

@app.route("/recruiter/logout")
def recruiter_logout():
    session.pop("recruiter_id",None); session.pop("recruiter_name",None)
    session.pop("recruiter_company",None)
    return redirect(url_for("index"))

# ── Post a job ────────────────────────────────────────────────────────────────
@app.route("/recruiter/post_job", methods=["POST"])
@recruiter_required
def post_job():
    rid = session["recruiter_id"]
    title       = request.form.get("title","").strip()
    description = request.form.get("description","").strip()
    skills_req  = [s.strip() for s in request.form.get("skills_required","").split(",") if s.strip()]
    location    = request.form.get("location","").strip()
    salary      = request.form.get("salary","").strip()
    job_type    = request.form.get("job_type","Full-time")
    if not title:
        flash("Job title is required.","danger"); return redirect(url_for("recruiter_dashboard"))
    jobs_col.insert_one({"recruiter_id":rid,
        "company":session.get("recruiter_company",""),
        "title":title,"description":description,
        "skills_required":skills_req,"location":location,
        "salary":salary,"job_type":job_type,
        "status":"open","created_at":datetime.utcnow()})
    flash(f"Job '{title}' posted!","success")
    return redirect(url_for("recruiter_dashboard"))

# ── Recruiter dashboard ───────────────────────────────────────────────────────
@app.route("/recruiter/dashboard")
@recruiter_required
def recruiter_dashboard():
    rid = session["recruiter_id"]
    my_jobs = list(jobs_col.find({"recruiter_id":rid}).sort("created_at",-1))
    for j in my_jobs:
        j["_id"] = str(j["_id"])
        j["applicant_count"] = applications_col.count_documents({"job_id":j["_id"]})
    selected_job_id = request.args.get("job_id","")
    skill_filter = request.args.get("skill","").strip()
    min_score    = request.args.get("min_score",0,type=int)
    sort_by      = request.args.get("sort","trust_score")

    candidates = []
    selected_job = None
    if selected_job_id:
        selected_job = jobs_col.find_one({"_id":ObjectId(selected_job_id)})
        apps = list(applications_col.find({"job_id":selected_job_id}))
        for app_doc in apps:
            sid = app_doc["student_id"]
            student = students_col.find_one({"_id":ObjectId(sid)},{"password":0})
            if not student: continue
            ts_doc = trust_scores_col.find_one({"student_id":sid})
            trust_score = ts_doc["score"] if ts_doc else 0
            if trust_score < min_score: continue
            s_skills = list(skills_col.find({"student_id":sid}))
            s_certs  = list(certs_col.find({"student_id":sid}))
            resume   = resumes_col.find_one({"student_id":sid})
            quiz_results = list(quiz_results_col.find({"student_id":sid}).sort("taken_at",1))

            if skill_filter:
                matched = any(skill_filter.lower() in sk["skill_name"].lower()
                              and sk["verified_status"]=="verified" for sk in s_skills)
                if not matched: continue

            # Career trajectory: quiz score history over time
            trajectory = [{"date":str(q["taken_at"])[:10],"score":q["score"],"skill":q["skill_name"]}
                          for q in quiz_results]

            # Skills radar: group by verified status
            verified_count   = sum(1 for s in s_skills if s.get("verified_status")=="verified")
            unverified_count = len(s_skills) - verified_count

            candidates.append({
                "id":str(student["_id"]), "name":student.get("name",""),
                "email":student.get("email",""), "trust_score":trust_score,
                "skills":s_skills, "certs":s_certs, "resume":resume,
                "app_status":app_doc.get("status","applied"),
                "quiz_score":app_doc.get("quiz_score",0),
                "quiz_skill":app_doc.get("quiz_skill",""),
                "applied_at":str(app_doc.get("applied_at",""))[:10],
                "trajectory":trajectory, "verified_count":verified_count,
                "unverified_count":unverified_count,
            })

        # Sort
        if sort_by == "trust_score":
            candidates.sort(key=lambda x: x["trust_score"], reverse=True)
        elif sort_by == "name":
            candidates.sort(key=lambda x: x["name"])
        elif sort_by == "quiz_score":
            candidates.sort(key=lambda x: x["quiz_score"], reverse=True)

    return render_template("recruiter_dashboard.html",
        my_jobs=my_jobs, selected_job=selected_job,
        selected_job_id=selected_job_id, candidates=candidates,
        skill_filter=skill_filter, min_score=min_score, sort_by=sort_by,
    )

# ── Candidate detail (AJAX JSON) ──────────────────────────────────────────────
@app.route("/recruiter/candidate/<sid>/json")
@recruiter_required
def candidate_json(sid):
    student  = students_col.find_one({"_id":ObjectId(sid)},{"password":0})
    skills   = list(skills_col.find({"student_id":sid}))
    certs    = list(certs_col.find({"student_id":sid}))
    ts_doc   = trust_scores_col.find_one({"student_id":sid})
    quiz_results = list(quiz_results_col.find({"student_id":sid}).sort("taken_at",1))
    resume   = resumes_col.find_one({"student_id":sid},{"_id":0,"raw_text":0})

    trajectory = [{"date":str(q["taken_at"])[:10],"score":q["score"],"skill":q["skill_name"]}
                  for q in quiz_results]
    skill_radar = [{"skill":s["skill_name"],"score":s.get("quiz_score",0),
                    "verified":s.get("verified_status","unverified")=="verified"} for s in skills]

    return jsonify({
        "name": student.get("name",""),
        "email": student.get("email",""),
        "trust_score": ts_doc["score"] if ts_doc else 0,
        "skills": skill_radar,
        "certs": [{"name":c["cert_name"],"number":c["cert_number"],
                   "status":c["verified_status"],"provider":c.get("provider","")} for c in certs],
        "trajectory": trajectory,
        "resume": resume if resume else {},
    })

if __name__ == "__main__":
    os.makedirs(os.path.join("static","uploads"), exist_ok=True)
    print("🚀 ResumeVis 2.0 → http://127.0.0.1:5000")
    app.run(debug=True)
