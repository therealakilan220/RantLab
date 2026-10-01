"""Generate a comprehensive, granular PDF task sheet with individual task breakdowns for every teammate."""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
    PageBreak,
)

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "docs" / "admin-portal-task-sheet.pdf"

doc = SimpleDocTemplate(
    str(PDF_PATH),
    pagesize=letter,
    leftMargin=32,
    rightMargin=32,
    topMargin=32,
    bottomMargin=32,
)

styles = getSampleStyleSheet()

# Colors
PRIMARY = colors.HexColor("#0d6b5f")
DARK_INK = colors.HexColor("#15212b")
MUTED = colors.HexColor("#5b6a77")
LIGHT_BG = colors.HexColor("#f8fafc")
CARD_BG = colors.HexColor("#f1f5f9")
LINE = colors.HexColor("#cbd5e1")
AKILAN_CLR = colors.HexColor("#0b6e99")
ARVIND_CLR = colors.HexColor("#a85a0c")
JAYASREE_CLR = colors.HexColor("#2c7a4b")
PRIYAN_CLR = colors.HexColor("#7b3fb3")

# Paragraph Styles
title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    textColor=DARK_INK,
    spaceAfter=3,
)

sub_style = ParagraphStyle(
    "DocSub",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=MUTED,
    spaceAfter=8,
)

h2_style = ParagraphStyle(
    "SectionH2",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=16,
    textColor=PRIMARY,
    spaceBefore=8,
    spaceAfter=4,
)

h3_style = ParagraphStyle(
    "SectionH3",
    parent=styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=14,
    textColor=DARK_INK,
    spaceBefore=6,
    spaceAfter=3,
)

normal_style = ParagraphStyle(
    "DocNormal",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8,
    leading=11,
    textColor=DARK_INK,
)

bold_label = ParagraphStyle(
    "BoldLabel",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=11,
    textColor=DARK_INK,
)

task_title_style = ParagraphStyle(
    "TaskTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8.5,
    leading=11,
    textColor=DARK_INK,
)

task_desc_style = ParagraphStyle(
    "TaskDesc",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=7.5,
    leading=10.5,
    textColor=MUTED,
)

meta_style = ParagraphStyle(
    "TaskMeta",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=7.5,
    leading=9.5,
    textColor=PRIMARY,
)

story = []

# Title Banner
story.append(Paragraph("RantLab: Domain Admin Portal & Mobile Alert System", title_style))
story.append(
    Paragraph(
        "<b>Task Sheet & Engineering Work Breakdown</b> | Domain Portals (Library, Hostel, Mess, IT) • Mobile Push Notifications • Semantic Grouping",
        sub_style,
    )
)
story.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=6))

# Section 1: Overview & Team Ownership
story.append(Paragraph("1. Feature Overview & Ownership Matrix", h2_style))

overview_text = (
    "This task adds a multi-domain administrator portal with real-time mobile push notifications. "
    "When students submit complaints, the AI pipeline automatically categorizes the domain (Library, Hostel, Mess, IT), "
    "clusters similar issues, alerts the respective domain administrator on their phone, and provides a unified dashboard to review and resolve grouped complaints."
)
story.append(Paragraph(overview_text, normal_style))
story.append(Spacer(1, 4))

