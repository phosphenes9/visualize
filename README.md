# ResumeVis 2.0 — Verified Talent Platform

A full-stack Flask web application that turns static resumes into verified talent profiles using skill quizzes, certificate validation, and a transparent Trust Score system.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- MongoDB Atlas account (free tier works)

### 2. Clone / extract project
```bash
cd resumevis
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and add your MongoDB Atlas URI and a secret key
```

Your `.env` file:
```
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/resumevis?retryWrites=true&w=majority
SECRET_KEY=change-this-to-a-random-string
```

### 5. Run
```bash
python app.py
```

Open → http://127.0.0.1:5000

---

## 🗂 Project Structure

```
resumevis/
├── app.py                  # Main Flask app (routes + logic)
├── requirements.txt
├── .env.example
├── static/
│   └── uploads/            # Uploaded resume files
└── templates/
    ├── base.html           # Base layout + shared styles
    ├── index.html          # Landing page
    ├── student_register.html
    ├── student_login.html
    ├── student_dashboard.html  # Main student view
    ├── quiz.html           # Skill MCQ quiz
    ├── quiz_result.html    # Quiz score result
    ├── recruiter_register.html
    ├── recruiter_login.html
    ├── recruiter_dashboard.html  # Candidate search
    └── candidate_profile.html   # Full candidate view
```

---

## 🎓 Student Features

| Feature | Details |
|---|---|
| Resume Upload | PDF / DOCX, auto-parses Education, Experience, Skills |
| Skill Verification | MCQ quiz per skill, pass ≥ 70% → Verified ✅ |
| Certificate Validation | Add Coursera / AWS / NPTEL IDs, format-based validation |
| Trust Score | Live composite score: Degree(40) + Certs(40) + Skills(20) |
| Visualizations | Skill bar chart + verification doughnut via Chart.js |

## 💼 Recruiter Features

| Feature | Details |
|---|---|
| Candidate Search | Filter by verified skill, minimum Trust Score, certification |
| Profile View | Full resume breakdown with charts and verified badges |
| Trust Score Ranking | Candidates sorted by score descending |

---

## 📊 Database Schema (MongoDB Collections)

| Collection | Key Fields |
|---|---|
| `students` | name, email, password (hashed), resume_path |
| `resumes` | student_id, education[], experience[], skills[], certificates[] |
| `skills` | student_id, skill_name, verified_status, quiz_score |
| `certificates` | student_id, cert_name, cert_number, verified_status |
| `quizzes` | skill_name, question, optionA-D, correctAnswer |
| `quiz_results` | student_id, skill_name, score, status, correct, total |
| `trust_scores` | student_id, score |
| `recruiters` | name, email, company, password (hashed) |

---

## 🧠 Trust Score Formula

```
Trust Score = Degree Points + Certificate Points + Skill Points

Degree Points:     +40  (if resume has education section)
Certificate Points: +20 per verified cert (max 40)
Skill Points:      +10 per verified skill  (max 20)
Maximum Score:     100
```

---

## 📚 Pre-loaded Quiz Skills

Quizzes are auto-seeded on first run for:
- **Python** (3 questions)
- **JavaScript** (3 questions)
- **SQL** (3 questions)
- **Machine Learning** (3 questions)
- **Data Analysis** (3 questions)

---

## 🔐 Certificate ID Validation Rules

| Provider | Pattern |
|---|---|
| Coursera | 8–12 uppercase alphanumeric |
| AWS | 12–16 uppercase alphanumeric |
| NPTEL | Starts with `NPTEL` + 8–15 alphanumeric |
| Generic | 8+ alphanumeric characters |

---

## 🛠 Tech Stack

- **Backend**: Flask 3.0, PyMongo, Flask-Bcrypt
- **Database**: MongoDB Atlas
- **Frontend**: Bootstrap 5.3, Chart.js 4.4
- **Fonts**: Syne (headings) + DM Sans (body)
- **Parsing**: PyPDF2, python-docx
