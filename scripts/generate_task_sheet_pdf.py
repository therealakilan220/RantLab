"""Generate a comprehensive PDF version of docs/rantlab-task-sheet.html including individual member work breakdowns using reportlab."""
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, PageBreak

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "docs" / "rantlab-task-sheet.pdf"

doc = SimpleDocTemplate(
    str(PDF_PATH),
    pagesize=letter,
    leftMargin=36,
    rightMargin=36,
    topMargin=36,
    bottomMargin=36
)

styles = getSampleStyleSheet()

# Custom Palette
PRIMARY = colors.HexColor("#0d6b5f")
DARK_INK = colors.HexColor("#15212b")
MUTED = colors.HexColor("#5b6a77")
LIGHT_BG = colors.HexColor("#f8fafc")
LINE = colors.HexColor("#cbd5e1")
P1_COLOR = colors.HexColor("#0b6e99")
P2_COLOR = colors.HexColor("#a85a0c")
P3_COLOR = colors.HexColor("#2c7a4b")
P4_COLOR = colors.HexColor("#7b3fb3")

title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=26,
    textColor=DARK_INK,
    spaceAfter=4
)

sub_style = ParagraphStyle(
    "DocSub",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10,
    leading=14,
    textColor=MUTED,
    spaceAfter=12
)

h2_style = ParagraphStyle(
    "SectionH2",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=18,
    textColor=PRIMARY,
    spaceBefore=10,
    spaceAfter=6
)

h3_style = ParagraphStyle(
    "SectionH3",
    parent=styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=16,
    textColor=DARK_INK,
    spaceBefore=8,
    spaceAfter=4
)

normal_style = ParagraphStyle(
    "DocNormal",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=DARK_INK
)

task_title_style = ParagraphStyle(
    "TaskTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9.5,
    leading=12,
    textColor=DARK_INK
)

task_desc_style = ParagraphStyle(
    "TaskDesc",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    textColor=MUTED
)

meta_style = ParagraphStyle(
    "TaskMeta",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=10,
    textColor=PRIMARY
)

story = []

# Header
story.append(Paragraph("RantLab: 24-Hour Task Sheet", title_style))
story.append(Paragraph("<b>Team Fantastic 4 — Open Innovation Track (Online Demo)</b> | Free open-source stack (FastAPI, Next.js, Ollama, Whisper)", sub_style))
story.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=10))

# Team Summary Table
story.append(Paragraph("1. Team Overview & Owned Files", h2_style))

team_data = [
    [Paragraph("<b>Member & Role</b>", normal_style), Paragraph("<b>Key Responsibilities & Files Owned</b>", normal_style)],
    [Paragraph("<font color='#0b6e99'><b>Akilan</b></font><br/><i>Team Lead</i>", normal_style), Paragraph("Pipeline, LLM prompt, integration<br/><code>backend/app/main.py, llm.py, models.py, config.py, docs/api-contract.md</code>", normal_style)],
    [Paragraph("<font color='#a85a0c'><b>Arvind</b></font><br/><i>AI & DB</i>", normal_style), Paragraph("Speech to text, database, embeddings, clustering<br/><code>backend/app/stt.py, db.py, embed.py, cluster.py</code>", normal_style)],
    [Paragraph("<font color='#2c7a4b'><b>Jayasree</b></font><br/><i>Frontend & Demo Lead</i>", normal_style), Paragraph("Frontend: recorder UI, card view, share page, board (Drives live online demo)<br/><code>frontend/ (lib/api.ts, lib/types.ts, mocks/, app pages)</code>", normal_style)],
    [Paragraph("<font color='#7b3fb3'><b>Priyan</b></font><br/><i>QA & Demo Deck</i>", normal_style), Paragraph("Test data, evaluation rubric, bug log, deck & backup video<br/><code>data/, scripts/, backend/tests/, README.md</code>", normal_style)]
]

t_team = Table(team_data, colWidths=[140, 400])
t_team.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
    ('TEXTCOLOR', (0,0), (-1,0), DARK_INK),
    ('GRID', (0,0), (-1,-1), 0.5, LINE),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(t_team)