team_data = [
    [
        Paragraph("<b>Member</b>", normal_style),
        Paragraph("<b>Role & Files Owned</b>", normal_style),
        Paragraph("<b>Core Deliverables for this Feature</b>", normal_style),
    ],
    [
        Paragraph(f"<font color='{AKILAN_CLR.hexval()}'><b>Akilan</b></font><br/><i>Lead Architect</i>", normal_style),
        Paragraph("<code>backend/app/main.py</code><br/><code>backend/app/llm.py</code><br/><code>backend/app/models.py</code><br/><code>docs/api-contract.md</code>", normal_style),
        Paragraph("• API Contract & Pydantic models for domain/status<br/>• LLM domain extraction prompt & fallback logic<br/>• Admin REST endpoints (<code>GET /api/admin/...</code>, <code>PATCH status</code>)<br/>• Public resolution feedback on card page", normal_style),
    ],
    [
        Paragraph(f"<font color='{ARVIND_CLR.hexval()}'><b>Arvind</b></font><br/><i>AI & DB Lead</i>", normal_style),
        Paragraph("<code>backend/app/db.py</code><br/><code>backend/app/cluster.py</code><br/><code>backend/app/embed.py</code><br/><code>backend/app/notify.py</code>", normal_style),
        Paragraph("• SQLite schema migration (domain, status, subscriptions table)<br/>• Domain-scoped clustering engine<br/>• Cluster representative & metrics computation<br/>• WebPush & Telegram notification dispatcher", normal_style),
    ],
    [
        Paragraph(f"<font color='{JAYASREE_CLR.hexval()}'><b>Jayasree</b></font><br/><i>Frontend Lead</i>", normal_style),
        Paragraph("<code>frontend/app/admin/</code><br/><code>frontend/components/</code><br/><code>frontend/lib/api.ts</code><br/><code>frontend/lib/types.ts</code>", normal_style),
        Paragraph("• Responsive Mobile Admin Portal (<code>/admin/[domain]</code>)<br/>• Grouped / Clustered Accordion component<br/>• Mobile WebPush permission & subscription prompt<br/>• Action controls (In-Progress / Resolve) with toast feedback", normal_style),
    ],
    [
        Paragraph(f"<font color='{PRIYAN_CLR.hexval()}'><b>Priyan</b></font><br/><i>QA & Demo Lead</i>", normal_style),
        Paragraph("<code>data/seed.json</code><br/><code>scripts/</code><br/><code>backend/tests/</code><br/><code>docs/</code>", normal_style),
        Paragraph("• 30+ domain-specific seed complaints across all domains<br/>• Automated pytest suite for admin endpoints & clustering<br/>• Notification simulation script (<code>test_push_alert.py</code>)<br/>• End-to-end demo rehearsal & verification", normal_style),
    ],
]

t_team = Table(team_data, colWidths=[90, 210, 245])
t_team.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])
)
story.append(t_team)
story.append(Spacer(1, 6))

# Section 2: Phase Timeline
story.append(Paragraph("2. Master Phase Schedule", h2_style))

phases = [
    ("Phase 1: Architecture & Contracts", "All", "1.5h", "API contract locked, SQLite schema migrated, seed complaints created, frontend types aligned."),
    ("Phase 2: Core Domain Logic & Clustering", "Akilan & Arvind", "2.5h", "LLM prompt extracts domain, cluster engine groups per domain, admin endpoints ready."),
    ("Phase 3: Admin UI & Mobile WebPush", "Jayasree & Arvind", "3.0h", "Mobile admin dashboard built, cluster accordions functional, WebPush alerts active."),
    ("Phase 4: Feedback Loop, QA & Live Demo", "Priyan & All", "2.0h", "Status updates sync back to students, push alert test script passes, live demo rehearsed."),
]

phase_table_data = [[
    Paragraph("<b>Phase & Milestone</b>", normal_style),
    Paragraph("<b>Owner(s)</b>", normal_style),
    Paragraph("<b>Est. Time</b>", normal_style),
    Paragraph("<b>Target Output & Checkpoint</b>", normal_style),
]]

for p_title, p_owner, p_est, p_desc in phases:
    phase_table_data.append([
        Paragraph(f"<b>{p_title}</b>", normal_style),
        Paragraph(p_owner, bold_label),
        Paragraph(p_est, meta_style),
        Paragraph(p_desc, task_desc_style),
    ])

t_phase = Table(phase_table_data, colWidths=[130, 95, 50, 270])
t_phase.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])
)
story.append(t_phase)
story.append(Spacer(1, 6))

# Page Break for Detailed Member Work Breakdown
story.append(PageBreak())

# Section 3: Detailed Tasks by Teammate
story.append(Paragraph("3. Detailed Task Breakdown by Teammate", h2_style))

# Akilan's Task Details
akilan_tasks = [
    (
        "A1. API Contract & Data Models",
        "docs/api-contract.md<br/>backend/app/models.py",
        "1.0h",
        "Define Domain literal ('library' | 'hostel' | 'mess' | 'it_infra' | 'academics' | 'general') and Status ('new' | 'in_progress' | 'resolved'). Add AdminCard, AdminCluster, and UpdateStatusPayload schemas.",
        "Models import cleanly; contract diff posted in team chat.",
    ),
    (
        "A2. LLM Domain Classification & Urgency",
        "backend/app/llm.py",
        "2.0h",
        "Update the fix-generation prompt to output 'domain' and 'urgency' ('low' | 'medium' | 'high'). Add keyword-based heuristic fallback in STUB_MODE=1 so frontend dev works seamlessly offline.",
        "POST /api/rant returns validated domain tag under 10s.",
    ),
    (
        "A3. Admin Endpoints Implementation",
        "backend/app/main.py",
        "2.0h",
        "Create GET /api/admin/{domain}/cards with ?status= filter and cluster metadata. Create PATCH /api/admin/cards/{id}/status to transition complaint lifecycle.",
        "Endpoints return correct filtered JSON and handle invalid domains with HTTP 400/404.",
    ),
    (
        "A4. Public Resolution Feedback Loop",
        "backend/app/main.py",
        "1.0h",
        "Update GET /api/card/{id} to return resolution status and optional admin note so students can track progress.",
        "Student card view reflects updated status immediately.",
    ),
]

# Arvind's Task Details
arvind_tasks = [
    (
        "B1. DB Schema Migration & Subscriptions",
        "backend/app/db.py",
        "1.5h",
        "Add 'domain TEXT', 'status TEXT DEFAULT \"new\"', and 'resolved_at TIMESTAMP' columns to cards table. Create 'admin_subscriptions' table (id, domain, push_subscription_json, created_at).",
        "Database initializes with new columns without breaking seed loader.",
    ),
    (
        "B2. Domain-Scoped Clustering Algorithm",
        "backend/app/cluster.py",
        "2.0h",
        "Update cluster(items, threshold) to partition embeddings by domain first, ensuring hostel complaints never cluster with library complaints.",
        "Clustering returns domain-specific cluster IDs ('k_hostel_01', 'k_lib_02').",
    ),
    (
        "B3. Cluster Representative & Summaries",
        "backend/app/cluster.py<br/>backend/app/embed.py",
        "1.5h",
        "Compute cluster card count, most representative central complaint using most_central(), and aggregate urgency level.",
        "GET /api/admin/{domain}/clusters returns grouped summaries with card counts.",
    ),
    (
        "B4. Mobile Push Dispatch Engine",
        "backend/app/notify.py",
        "2.5h",
        "Build notification dispatcher using WebPush (pywebpush) with Telegram bot fallback. Trigger alerts on new complaint arrival or cluster threshold >= 3.",
        "Test script successfully sends push payload to registered admin subscription.",
    ),
]

# Jayasree's Task Details
jayasree_tasks = [
    (
        "C1. Admin Dashboard Page (/admin/[domain])",
        "frontend/app/admin/[domain]/page.tsx<br/>frontend/lib/api.ts",
        "2.5h",
        "Build mobile-first admin dashboard with domain switcher, summary stat cards (Active, Grouped, In Progress, Resolved), and status filters.",
        "Dashboard renders on mobile screen with zero horizontal overflow.",
    ),
    (
        "C2. Grouped Cluster Accordion View",
        "frontend/components/ClusterAccordion.tsx",
        "2.5h",
        "Build expandable accordion cards showing: Cluster Problem Title, Affected Count Badge (e.g. '8 students'), expanded list of rants, and 3 AI Recommended Fixes.",
        "Accordion expands smoothly; displays individual transcripts and timestamps.",
    ),
    (
        "C3. Mobile Push Opt-in Component",
        "frontend/components/PushNotificationModal.tsx",
        "1.5h",
        "Create 'Enable Mobile Alerts' modal requesting browser Notification & ServiceWorker permissions. Send subscription payload to POST /api/admin/subscribe.",
        "Admins can toggle notifications on/off from mobile browser.",
    ),
    (
        "C4. Status Action Controls & Toast Feedback",
        "frontend/components/StatusActionBar.tsx",
        "1.5h",
        "Add quick action buttons: 'Mark In Progress', 'Resolve Cluster', and 'Assign Fix'. Trigger optimistic UI update with instant toast confirmation.",
        "Clicking resolve marks all cards in cluster as resolved with live feedback.",
    ),
]