story.append(Spacer(1, 10))

# Master Task List by Phase
tasks_by_phase = [
    {
        "phase": "Setup (H0 to H1)",
        "checkpoint": "Checkpoint H1: Everyone can run the repo and their own tool locally.",
        "tasks": [
            ("Akilan", "0.5h", "Create repo & API contract", "Free GitHub repo, api-contract.md with JSON shape.", "MVP"),
            ("Akilan", "0.5h", "Install Ollama & pull qwen2.5:3b", "Test response time under 15s on local machine.", "MVP"),
            ("Arvind", "0.5h", "Install faster-whisper & ffmpeg", "Transcribe test clip on CPU. Pick tiny/base model.", "MVP"),
            ("Jayasree", "0.5h", "Scaffold Next.js, TS & Tailwind", "Setup project, code against mock JSON.", "MVP"),
            ("Priyan", "1.0h", "Write 40 campus complaints", "Save as seed.json with near-duplicates.", "MVP"),
        ]
    },
    {
        "phase": "Build the parts (H1 to H6)",
        "checkpoint": "Checkpoint H6: A typed complaint returns three fixes from the API.",
        "tasks": [
            ("Akilan", "3.0h", "Write fix-generation prompt", "Ollama JSON mode, pydantic validation, retry once.", "MVP"),
            ("Akilan", "1.5h", "FastAPI app POST /api/rant/text", "Text input in, card JSON output out with CORS.", "MVP"),
            ("Arvind", "2.0h", "Write transcribe(audio)", "Accept webm/ogg audio, convert with faster-whisper.", "MVP"),
            ("Arvind", "1.5h", "SQLite schema", "Cards, complaints, embeddings tables (anonymous).", "MVP"),
            ("Arvind", "1.5h", "Embedding helper", "Load MiniLM at startup, embed(text) vector helper.", "MVP"),
            ("Jayasree", "3.0h", "Record screen UI", "MediaRecorder, 30s cap, timer, typed option.", "MVP"),
            ("Jayasree", "2.0h", "Concept card component", "Problem, pattern, 3 fix rows (cost/timeframe).", "MVP"),
            ("Priyan", "1.5h", "Record 6 voice samples", "Different voices, noisy clip for Whisper test.", "MVP"),
            ("Priyan", "1.5h", "Evaluation rubric", "Score relevance, specificity, sensible owner.", "MVP"),
        ]
    },
    {
        "phase": "Wire it together (H6 to H12)",
        "checkpoint": "Checkpoint H12: Voice in the browser produces a card.",
        "tasks": [
            ("Akilan", "3.0h", "Full pipeline POST /api/rant", "Audio/text -> transcribe -> LLM -> save DB -> card.", "MVP"),
            ("Akilan", "1.0h", "Set up HTTPS tunnel", "Cloudflare Tunnel / ngrok for online mic access.", "MVP"),
            ("Arvind", "3.0h", "Clustering", "Cosine similarity grouping for Wi-Fi / canteen rants.", "MVP"),
            ("Jayasree", "2.0h", "Connect to real API", "Audio upload, loading stages (Transcribing/Thinking).", "MVP"),
            ("Jayasree", "2.0h", "Card page at /card/[id]", "Public link for online demo screen sharing.", "MVP"),
            ("Priyan", "3.0h", "Test model on 10 complaints", "Prompt evaluation as soon as prompt is ready.", "MVP"),
            ("Priyan", "2.0h", "README & architecture diagram", "Setup steps and flow diagram for online presentation.", "MVP"),
        ]
    },
    {
        "phase": "MVP Freeze & Testing (H12 to H16)",
        "checkpoint": "Checkpoint H16: Feature freeze. After this, only bug fixes.",
        "tasks": [
            ("Akilan", "2.0h", "Merge & fix top bugs", "Merge branches, run end-to-end QA fixes.", "MVP"),
            ("Akilan", "0.25h", "Tag v1-mvp", "Tag working build on Git for Jayasree's demo machine.", "MVP"),
            ("Arvind", "1.5h", "GET /api/board", "Return clusters with counts, labels, complaints.", "MVP"),
            ("Arvind", "1.5h", "Speed check", "Benchmark upload, STT, and LLM steps.", "MVP"),
            ("Jayasree", "1.5h", "Copy link / PNG download", "html-to-image package export.", "Stretch"),
            ("Jayasree", "1.5h", "Mobile & browser pass", "Safari/Chrome mic permissions check.", "MVP"),
            ("Priyan", "3.0h", "QA pass & bug log", "Stress test text, voice, online network conditions.", "MVP"),
            ("Priyan", "1.0h", "Privacy checklist", "Verify anonymous storage, short notice.", "MVP"),
        ]
    },
    {
        "phase": "Stretch & Polish (H16 to H20)",
        "checkpoint": "Checkpoint H20: Stop building. Nothing new after this.",
        "tasks": [
            ("Akilan", "2.0h", "Tune prompt on weak outputs", "Re-run test set, refine vague fixes & owners.", "MVP"),
            ("Akilan", "1.0h", "Model fallback switch", "Environment flag to switch to cloud API if needed.", "Stretch"),
            ("Arvind", "2.0h", "Handle messy audio", "Silence, noise, accents -> clear error message.", "MVP"),
            ("Arvind", "1.0h", "Rank recurring issues", "Sort clusters by recency and count.", "Stretch"),
            ("Jayasree", "3.0h", "Board page at /board", "List clusters with counts and complaints.", "Stretch"),
            ("Jayasree", "1.0h", "Polish states & branding", "Loading, empty states, logo, tagline.", "MVP"),
            ("Priyan", "2.0h", "Backup demo video", "90s OBS recording for screen-share fallback.", "MVP"),
            ("Priyan", "2.0h", "Visual concept for top fix", "Generate optional fix preview image.", "Stretch"),
        ]
    },
    {
        "phase": "Pitch Prep & Buffer (H20 to H24)",
        "checkpoint": "Rehearsals: Two full online 8-minute run-throughs, Jayasree driving demo screen.",
        "tasks": [
            ("Akilan", "3.0h", "Demo environment & team rehearsal", "Support Jayasree with backend setup, test slides 1-2.", "MVP"),
            ("Arvind", "2.5h", "Speaker 2 rehearsal & Tech Q&A", "Arvind rehearses slides 3-4 (Whisper, MiniLM).", "MVP"),
            ("Jayasree", "2.5h", "Online Demo Lead & Speaker 3", "Jayasree drives screen-share live demo under 60s.", "MVP"),
            ("Priyan", "3.0h", "Real numbers into slides & Speaker 4", "Priyan updates slide 7 metrics, team Q&A sheet.", "MVP"),
        ]
    }
]

story.append(Paragraph("2. 24-Hour Phase & Task Timeline", h2_style))

for section in tasks_by_phase:
    elems = []
    elems.append(Paragraph(f"<b>{section['phase']}</b> — <font color='{PRIMARY.hexval()}'><i>{section['checkpoint']}</i></font>", normal_style))
    
    table_data = [[
        Paragraph("<b>Member</b>", normal_style),
        Paragraph("<b>Task</b>", normal_style),
        Paragraph("<b>Detail</b>", normal_style),
        Paragraph("<b>Time</b>", normal_style),
        Paragraph("<b>Type</b>", normal_style)
    ]]
    
    for owner, duration, title, detail, ttype in section["tasks"]:
        owner_color = P1_COLOR if owner == "Akilan" else (P2_COLOR if owner == "Arvind" else (P3_COLOR if owner == "Jayasree" else P4_COLOR))
        type_str = f"<b><font color='{PRIMARY.hexval()}'>MVP</font></b>" if ttype == "MVP" else "<font color='#94a3b8'>Stretch</font>"
        table_data.append([
            Paragraph(f"<font color='{owner_color.hexval()}'><b>{owner}</b></font>", normal_style),
            Paragraph(title, task_title_style),
            Paragraph(detail, task_desc_style),
            Paragraph(duration, meta_style),
            Paragraph(type_str, normal_style)
        ])
    
    t_sec = Table(table_data, colWidths=[70, 150, 230, 45, 45])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, LINE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elems.append(t_sec)
    elems.append(Spacer(1, 8))
    story.append(KeepTogether(elems))