# Priyan's Task Details
priyan_tasks = [
    (
        "D1. Domain Seed Dataset Creation",
        "data/seed.json<br/>scripts/load_seed.py",
        "1.5h",
        "Create 30+ realistic domain-specific complaints: 8 Hostel (Wi-Fi, water, hygiene), 8 Library (AC, noise, books), 8 Mess (food quality, queues), 6 IT (lab PCs, portal).",
        "load_seed.py populates DB with pre-tagged domains and vectors.",
    ),
    (
        "D2. Admin API Automated Test Suite",
        "backend/tests/test_admin_api.py",
        "1.5h",
        "Write pytest test suite covering: domain filtering, cluster isolation across domains, status update transitions, and subscription registration.",
        "pytest backend/tests/ passes with 100% success rate.",
    ),
    (
        "D3. Push Alert Simulation Script",
        "scripts/test_push_alert.py",
        "1.5h",
        "Create a CLI test script that posts a synthetic complaint, triggers the notification engine, and validates delivery in < 2 seconds.",
        "CLI outputs clear confirmation of notification dispatch.",
    ),
    (
        "D4. Live Demo Flow & Rehearsal",
        "docs/demo_walkthrough.md",
        "1.5h",
        "Prepare the live demo script: 1) Student rants on phone, 2) Library admin receives instant push alert, 3) Admin opens clustered portal, 4) Admin picks AI fix.",
        "Team completes seamless 5-minute rehearsal without blockers.",
    ),
]

def render_member_section(name, role, color, file_list, task_list):
    section_elems = []
    section_elems.append(Paragraph(f"<font color='{color.hexval()}'><b>■ {name} — {role}</b></font>", h3_style))
    section_elems.append(Paragraph(f"<b>Owned Files:</b> <code>{file_list}</code>", sub_style))
    
    rows = [[
        Paragraph("<b>Task & Deliverable</b>", normal_style),
        Paragraph("<b>Est.</b>", normal_style),
        Paragraph("<b>Technical Details & Implementation Steps</b>", normal_style),
        Paragraph("<b>Acceptance Criteria</b>", normal_style),
    ]]
    
    for title, files, duration, details, crit in task_list:
        rows.append([
            Paragraph(f"<b>{title}</b>", task_title_style),
            Paragraph(duration, meta_style),
            Paragraph(details, normal_style),
            Paragraph(f"<i>{crit}</i>", task_desc_style),
        ])
        
    t_sec = Table(rows, colWidths=[120, 35, 230, 160])
    t_sec.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BG),
            ("GRID", (0, 0), (-1, -1), 0.5, LINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])
    )
    section_elems.append(t_sec)
    section_elems.append(Spacer(1, 6))
    return KeepTogether(section_elems)

story.append(render_member_section("Akilan", "Pipeline, LLM Prompt & API Integration", AKILAN_CLR, "main.py, llm.py, models.py, docs/api-contract.md", akilan_tasks))
story.append(render_member_section("Arvind", "Database, Clustering & Notification Engine", ARVIND_CLR, "db.py, cluster.py, embed.py, notify.py", arvind_tasks))
story.append(PageBreak())
story.append(render_member_section("Jayasree", "Frontend & Mobile Admin Portal UI", JAYASREE_CLR, "frontend/app/admin/, components/, lib/api.ts", jayasree_tasks))
story.append(render_member_section("Priyan", "QA, Test Data, Simulation & Demo Lead", PRIYAN_CLR, "data/seed.json, scripts/, backend/tests/", priyan_tasks))

# Section 4: Acceptance Checklist
story.append(Spacer(1, 4))
story.append(Paragraph("4. Feature Definition of Done (DoD)", h2_style))

dod_items = [
    "<b>Domain Classification:</b> Every complaint is accurately tagged to one of: Library, Hostel, Mess, IT, Academics, or General.",
    "<b>Domain Clustering:</b> Similar complaints cluster together only within their respective domain (no cross-domain grouping).",
    "<b>Mobile Notifications:</b> Domain admins receive an immediate phone push alert when a new complaint is filed or when a cluster reaches $\\ge 3$ complaints.",
    "<b>Admin Portal Experience:</b> Admins can filter by status (New, In Progress, Resolved) and expand clusters to see all individual rants and AI fixes.",
    "<b>Feedback Loop:</b> Resolving an issue in the admin portal automatically updates the status seen by students on their public card view.",
]

dod_data = [[Paragraph(f"• {item}", normal_style)] for item in dod_items]
t_dod = Table(dod_data, colWidths=[545])
t_dod.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])
)
story.append(t_dod)

# Footer Note
story.append(Spacer(1, 6))
story.append(HRFlowable(width="100%", thickness=0.5, color=LINE, spaceAfter=4))
story.append(
    Paragraph(
        "<b>RantLab Engineering Documentation</b> | Team Fantastic 4 | <i>Small PRs, rebase often, keep main green.</i>",
        sub_style,
    )
)

doc.build(story)
print(f"Generated comprehensive task sheet PDF at: {PDF_PATH}")