# NEW SECTION: INDIVIDUAL WORKSHEETS BY MEMBER
story.append(Spacer(1, 10))
story.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=10))
story.append(Paragraph("3. Individual Member Worksheets & Complete Task Lists", h2_style))
story.append(Paragraph("Comprehensive task list for each person across the entire 24-hour hackathon duration.", sub_style))

member_configs = [
    {
        "name": "Akilan",
        "role": "Team Lead: Backend, LLM Prompt & Integration",
        "color": P1_COLOR,
        "files": "backend/app/main.py, llm.py, models.py, config.py, docs/api-contract.md",
        "desc": "Responsible for overall architecture, API endpoints, Ollama LLM prompt engineering, response validation, and backend integration."
    },
    {
        "name": "Arvind",
        "role": "AI & DB Specialist: Speech, Embeddings & Clustering",
        "color": P2_COLOR,
        "files": "backend/app/stt.py, db.py, embed.py, cluster.py",
        "desc": "Responsible for local Speech-to-Text via faster-whisper, SQLite database storage, MiniLM vector embeddings, and complaint clustering."
    },
    {
        "name": "Jayasree",
        "role": "Frontend Lead & Online Demo Presenter",
        "color": P3_COLOR,
        "files": "frontend/ (lib/api.ts, lib/types.ts, mocks/, app pages)",
        "desc": "Responsible for Next.js web UI, audio recording interface, shareable card view, board UI, and driving the live screen-shared demo during online judging."
    },
    {
        "name": "Priyan",
        "role": "QA, Test Data, Privacy & Demo Deck Lead",
        "color": P4_COLOR,
        "files": "data/, scripts/, backend/tests/, README.md",
        "desc": "Responsible for seed dataset creation, prompt evaluation rubric, QA bug logging, backup demo video, slide deck preparation, and tech Q&A."
    },
]

for m in member_configs:
    m_name = m["name"]
    elems = []
    elems.append(Paragraph(f"Subtopic 3.{member_configs.index(m)+1}: <font color='{m['color'].hexval()}'><b>{m['name']}</b></font> — {m['role']}", h3_style))
    elems.append(Paragraph(f"<b>Files Owned:</b> <code>{m['files']}</code><br/><b>Overview:</b> {m['desc']}", normal_style))
    elems.append(Spacer(1, 4))

    # Collect all tasks for this person across all phases
    m_tasks_table = [[
        Paragraph("<b>Phase</b>", normal_style),
        Paragraph("<b>Task Name</b>", normal_style),
        Paragraph("<b>Detailed Instructions</b>", normal_style),
        Paragraph("<b>Hours</b>", normal_style),
        Paragraph("<b>Priority</b>", normal_style)
    ]]

    total_hours = 0.0
    for phase_info in tasks_by_phase:
        p_title = phase_info["phase"].split(" (")[0]
        for owner, duration, title, detail, ttype in phase_info["tasks"]:
            if owner == m_name:
                hrs_val = float(duration.replace("h", ""))
                total_hours += hrs_val
                type_str = f"<b><font color='{PRIMARY.hexval()}'>MVP</font></b>" if ttype == "MVP" else "<font color='#94a3b8'>Stretch</font>"
                m_tasks_table.append([
                    Paragraph(f"<b>{p_title}</b>", normal_style),
                    Paragraph(title, task_title_style),
                    Paragraph(detail, task_desc_style),
                    Paragraph(duration, meta_style),
                    Paragraph(type_str, normal_style)
                ])

    t_m = Table(m_tasks_table, colWidths=[80, 140, 220, 45, 55])
    t_m.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, LINE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elems.append(t_m)
    elems.append(Paragraph(f"<b>Total Allocated Hours:</b> {total_hours:.2f} hrs", meta_style))
    elems.append(Spacer(1, 10))
    story.append(KeepTogether(elems))

doc.build(story)
print(f"Generated PDF: {PDF_PATH}")
