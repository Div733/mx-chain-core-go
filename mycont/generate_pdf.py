#!/usr/bin/env python3
"""
PDF Generator for Security Audit Report
Matches the reference report style exactly
"""

import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Preformatted, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Read the markdown report
with open('/home/divesh/Desktop/RWA/fin2/mangonui/mx-chain-core-go/mycont/SECURITY_AUDIT_REPORT_FINAL_v2_mx-chain-core-go.md', 'r') as f:
    content = f.read()

# Output PDF path
output_pdf = '/home/divesh/Desktop/RWA/fin2/mangonui/mx-chain-core-go/mycont/SECURITY_AUDIT_REPORT_FINAL_v2_mx-chain-core-go.pdf'

# Create PDF document
doc = SimpleDocTemplate(
    output_pdf,
    pagesize=A4,
    rightMargin=20*mm,
    leftMargin=20*mm,
    topMargin=20*mm,
    bottomMargin=20*mm
)

# Story will hold all flowables
story = []

print("Step 1: Imports and setup complete")

# ─── STYLES ───────────────────────────────────────────────────────────────────

PAGE_WIDTH = A4[0] - 40*mm  # usable width

# Colour palette matching reference PDF
C_BLACK      = colors.HexColor('#1a1a1a')
C_DARK_GREY  = colors.HexColor('#333333')
C_MID_GREY   = colors.HexColor('#555555')
C_LIGHT_GREY = colors.HexColor('#f5f5f5')
C_BORDER     = colors.HexColor('#cccccc')
C_RED        = colors.HexColor('#c0392b')
C_ORANGE     = colors.HexColor('#e67e22')
C_GREEN      = colors.HexColor('#27ae60')
C_BLUE       = colors.HexColor('#2980b9')
C_PURPLE     = colors.HexColor('#8e44ad')
C_HEADER_BG  = colors.HexColor('#2c3e50')
C_CODE_BG    = colors.HexColor('#f4f4f4')
C_CODE_BORDER= colors.HexColor('#dddddd')
C_SECTION_BG = colors.HexColor('#2c3e50')
C_MANDATORY  = colors.HexColor('#c0392b')
C_RECOMMENDED= colors.HexColor('#e67e22')
C_SECURE     = colors.HexColor('#27ae60')

styles = getSampleStyleSheet()

# Title style
style_title = ParagraphStyle(
    'ReportTitle',
    fontName='Helvetica-Bold',
    fontSize=20,
    textColor=C_BLACK,
    spaceAfter=4,
    spaceBefore=0,
    leading=24,
)

# Subtitle / meta line
style_meta = ParagraphStyle(
    'Meta',
    fontName='Helvetica',
    fontSize=9,
    textColor=C_MID_GREY,
    spaceAfter=2,
    spaceBefore=0,
    leading=13,
)

# Section heading (## level)
style_section = ParagraphStyle(
    'SectionHeading',
    fontName='Helvetica-Bold',
    fontSize=13,
    textColor=colors.white,
    spaceAfter=8,
    spaceBefore=14,
    leading=16,
    backColor=C_SECTION_BG,
    leftIndent=-2*mm,
    rightIndent=-2*mm,
    borderPad=4,
)

# Finding heading (### level)
style_finding = ParagraphStyle(
    'FindingHeading',
    fontName='Helvetica-Bold',
    fontSize=11,
    textColor=C_BLACK,
    spaceAfter=6,
    spaceBefore=12,
    leading=14,
    borderPad=3,
    leftIndent=0,
)

# Sub-heading (bold label like Classification:)
style_label = ParagraphStyle(
    'Label',
    fontName='Helvetica-Bold',
    fontSize=9,
    textColor=C_BLACK,
    spaceAfter=2,
    spaceBefore=6,
    leading=12,
)

# Normal body text
style_body = ParagraphStyle(
    'Body',
    fontName='Helvetica',
    fontSize=9,
    textColor=C_DARK_GREY,
    spaceAfter=4,
    spaceBefore=2,
    leading=13,
    alignment=TA_JUSTIFY,
)

# Bullet item
style_bullet = ParagraphStyle(
    'Bullet',
    fontName='Helvetica',
    fontSize=9,
    textColor=C_DARK_GREY,
    spaceAfter=3,
    spaceBefore=1,
    leading=13,
    leftIndent=12,
    bulletIndent=4,
)

# Sub-bullet (indented)
style_sub_bullet = ParagraphStyle(
    'SubBullet',
    fontName='Helvetica',
    fontSize=9,
    textColor=C_DARK_GREY,
    spaceAfter=2,
    spaceBefore=1,
    leading=13,
    leftIndent=24,
    bulletIndent=16,
)

# Code block
style_code = ParagraphStyle(
    'Code',
    fontName='Courier',
    fontSize=8,
    textColor=C_DARK_GREY,
    spaceAfter=6,
    spaceBefore=4,
    leading=11,
    leftIndent=4,
    backColor=C_CODE_BG,
    borderColor=C_CODE_BORDER,
    borderWidth=0.5,
    borderPad=6,
)

# Inline code (within paragraph)
style_inline_code = ParagraphStyle(
    'InlineCode',
    fontName='Courier',
    fontSize=8,
    textColor=C_DARK_GREY,
    leading=11,
)

# Classification block
style_classif = ParagraphStyle(
    'Classification',
    fontName='Helvetica',
    fontSize=9,
    textColor=C_DARK_GREY,
    spaceAfter=2,
    spaceBefore=1,
    leading=13,
    leftIndent=8,
)

# Severity note
style_severity = ParagraphStyle(
    'SeverityNote',
    fontName='Helvetica',
    fontSize=9,
    textColor=C_DARK_GREY,
    spaceAfter=4,
    spaceBefore=2,
    leading=13,
    leftIndent=0,
    backColor=colors.HexColor('#fef9e7'),
    borderColor=colors.HexColor('#f39c12'),
    borderWidth=0.5,
    borderPad=5,
    alignment=TA_JUSTIFY,
)

# If Left Unfixed block
style_unfixed = ParagraphStyle(
    'IfUnfixed',
    fontName='Helvetica',
    fontSize=9,
    textColor=C_DARK_GREY,
    spaceAfter=3,
    spaceBefore=1,
    leading=13,
    leftIndent=8,
    backColor=colors.HexColor('#fdf2f2'),
    borderColor=C_RED,
    borderWidth=0.5,
    borderPad=5,
)

# Fix Priority Summary
style_priority = ParagraphStyle(
    'Priority',
    fontName='Helvetica',
    fontSize=9,
    textColor=C_DARK_GREY,
    spaceAfter=3,
    spaceBefore=2,
    leading=13,
    leftIndent=8,
)

print("Step 2: Styles defined")

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def hr():
    """Horizontal rule"""
    from reportlab.platypus import HRFlowable
    return HRFlowable(width='100%', thickness=0.5, color=C_BORDER, spaceAfter=6, spaceBefore=6)

def spacer(h=4):
    return Spacer(1, h)

def escape(text):
    """Escape HTML special chars for Paragraph"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def bold(text):
    return f'<b>{escape(text)}</b>'

def code_inline(text):
    return f'<font name="Courier" size="8">{escape(text)}</font>'

def severity_color(sev):
    sev = sev.upper()
    if 'CRITICAL' in sev or 'HIGH' in sev:
        return C_RED
    if 'MEDIUM' in sev:
        return C_ORANGE
    if 'LOW' in sev:
        return C_BLUE
    if 'INFO' in sev:
        return C_MID_GREY
    return C_DARK_GREY

def make_summary_table(rows, col_widths, header_row):
    """Build a styled table matching reference PDF"""
    data = [header_row] + rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = TableStyle([
        # Header
        ('BACKGROUND',   (0,0), (-1,0), C_HEADER_BG),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,0), 8),
        ('BOTTOMPADDING',(0,0), (-1,0), 6),
        ('TOPPADDING',   (0,0), (-1,0), 6),
        # Body rows
        ('FONTNAME',     (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',     (0,1), (-1,-1), 8),
        ('TOPPADDING',   (0,1), (-1,-1), 5),
        ('BOTTOMPADDING',(0,1), (-1,-1), 5),
        ('LEFTPADDING',  (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        # Alternating rows
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, C_LIGHT_GREY]),
        # Grid
        ('GRID',         (0,0), (-1,-1), 0.4, C_BORDER),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
        ('WORDWRAP',     (0,0), (-1,-1), True),
    ])
    t.setStyle(style)
    return t

def make_code_block(code_text):
    """Render a code block with background"""
    lines = code_text.strip().split('\n')
    escaped = '\n'.join(escape(l) for l in lines)
    return Preformatted(
        code_text.strip(),
        ParagraphStyle(
            'CodeBlock',
            fontName='Courier',
            fontSize=7.5,
            leading=11,
            leftIndent=6,
            rightIndent=6,
            spaceAfter=6,
            spaceBefore=4,
            backColor=C_CODE_BG,
            borderColor=C_CODE_BORDER,
            borderWidth=0.5,
            borderPad=6,
            textColor=C_DARK_GREY,
        )
    )

def section_heading(text):
    """Dark background section heading"""
    return Paragraph(f'&nbsp;&nbsp;{escape(text)}', style_section)

def finding_heading(text):
    """Finding level heading with left border effect"""
    return Paragraph(escape(text), style_finding)

def label_para(label, value='', style=None):
    """Bold label followed by normal value"""
    s = style or style_body
    if value:
        return Paragraph(f'<b>{escape(label)}</b> {escape(value)}', s)
    return Paragraph(f'<b>{escape(label)}</b>', s)

def body_para(text, style=None):
    s = style or style_body
    # Convert inline backtick code to courier font
    def replace_code(m):
        return code_inline(m.group(1))
    text = re.sub(r'`([^`]+)`', replace_code, text)
    # Convert **bold** to <b>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    return Paragraph(text, s)

def bullet_para(text, level=0):
    s = style_sub_bullet if level > 0 else style_bullet
    def replace_code(m):
        return code_inline(m.group(1))
    text = re.sub(r'`([^`]+)`', replace_code, text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    bullet_char = '•' if level == 0 else '◦'
    return Paragraph(f'{bullet_char}&nbsp;&nbsp;{text}', s)

print("Step 3: Helper functions defined")

# ─── SECTION: HEADER ──────────────────────────────────────────────────────────

story.append(Paragraph('Security Findings &amp; Fix Report — mx-chain-core-go', style_title))
story.append(spacer(2))
story.append(Paragraph('<b>Scan Type:</b> Full repository scan — all files analyzed', style_meta))
story.append(Paragraph('<b>Files Covered:</b> core/common.go, core/common_test.go, core/file.go, core/file_test.go, core/constants.go, data/drwa/constants.go, data/drwa/constants_test.go', style_meta))
story.append(spacer(6))

# Overall status box
status_text = (
    '<b>Overall Status:</b> 5 findings total — 2 real security findings (1 Medium, 1 Medium), '
    '3 code/quality findings (1 Low, 1 Low, 1 Low), 1 false positive, 1 DRWA flow gap (Medium). '
    'Previous audit findings F1 (rand.Read error), F2 (strings.Index), F4 (untyped prefixes), '
    'F5 (test uniqueness) confirmed fixed in code. '
    '<b>Finding A</b> — IsValid() accepts DenialUnknown as storable, re-introducing the compliance '
    'reporting failure the previous fix was designed to close. '
    '<b>Finding B</b> — LoadTomlFileToMap defers f.Close() after two early-return points, leaking '
    'file descriptors on f.Stat() and f.Read() error paths. '
    '<b>Finding C</b> — SaveSkToPemFile writes PEM with no identifier validation. '
    '<b>Finding D</b> — CreateFile creates directories with os.ModePerm (0777). '
    '<b>Finding E</b> — GetPBFTThreshold and GetPBFTFallbackThreshold return threshold 1 for '
    'consensusSize 0 or negative, collapsing Byzantine fault tolerance silently.'
)
status_style = ParagraphStyle(
    'StatusBox',
    fontName='Helvetica',
    fontSize=8.5,
    textColor=C_DARK_GREY,
    spaceAfter=8,
    spaceBefore=4,
    leading=13,
    backColor=colors.HexColor('#eaf4fb'),
    borderColor=C_BLUE,
    borderWidth=1,
    borderPad=8,
    alignment=TA_JUSTIFY,
)
story.append(Paragraph(status_text, status_style))
story.append(hr())

# ─── SECTION 1: SUMMARY TABLE ─────────────────────────────────────────────────

story.append(section_heading('SECTION 1 — SUMMARY TABLE'))
story.append(spacer(4))

# Column widths
cw = [8*mm, 42*mm, 16*mm, 16*mm, 24*mm, 22*mm, 38*mm, 24*mm]

header = [
    Paragraph('<b>#</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>File</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Line</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Severity</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Type</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Fix Required</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Mandatory?</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Status</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
]

cell = lambda t, bold=False, color=C_DARK_GREY: Paragraph(
    f'<b>{escape(t)}</b>' if bold else escape(t),
    ParagraphStyle('td', fontName='Helvetica-Bold' if bold else 'Helvetica',
                   fontSize=7.5, textColor=color, leading=10)
)

rows = [
    [cell('A', bold=True, color=C_RED),
     cell('data/drwa/constants.go'),
     cell('67'),
     cell('Medium', color=C_ORANGE),
     cell('DRWA FINDING'),
     cell('Yes'),
     cell('YES — regulatory violations accumulate', color=C_RED),
     cell('REAL FINDING', bold=True)],

    [cell('B', bold=True, color=C_RED),
     cell('core/file.go'),
     cell('69–100'),
     cell('Medium', color=C_ORANGE),
     cell('REAL FINDING'),
     cell('Yes'),
     cell('YES — node crashes under disk pressure', color=C_RED),
     cell('REAL FINDING', bold=True)],

    [cell('C'),
     cell('core/file.go'),
     cell('260–272'),
     cell('Low', color=C_BLUE),
     cell('REAL FINDING'),
     cell('Recommended'),
     cell('Latent trap for downstream developers'),
     cell('REAL FINDING', bold=True)],

    [cell('D'),
     cell('core/file.go'),
     cell('124'),
     cell('Low', color=C_BLUE),
     cell('CODE QUALITY'),
     cell('Conditional'),
     cell('Critical in containers with permissive umask'),
     cell('REAL FINDING', bold=True)],

    [cell('E'),
     cell('core/common.go'),
     cell('46–52'),
     cell('Low', color=C_BLUE),
     cell('CODE QUALITY'),
     cell('Recommended'),
     cell('Defence-in-depth gap'),
     cell('REAL FINDING', bold=True)],

    [cell('6'),
     cell('core/common.go'),
     cell('28–33'),
     cell('—'),
     cell('FALSE POSITIVE'),
     cell('None'),
     cell('Not a vulnerability'),
     cell('DISMISSED', color=C_GREEN)],

    [cell('7'),
     cell('data/drwa/constants_test.go'),
     cell('—'),
     cell('Medium', color=C_ORANGE),
     cell('DRWA FLOW GAP'),
     cell('Recommended'),
     cell('Regulatory gap grows with new denial codes'),
     cell('OPEN', color=C_ORANGE)],
]

story.append(make_summary_table(rows, cw, header))
story.append(spacer(8))
story.append(hr())

print("Step 4: Header and Section 1 built")

# ─── SECTION 2: REAL FINDINGS ─────────────────────────────────────────────────

story.append(section_heading('SECTION 2 — REAL FINDINGS'))
story.append(spacer(4))

# ── Finding A ─────────────────────────────────────────────────────────────────

story.append(KeepTogether([
    finding_heading('Finding A — DRWA FINDING — IsValid() Accepts DenialUnknown as a Storable Denial Code in data/drwa/constants.go line 67'),
]))

# Classification box
classif_data = [
    ['CWE:', 'CWE-20 (Improper Input Validation)'],
    ['CVSS v3.1 Score:', '5.3 (Medium) — AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N'],
    ['Severity:', 'Medium'],
    ['Fix Required:', 'Yes — MANDATORY'],
    ['Runtime Impact:', 'Any downstream compliance gate that calls code.IsValid() before storing a denial record will accept DenialUnknown ("DRWA_UNKNOWN") as a valid storable denial reason. A denial record carrying "DRWA_UNKNOWN" is not attributable to any specific compliance rule.'],
    ['Monitoring Impact:', 'No compile-time error, no runtime panic — DenialUnknown is silently stored in the compliance index as if it were a valid denial reason.'],
]
ct = Table(classif_data, colWidths=[30*mm, PAGE_WIDTH-30*mm])
ct.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTNAME',     (1,0), (1,-1), 'Helvetica'),
    ('FONTSIZE',     (0,0), (-1,-1), 8),
    ('TOPPADDING',   (0,0), (-1,-1), 3),
    ('BOTTOMPADDING',(0,0), (-1,-1), 3),
    ('LEFTPADDING',  (0,0), (-1,-1), 5),
    ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ('BACKGROUND',   (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
    ('GRID',         (0,0), (-1,-1), 0.3, C_BORDER),
    ('TEXTCOLOR',    (0,0), (0,-1), C_DARK_GREY),
    ('TEXTCOLOR',    (1,0), (1,-1), C_DARK_GREY),
    ('TEXTCOLOR',    (1,3), (1,3), C_RED),
]))
story.append(ct)
story.append(spacer(6))

story.append(label_para('Severity Note:', 'Medium. Data origin is INTERNAL — the return value of NormalizeDenialCode for any unrecognized input. No external attacker input is required. The previous audit prescribed IsValid() to return false for the unknown sentinel. The implementation inverted this: IsValid() returns true for DenialUnknown (line 67). IsKnown() correctly returns false for DenialUnknown, but IsValid() is the natural method name a downstream developer reaches for as a storage pre-check. The inversion is a design contract violation that silently re-introduces the regulatory reporting failure the previous fix was designed to close.', style_severity))
story.append(spacer(4))

story.append(label_para('What the Vulnerable Function Does:'))
story.append(body_para('`IsValid()` in data/drwa/constants.go lines 66–68 returns `true` for `DenialUnknown` ("DRWA_UNKNOWN") via the condition `code == DenialUnknown || code.IsKnown()`. The doc comment says "including the explicit unknown sentinel" — this is the design choice that creates the vulnerability.'))
story.append(body_para('<b>What it does NOT do:</b> does not distinguish between "this code is a known concrete denial reason" and "this code is the explicit fallback for unrecognized inputs". Does not prevent `DenialUnknown` from being stored in the compliance index when `IsValid()` is used as the storage guard.'))
story.append(body_para('<b>Call chain:</b> compliance gate evaluates transfer → `NormalizeDenialCode` returns `DenialUnknown` for unrecognized input → `code.IsValid()` returns `true` → denial record stored with `denial_code: "DRWA_UNKNOWN"` → indexed to compliance store → regulatory report contains denial with no attributable rule.'))
story.append(spacer(4))

story.append(label_para('Where Does the Vulnerable Data Come From:'))
story.append(body_para('`NormalizeDenialCode` (line 73) returns `DenialUnknown` for any unrecognized non-empty input → downstream compliance gate calls `code.IsValid()` → returns `true` → `DenialUnknown` stored in compliance index → regulatory audit trail contains denial with no rule attribution.'))
story.append(body_para('<b>Data origin:</b> INTERNAL (`NormalizeDenialCode` return value). No external input required.'))
story.append(spacer(4))

story.append(label_para('Who Uses This Data and Why It Must Be Trusted:'))
for item in [
    '<b>DevOps / Node Operator:</b> Monitors denial code distribution in compliance metrics. Breaks if `DenialUnknown` denial records accumulate — metrics show denials with no rule attribution. <b>Silent failure consequence:</b> operators assume the denial reason was intentionally "unknown"; the bug is never investigated.',
    '<b>Security / Compliance Engineer:</b> Relies on `IsValid()` as the storage guard to reject unattributable denial codes. Breaks because `IsValid()` returns `true` for `DenialUnknown` — the guard passes silently. <b>Silent failure consequence:</b> compliance audit cannot determine which rule triggered the denial.',
    '<b>Compliance / Regulatory Officer:</b> Must demonstrate that every transfer denial corresponds to a specific regulatory rule (KYC, AML, sanctions, etc.). Breaks if `DenialUnknown` appears in the compliance index. <b>Silent failure consequence:</b> regulatory filing contains unexplained denials — potential MiCA Article 45 violation.',
    '<b>On-Call Engineer:</b> Investigates compliance gate anomalies. Breaks because `DenialUnknown` gives no indication of which code path produced it. <b>Silent failure consequence:</b> on-call cannot determine root cause without full code path analysis.',
]:
    story.append(bullet_para(item))
story.append(spacer(4))

story.append(label_para('What an Attacker Can Do:'))
attacker_scenarios_a = [
    ('<b>Compliance Index Pollution via Unrecognized Input:</b> Attacker sends a transfer with a denial code field set to an unrecognized string → `NormalizeDenialCode` returns `DenialUnknown` → `IsValid()` returns `true` → denial record stored with `denial_code: "DRWA_UNKNOWN"`.', 'No error — denial record stored silently', 'Compliance index accumulates DenialUnknown records; regulatory report contains denials with no rule attribution.'),
    ('<b>Regulatory Report Corruption:</b> Regulatory reporting tool filters denial records by `DenialCode` — records with `DenialUnknown` are excluded from category counts. Total denial count does not match sum of category counts.', 'No error', 'Regulatory report is internally inconsistent — potential regulatory filing failure.'),
    ('<b>Compliance Gate Bypass via Default Branch:</b> Downstream switch on `DenialCode` has no `case DenialUnknown:` branch — unknown code falls to default which may not block the transfer.', 'No error — default branch executes, transfer may proceed', 'Transfer that should be denied proceeds because the denial code was never resolved to a concrete rule.'),
    ('<b>Audit Trail Collapse:</b> High-volume transfers through the unrecognized-input path — all denial records carry `DenialUnknown`, making the compliance index useless for attribution.', 'No error — all records indexed with DenialUnknown', 'Compliance dashboard shows thousands of denials with no rule attribution; dashboard is unusable.'),
]
for i, (scenario, log, consequence) in enumerate(attacker_scenarios_a, 1):
    story.append(bullet_para(f'{i}. {scenario}'))
    story.append(bullet_para(f'<b>Exact log output:</b> {log}', level=1))
    story.append(bullet_para(f'<b>Consequence:</b> {consequence}', level=1))
story.append(spacer(4))

story.append(label_para('Why This Is Specific to This Feature:'))
story.append(body_para('`DenialCode` is the only typed string in data/drwa/constants.go that carries regulatory significance — each value maps to a specific compliance rule that must be attributable in regulatory filings. `IsValid()` is the only validation method on `DenialCode`. Its semantics directly determine what gets stored in the compliance index. The previous audit\'s prescribed fix explicitly required `IsValid()` to return `false` for the unknown sentinel — the implementation inverted this contract.'))
story.append(spacer(4))

story.append(label_para('The Fix:'))
story.append(body_para('<b>BEFORE</b> (data/drwa/constants.go lines 64–68 — exact code from file):'))
story.append(make_code_block('// IsValid reports whether code is a valid canonical value, including the\n// explicit unknown sentinel. The empty string is never valid.\nfunc (code DenialCode) IsValid() bool {\n    return code == DenialUnknown || code.IsKnown()\n}'))
story.append(body_para('<b>AFTER:</b>'))
story.append(make_code_block('// IsValid reports whether code is one of the 15 concrete denial codes\n// emitted by the DRWA gate. Returns false for DenialUnknown and the\n// empty string. Use IsValid() as the storage guard before writing a\n// denial record to the compliance index.\nfunc (code DenialCode) IsValid() bool {\n    return code.IsKnown()\n}'))
story.append(body_para('<b>What each line does:</b> Removing `code == DenialUnknown` from the return condition means `IsValid()` returns `false` for `DenialUnknown`, consistent with the previous audit\'s prescription. `IsKnown()` already iterates `AllDenialCodes()` and returns `true` only for the 15 concrete codes — no new logic needed.'))
story.append(spacer(4))

story.append(label_para('Why This Fix Is Safe:'))
story.append(body_para('No imports needed. No existing call sites in this repo are broken — `IsValid()` has no callers in mx-chain-core-go itself. Downstream code that uses `IsValid()` as a storage guard gains the correct behaviour. `DenialUnknown` remains a valid named constant.'))
story.append(spacer(4))

story.append(label_para('Integration Impact — Will It Break Existing Flow:'))
for item in [
    '<b>One existing test must be updated before applying this fix.</b> `TestDenialCodes_ValidityAndNormalization` at constants_test.go line 28 currently asserts `if !DenialUnknown.IsValid()` — this assertion flips after the fix. Update it to `if DenialUnknown.IsValid()` before deploying.',
    '`NormalizeDenialCode` internal behaviour is unchanged. The output is identical — `DenialUnknown` is still returned for unrecognized inputs — via a different internal path. No caller observes any difference.',
    '<b>No runtime flow breaks.</b> `IsKnown()` is not changed. All 15 concrete denial codes continue to pass both `IsValid()` and `IsKnown()` unchanged.',
    '<b>Smooth integration:</b> After updating the one test assertion, `go test ./...` passes clean. No API changes, no signature changes, no import changes.',
]:
    story.append(bullet_para(item))
story.append(spacer(4))

story.append(label_para('Test Update Required:'))
story.append(body_para('Update `TestDenialCodes_ValidityAndNormalization` in constants_test.go line 28 — change assertion so that `DenialUnknown.IsValid()` must return `false`. Add `TestDenialUnknown_IsNotStorable` asserting `DenialUnknown.IsValid() == false`.'))
story.append(spacer(4))

story.append(label_para('Why This Fix Is Necessary:'))
story.append(body_para('A compliance type whose "is valid for storage" method returns `true` for the explicit "I don\'t know what this is" sentinel is a regulatory reporting risk. Every denial record in the compliance audit trail must carry a specific, attributable denial reason. Silence is worse than explicit failure because a denial record with `denial_code: "DRWA_UNKNOWN"` stored in the compliance index gives no indication to the compliance engineer, the regulatory officer, or the on-call engineer that the denial reason was never resolved to a concrete rule.'))
story.append(spacer(4))

story.append(label_para('If Left Unfixed — Consequences:'))
unfixed_a = [
    'Every transfer that triggers an unrecognized denial code path permanently stores a `DRWA_UNKNOWN` record in the compliance index. These records accumulate with every transaction and cannot be retroactively corrected.',
    'Under MiCA Article 45 this is a direct regulatory filing violation — you cannot demonstrate which compliance rule triggered the denial.',
    'A downstream switch with no `case DenialUnknown:` branch silently allows transfers that should be denied — a regulated transfer that should be blocked goes through with no error, no log, no alert.',
    'Compliance dashboards become unreliable — denial counts include `DRWA_UNKNOWN` records that map to no rule, making category breakdowns internally inconsistent.',
    '<b>This is the highest-priority fix in the entire report. It must be applied before the system processes any real regulated transfers.</b>',
]
for item in unfixed_a:
    story.append(bullet_para(item, level=0))
story.append(spacer(6))
story.append(hr())

print("Step 5: Finding A built")

# ── Finding B ─────────────────────────────────────────────────────────────────

story.append(finding_heading('Finding B — REAL FINDING — defer f.Close() Placed After Early Returns Leaks File Descriptor on Error Paths in core/file.go lines 69–100'))

classif_b = [
    ['CWE:', 'CWE-775 (Missing Release of File Descriptor or Handle after Effective Lifetime)'],
    ['CVSS v3.1 Score:', '5.3 (Medium) — AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H'],
    ['Severity:', 'Medium'],
    ['Fix Required:', 'Yes — MANDATORY'],
    ['Runtime Impact:', 'LoadTomlFileToMap opens a file at line 71, calls f.Stat() at line 76 and f.Read() at line 84. If either returns an error the function returns early at lines 78 or 86. The defer f.Close() is registered at line 89 — after both early return points. On the f.Stat() and f.Read() error paths the defer is never registered, so f.Close() is never called. The file descriptor is leaked for the lifetime of the process.'],
    ['Monitoring Impact:', 'No error logged for the leaked descriptor. The OS fd table silently fills. On Linux the default per-process limit is 1024 (soft) / 4096 (hard). A node that repeatedly calls LoadTomlFileToMap on error paths will exhaust its fd table, causing all subsequent file opens to fail with "too many open files".'],
]
ct_b = Table(classif_b, colWidths=[30*mm, PAGE_WIDTH-30*mm])
ct_b.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTNAME',     (1,0), (1,-1), 'Helvetica'),
    ('FONTSIZE',     (0,0), (-1,-1), 8),
    ('TOPPADDING',   (0,0), (-1,-1), 3),
    ('BOTTOMPADDING',(0,0), (-1,-1), 3),
    ('LEFTPADDING',  (0,0), (-1,-1), 5),
    ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ('BACKGROUND',   (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
    ('GRID',         (0,0), (-1,-1), 0.3, C_BORDER),
    ('TEXTCOLOR',    (0,0), (-1,-1), C_DARK_GREY),
    ('TEXTCOLOR',    (1,3), (1,3), C_RED),
]))
story.append(ct_b)
story.append(spacer(6))

story.append(label_para('Severity Note:', 'Medium. Data origin is LOCAL FILE (operator-controlled filesystem). The error paths that trigger the leak require either a filesystem race or a kernel-level read error (disk I/O failure). Neither requires an external attacker. All other file-handling functions in the same file (LoadTomlFile line 48, SaveTomlFile line 62, LoadJsonFile line 110) correctly register defer f.Close() immediately after the file is opened — the misplacement is unique to LoadTomlFileToMap.', style_severity))
story.append(spacer(4))

story.append(label_para('What the Vulnerable Function Does:'))
story.append(body_para('`LoadTomlFileToMap` in core/file.go opens a file, calls `f.Stat()` to get the file size, allocates a buffer, calls `f.Read()` to fill it, then defers `f.Close()` and proceeds to parse the buffer as TOML.'))
story.append(body_para('<b>What it does NOT do:</b> does not register `defer f.Close()` immediately after `OpenFile` succeeds. Does not call `f.Close()` explicitly on the error paths at lines 78 and 86.'))
story.append(body_para('<b>Call chain:</b> node startup → `LoadTomlFileToMap("config.toml")` → `OpenFile` succeeds → `f.Stat()` fails (disk error) → `return nil, err` at line 78 → defer never registered → `f.Close()` never called → file descriptor leaked → repeated calls exhaust fd table → all subsequent file opens fail with `EMFILE`.'))
story.append(spacer(4))

story.append(label_para('Where Does the Vulnerable Data Come From:'))
story.append(body_para('Operator-placed config file → `OpenFile` opens it → `f.Stat()` or `f.Read()` fails due to filesystem error → early return without closing. <b>Data origin:</b> LOCAL FILE.'))
story.append(spacer(4))

story.append(label_para('Who Uses This Data and Why It Must Be Trusted:'))
for item in [
    '<b>DevOps / Node Operator:</b> Relies on `LoadTomlFileToMap` releasing file descriptors on all paths. Breaks if fd table is exhausted — node cannot open PEM key files or config files at startup. <b>Silent failure consequence:</b> node fails to start with "too many open files" with no indication the root cause is a leaked descriptor.',
    '<b>Security / Compliance Engineer:</b> Relies on node starting cleanly to begin processing regulated transfers. Breaks if node cannot open key files due to fd exhaustion. <b>Silent failure consequence:</b> all regulated transfers blocked because the node never reaches the compliance gate.',
    '<b>Compliance / Regulatory Officer:</b> Relies on the node being operational to process and record regulated transfers. Breaks if node is DoS\'d via fd exhaustion. <b>Silent failure consequence:</b> regulated transfers are not processed during the outage window.',
    '<b>On-Call Engineer:</b> Investigates node startup failures. Breaks because "too many open files" gives no indication of which function leaked the descriptor. <b>Silent failure consequence:</b> on-call cannot determine root cause without strace or lsof analysis.',
]:
    story.append(bullet_para(item))
story.append(spacer(4))

story.append(label_para('What an Attacker Can Do:'))
attacker_b = [
    ('<b>Filesystem Race to Trigger Leak:</b> Attacker repeatedly creates and removes a config file between `OpenFile` and `Stat` → `f.Stat()` fails on every call → each call leaks one fd → fd table exhausted.', 'No error for the leaked fd — only "too many open files" when full', 'Node DoS — all file operations fail.'),
    ('<b>Disk I/O Error Amplification:</b> Under disk pressure, `f.Read()` returns an error → fd leaked → repeated config reloads each leak one fd → fd table exhausted faster than the disk recovers.', 'No error for the leaked fd', 'Node cannot recover from disk pressure — permanent DoS until restart.'),
    ('<b>Container fd Limit Exhaustion:</b> In a containerised deployment with a low fd limit, a single burst of config reload errors exhausts the fd table — node cannot open the PEM key file needed to sign blocks.', 'No error at leak time', 'Node stops signing blocks — silently excluded from consensus.'),
    ('<b>Repeated Error Path Triggering:</b> Attacker causes repeated `f.Stat()` failures by toggling file permissions — each call leaks one fd — fd table exhausted in O(fd_limit) calls.', 'No error', 'Node DoS with no log trail pointing to the root cause.'),
]
for i, (scenario, log, consequence) in enumerate(attacker_b, 1):
    story.append(bullet_para(f'{i}. {scenario}'))
    story.append(bullet_para(f'<b>Exact log output:</b> {log}', level=1))
    story.append(bullet_para(f'<b>Consequence:</b> {consequence}', level=1))
story.append(spacer(4))

story.append(label_para('Why This Is Specific to This Feature:'))
story.append(body_para('`LoadTomlFileToMap` is the only function in core/file.go that places `defer f.Close()` after error-returning statements that follow the file open. All other functions in the same file correctly register `defer f.Close()` immediately after the file is opened. The misplacement is unique to `LoadTomlFileToMap` and is not present in any other file-handling function in the package.'))
story.append(spacer(4))

story.append(label_para('The Fix:'))
story.append(body_para('<b>BEFORE</b> (core/file.go lines 69–100 — exact code from file):'))
story.append(make_code_block('func LoadTomlFileToMap(relativePath string) (map[string]interface{}, error) {\n    f, err := OpenFile(relativePath)\n    if err != nil {\n        return nil, err\n    }\n\n    fileinfo, err := f.Stat()\n    if err != nil {\n        return nil, err          // fd leaked here — defer not yet registered\n    }\n\n    filesize := fileinfo.Size()\n    buffer := make([]byte, filesize)\n\n    _, err = f.Read(buffer)\n    if err != nil {\n        return nil, err          // fd leaked here — defer not yet registered\n    }\n\n    defer func() {               // too late — only reached on success path\n        _ = f.Close()\n    }()\n    ...\n}'))
story.append(body_para('<b>AFTER:</b>'))
story.append(make_code_block('func LoadTomlFileToMap(relativePath string) (map[string]interface{}, error) {\n    f, err := OpenFile(relativePath)\n    if err != nil {\n        return nil, err\n    }\n\n    defer func() {               // registered immediately after open — fires on all paths\n        _ = f.Close()\n    }()\n\n    fileinfo, err := f.Stat()\n    if err != nil {\n        return nil, err          // defer now fires — fd closed\n    }\n\n    filesize := fileinfo.Size()\n    buffer := make([]byte, filesize)\n\n    _, err = f.Read(buffer)\n    if err != nil {\n        return nil, err          // defer now fires — fd closed\n    }\n    ...\n}'))
story.append(body_para('<b>What each line does:</b> Moving `defer f.Close()` to immediately after the nil-error check on `OpenFile` ensures it is registered on every code path that successfully opens the file. No other logic changes — the fix is a single block move of 3 lines.'))
story.append(spacer(4))

story.append(label_para('Why This Fix Is Safe:'))
story.append(body_para('Semantically identical for all success paths. Additive only for error paths — `f.Close()` is now called on paths where it was previously skipped. No imports needed. No API changes.'))
story.append(spacer(4))

story.append(label_para('Integration Impact — Will It Break Existing Flow:'))
for item in [
    '<b>No existing tests break.</b> The fix is a 3-line block move. The success path — the only path currently exercised by all existing tests — is completely unchanged.',
    '<b>No runtime flow breaks.</b> All callers of `LoadTomlFileToMap` receive identical return values on both success and error paths.',
    '<b>Smooth integration:</b> Drop-in safe. No API changes, no signature changes, no import changes. `go test ./...` passes clean with no modifications.',
]:
    story.append(bullet_para(item))
story.append(spacer(4))

story.append(label_para('Test Update Required:'))
story.append(body_para('Add a test that calls `LoadTomlFileToMap` with a file that is deleted between open and read and asserts no file descriptor leak. Verify with `/proc/self/fd` that the fd count does not increase on repeated error-path calls.'))
story.append(spacer(4))

story.append(label_para('Why This Fix Is Necessary:'))
story.append(body_para('A file descriptor leak in a config-loading function that is called at node startup and on config reload is a latent DoS vector. The leak is silent — no error is logged, no metric is incremented. The only observable symptom is "too many open files" when the fd table is exhausted, at which point the node cannot recover without a restart.'))
story.append(spacer(4))

story.append(label_para('If Left Unfixed — Consequences:'))
for item in [
    'Under disk pressure: the node silently accumulates leaked file descriptors, then crashes with "too many open files" at an unpredictable point during the incident — exactly when you need it most stable.',
    'In containerised deployments with low fd limits: a single burst of config reload errors can exhaust the fd table in minutes, stopping the node from signing blocks and silently excluding it from consensus.',
    'The failure symptom gives no indication of the root cause — on-call spends hours debugging the wrong thing while the node is down.',
    '<b>This is the second highest-priority fix. It must be applied before any production deployment under disk pressure or in containers.</b>',
]:
    story.append(bullet_para(item))
story.append(spacer(6))
story.append(hr())

print("Step 6: Finding B built")

# ── Finding C ─────────────────────────────────────────────────────────────────

story.append(finding_heading('Finding C — REAL FINDING — SaveSkToPemFile Writes PEM Block with No Identifier Validation in core/file.go lines 260–272'))

classif_c = [
    ['CWE:', 'CWE-20 (Improper Input Validation)'],
    ['CVSS v3.1 Score:', '4.0 (Low) — AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:L'],
    ['Severity:', 'Low'],
    ['Fix Required:', 'Recommended — fix before codebase grows'],
    ['Runtime Impact:', 'SaveSkToPemFile writes a PEM block with type "PRIVATE KEY for " + identifier with no validation. LoadSkPkFromPemFile and LoadAllKeysFromPemFile both call isValidPemPublicKeySuffix on the extracted suffix. If SaveSkToPemFile writes a PEM file with an identifier that fails isValidPemPublicKeySuffix, the file cannot be loaded back. The write succeeds silently; the load fails with ErrPemFileIsInvalid.'],
    ['Monitoring Impact:', 'No error at write time. The failure is discovered only when the node attempts to load the key at startup, producing ErrPemFileIsInvalid with no indication that the root cause is the identifier that was written.'],
]
ct_c = Table(classif_c, colWidths=[30*mm, PAGE_WIDTH-30*mm])
ct_c.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTNAME',     (1,0), (1,-1), 'Helvetica'),
    ('FONTSIZE',     (0,0), (-1,-1), 8),
    ('TOPPADDING',   (0,0), (-1,-1), 3),
    ('BOTTOMPADDING',(0,0), (-1,-1), 3),
    ('LEFTPADDING',  (0,0), (-1,-1), 5),
    ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ('BACKGROUND',   (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
    ('GRID',         (0,0), (-1,-1), 0.3, C_BORDER),
    ('TEXTCOLOR',    (0,0), (-1,-1), C_DARK_GREY),
]))
story.append(ct_c)
story.append(spacer(6))

story.append(label_para('Severity Note:', 'Low. Data origin is the caller-supplied identifier string. In production the identifier is the node\'s public key string, which is validated upstream. The risk is a programming error in a downstream repo that passes an empty, whitespace-padded, or control-character-containing identifier to SaveSkToPemFile. The writer and reader of the same PEM format apply different validation rules to the same field — this asymmetry is the root cause.', style_severity))
story.append(spacer(4))

story.append(label_para('What the Vulnerable Function Does:'))
story.append(body_para('`SaveSkToPemFile` in core/file.go lines 260–272 checks only that `file != nil`, then concatenates the identifier directly into the PEM block type and calls `pem.Encode`.'))
story.append(body_para('<b>What it does NOT do:</b> does not validate that identifier is non-empty. Does not validate that identifier passes `isValidPemPublicKeySuffix`. Does not check for leading/trailing whitespace or control characters.'))
story.append(body_para('<b>Call chain:</b> key generator → `SaveSkToPemFile(file, "", skBytes)` → `pem.Encode` writes block with type `"PRIVATE KEY for "` → file written successfully → node restart → `LoadSkPkFromPemFile` → `isValidPemPublicKeySuffix("")` returns `false` → `ErrPemFileIsInvalid` → node fails to start.'))
story.append(spacer(4))

story.append(label_para('The Fix:'))
story.append(body_para('<b>BEFORE</b> (core/file.go lines 260–272 — exact code from file):'))
story.append(make_code_block('func SaveSkToPemFile(file *os.File, identifier string, skBytes []byte) error {\n    if file == nil {\n        return ErrNilFile\n    }\n\n    blk := pem.Block{\n        Type:  "PRIVATE KEY for " + identifier,\n        Bytes: skBytes,\n    }\n\n    return pem.Encode(file, &blk)\n}'))
story.append(body_para('<b>AFTER:</b>'))
story.append(make_code_block('func SaveSkToPemFile(file *os.File, identifier string, skBytes []byte) error {\n    if file == nil {\n        return ErrNilFile\n    }\n    if !isValidPemPublicKeySuffix(identifier) {\n        return fmt.Errorf("%w invalid identifier for PEM block type", ErrPemFileIsInvalid)\n    }\n\n    blk := pem.Block{\n        Type:  "PRIVATE KEY for " + identifier,\n        Bytes: skBytes,\n    }\n\n    return pem.Encode(file, &blk)\n}'))
story.append(body_para('<b>Why This Fix Is Safe:</b> `isValidPemPublicKeySuffix` is already defined in the same file (line 247). `fmt` is already imported. No API changes — the new error path only fires for inputs that would produce an unloadable PEM file anyway.'))
story.append(spacer(4))

story.append(label_para('Integration Impact — Will It Break Existing Flow:'))
for item in [
    '<b>No existing tests break.</b> The existing `TestSaveSkToPemFile` "should work" sub-test passes `"data"` as the identifier — it passes `isValidPemPublicKeySuffix` and continues to pass unchanged.',
    '<b>No runtime flow breaks.</b> Every existing production caller passes a real public key string which already satisfies `isValidPemPublicKeySuffix`. The new guard is unreachable for all current valid callers.',
    '<b>Smooth integration:</b> Drop-in safe. No import changes needed.',
]:
    story.append(bullet_para(item))
story.append(spacer(4))

story.append(label_para('If Left Unfixed — Consequences:'))
for item in [
    'No immediate production risk — all current callers pass valid identifiers.',
    'Becomes a hard-to-diagnose node startup failure the moment any downstream developer passes an empty, whitespace-padded, or control-character-containing identifier. The write succeeds with no error; the node fails to start on the next restart with `ErrPemFileIsInvalid` and no pointer to the write-time cause.',
    '<b>Recommended to fix before the codebase grows. Not mandatory today.</b>',
]:
    story.append(bullet_para(item))
story.append(spacer(6))
story.append(hr())

# ── Finding D ─────────────────────────────────────────────────────────────────

story.append(finding_heading('Finding D — CODE QUALITY — CreateFile Creates Directory with os.ModePerm (0777) in core/file.go line 124'))

classif_d = [
    ['CWE:', 'CWE-732 (Incorrect Permission Assignment for Critical Resource)'],
    ['CVSS v3.1 Score:', '3.3 (Low) — AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N'],
    ['Severity:', 'Low'],
    ['Fix Required:', 'Conditional — verify deployment environment first'],
    ['Runtime Impact:', 'CreateFile calls os.MkdirAll(absPath, os.ModePerm) at line 124. os.ModePerm is 0777 — world-readable, world-writable, world-executable before umask. On a system with a permissive umask (e.g. 0000 or 0002), the created directory is writable by all local users. The file inside uses FileModeUserReadWrite (0600), but the directory itself is 0777.'],
    ['Monitoring Impact:', 'No error logged. The directory is created silently with world-write permissions. The permission mismatch between the directory (0777) and the files inside it (0600) is not flagged anywhere.'],
]
ct_d = Table(classif_d, colWidths=[30*mm, PAGE_WIDTH-30*mm])
ct_d.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTNAME',     (1,0), (1,-1), 'Helvetica'),
    ('FONTSIZE',     (0,0), (-1,-1), 8),
    ('TOPPADDING',   (0,0), (-1,-1), 3),
    ('BOTTOMPADDING',(0,0), (-1,-1), 3),
    ('LEFTPADDING',  (0,0), (-1,-1), 5),
    ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ('BACKGROUND',   (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
    ('GRID',         (0,0), (-1,-1), 0.3, C_BORDER),
    ('TEXTCOLOR',    (0,0), (-1,-1), C_DARK_GREY),
]))
story.append(ct_d)
story.append(spacer(6))

story.append(label_para('The Fix:'))
story.append(body_para('<b>BEFORE</b> (core/file.go line 124 — exact code from file):'))
story.append(make_code_block('err = os.MkdirAll(absPath, os.ModePerm)'))
story.append(body_para('<b>AFTER:</b>'))
story.append(make_code_block('err = os.MkdirAll(absPath, 0700)'))
story.append(body_para('<b>What each line does:</b> `0700` — owner read/write/execute only. Consistent with `FileModeUserReadWrite` (`0600`) on the files inside. No other local user can list, create, or delete files in the directory.'))
story.append(body_para('<b>Why This Fix Is Safe:</b> The node process is the only consumer of the created directory. `0700` gives the node full access. No other process needs access to the log/key directory.'))
story.append(spacer(4))

story.append(label_para('If Left Unfixed — Consequences:'))
for item in [
    'On a standard production Linux server with umask `0022`: effective directory permission is `0755` — group and world readable but not writable. Risk is low and the node operates normally.',
    'In containers running as root with umask `0000` or on systems with permissive umask: the directory is world-writable. Any co-located process can create, rename, or delete files inside it including log files and key files.',
    '<b>Not mandatory on standard deployments. Mandatory in containers with permissive umask. Verify your deployment environment before deciding.</b>',
]:
    story.append(bullet_para(item))
story.append(spacer(6))
story.append(hr())

# ── Finding E ─────────────────────────────────────────────────────────────────

story.append(finding_heading('Finding E — CODE QUALITY — GetPBFTThreshold and GetPBFTFallbackThreshold Return Threshold 1 for consensusSize 0 or Negative in core/common.go lines 46–52'))

classif_e = [
    ['CWE:', 'CWE-20 (Improper Input Validation)'],
    ['CVSS v3.1 Score:', '3.1 (Low) — AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N'],
    ['Severity:', 'Low'],
    ['Fix Required:', 'Recommended — defence-in-depth before upstream validation is refactored'],
    ['Runtime Impact:', 'GetPBFTThreshold(0) returns 0*2/3 + 1 = 1. GetPBFTThreshold(-1) returns -1*2/3 + 1 = 1 (Go integer division truncates toward zero). GetPBFTFallbackThreshold(0) returns 0*1/2 + 1 = 1. A threshold of 1 means a single node can reach consensus alone — the pBFT safety guarantee collapses.'],
    ['Monitoring Impact:', 'No error logged. No panic. The function returns a numerically valid but semantically wrong threshold. The caller has no signal that the input was invalid.'],
]
ct_e = Table(classif_e, colWidths=[30*mm, PAGE_WIDTH-30*mm])
ct_e.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTNAME',     (1,0), (1,-1), 'Helvetica'),
    ('FONTSIZE',     (0,0), (-1,-1), 8),
    ('TOPPADDING',   (0,0), (-1,-1), 3),
    ('BOTTOMPADDING',(0,0), (-1,-1), 3),
    ('LEFTPADDING',  (0,0), (-1,-1), 5),
    ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ('BACKGROUND',   (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
    ('GRID',         (0,0), (-1,-1), 0.3, C_BORDER),
    ('TEXTCOLOR',    (0,0), (-1,-1), C_DARK_GREY),
]))
story.append(ct_e)
story.append(spacer(6))

story.append(label_para('The Fix:'))
story.append(body_para('<b>BEFORE</b> (core/common.go lines 46–52 — exact code from file):'))
story.append(make_code_block('func GetPBFTThreshold(consensusSize int) int {\n    return consensusSize*2/3 + 1\n}\n\nfunc GetPBFTFallbackThreshold(consensusSize int) int {\n    return consensusSize*1/2 + 1\n}'))
story.append(body_para('<b>AFTER:</b>'))
story.append(make_code_block('func GetPBFTThreshold(consensusSize int) int {\n    if consensusSize <= 0 {\n        return 0\n    }\n    return consensusSize*2/3 + 1\n}\n\nfunc GetPBFTFallbackThreshold(consensusSize int) int {\n    if consensusSize <= 0 {\n        return 0\n    }\n    return consensusSize*1/2 + 1\n}'))
story.append(body_para('<b>Why This Fix Is Safe:</b> Additive only for invalid inputs. All valid consensus sizes (`>= 2`) produce the same result as before.'))
story.append(spacer(4))

story.append(label_para('If Left Unfixed — Consequences:'))
for item in [
    'No immediate production risk — all current callers in mx-chain-go pass validated consensus sizes of `>= 2`. The guard is never reached today.',
    'Becomes a critical consensus safety failure if any future upstream change removes or bypasses the consensus size validation and passes `0` or a negative value. `GetPBFTThreshold(0)` returns `1` — a single node can reach consensus alone with no error, no log, no alert.',
    '<b>Not mandatory today. Recommended as a defence-in-depth measure before any upstream consensus size validation is refactored.</b>',
]:
    story.append(bullet_para(item))
story.append(spacer(6))
story.append(hr())

print("Step 7: Findings C, D, E built")

# ─── SECTION 3: FALSE POSITIVES ───────────────────────────────────────────────

story.append(section_heading('SECTION 3 — FALSE POSITIVES'))
story.append(spacer(4))

story.append(finding_heading('Finding 6 — FALSE POSITIVE — UniqueIdentifier Returns Non-Printable Bytes'))

story.append(label_para('What the Scanner Flagged:'))
story.append(body_para('`UniqueIdentifier()` in core/common.go returns `string(buff)` where `buff` is a 32-byte slice filled by `io.ReadFull(rand.Reader, buff)`. The resulting string contains non-printable, non-UTF-8 bytes. Flagged as potential unsafe string construction or encoding issue.'))
story.append(spacer(4))

story.append(label_para('Why It Is Not a Vulnerability:'))
story.append(body_para('`string(buff)` in Go is a valid byte-to-string conversion — it does not require the bytes to be valid UTF-8. The Go specification explicitly allows strings to contain arbitrary bytes. `UniqueIdentifier()` is documented as returning a "unique string identifier of 32 bytes" — the bytes are used as an opaque identifier, not as human-readable text. The non-printable bytes are intentional — they maximise entropy in the identifier. The previous audit\'s Finding 1 (rand.Read error discarded) is now fixed — `io.ReadFull` captures the error and panics on failure. The non-printable byte content is correct and intentional.'))
story.append(spacer(4))

story.append(label_para('Action required:'))
story.append(body_para('None. The non-printable byte content is correct and intentional.'))
story.append(spacer(6))
story.append(hr())

print("Step 8: Section 3 built")

# ─── SECTION 4: FEATURE SECURITY ASSESSMENT ───────────────────────────────────

story.append(section_heading('SECTION 4 — FEATURE SECURITY ASSESSMENT'))
story.append(spacer(4))

def status_cell(text):
    if text == 'VULNERABLE':
        c = C_RED
    elif text == 'PARTIAL ISSUE':
        c = C_ORANGE
    elif text == 'SECURE':
        c = C_GREEN
    else:
        c = C_DARK_GREY
    return Paragraph(f'<b>{escape(text)}</b>',
        ParagraphStyle('sc', fontName='Helvetica-Bold', fontSize=7.5, textColor=c, leading=10))

def note_cell(text):
    def replace_code(m):
        return f'<font name="Courier" size="7">{escape(m.group(1))}</font>'
    text = re.sub(r'`([^`]+)`', replace_code, text)
    return Paragraph(text,
        ParagraphStyle('nc', fontName='Helvetica', fontSize=7.5, textColor=C_DARK_GREY, leading=10))

feat_header = [
    Paragraph('<b>Feature Area</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Status</b>',       ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Notes</b>',        ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
]

feat_rows = [
    [note_cell('DRWA Denial Code Vocabulary'),  status_cell('PARTIAL ISSUE'), note_cell('16 constants defined (15 concrete + DenialUnknown sentinel). IsKnown() correct. IsValid() incorrectly accepts DenialUnknown — re-introduces compliance reporting failure. Fix: Finding A.')],
    [note_cell('DRWA Storage Key Prefixes'),    status_cell('SECURE'),        note_cell('StorageKeyPrefix typed. AllStorageKeyPrefixes() present. IsValid() and non-overlap tests present. Previous Finding 4 fixed.')],
    [note_cell('DRWA Test Coverage'),           status_cell('PARTIAL ISSUE'), note_cell('Uniqueness, IsKnown(), IsValid(), NormalizeDenialCode all tested. Missing: AllDenialCodes() count assertion (len == 15). Fix: Section 7.')],
    [note_cell('Entropy Safety (UniqueIdentifier)'), status_cell('SECURE'),   note_cell('io.ReadFull + panic on failure. Error is no longer discarded. Previous Finding 1 fixed.')],
    [note_cell('PEM Key Loading'),              status_cell('PARTIAL ISSUE'), note_cell('strings.HasPrefix + isValidPemPublicKeySuffix correct in loaders. Missing: identifier validation in SaveSkToPemFile — writer/reader asymmetry. Fix: Finding C.')],
    [note_cell('File Descriptor Management'),   status_cell('VULNERABLE'),    note_cell('LoadTomlFileToMap defers f.Close() after two early-return points — fd leaked on f.Stat() and f.Read() error paths. All other functions in the same file are correct. Fix: Finding B.')],
    [note_cell('Directory Permissions'),        status_cell('PARTIAL ISSUE'), note_cell('CreateFile uses os.ModePerm (0777) for MkdirAll. Should be 0700 to match FileModeUserReadWrite (0600) on files inside. Fix: Finding D.')],
    [note_cell('PBFT Threshold Calculation'),   status_cell('PARTIAL ISSUE'), note_cell('No guard for consensusSize <= 0. Returns threshold 1 for size 0 or negative — collapses Byzantine fault tolerance silently. Fix: Finding E.')],
    [note_cell('Cryptographic Hashing'),        status_cell('SECURE'),        note_cell('hashing/blake2b, hashing/keccak, hashing/sha256 — all use standard library implementations with no custom logic. No issues found.')],
    [note_cell('Marshaling / Unmarshaling'),    status_cell('SECURE'),        note_cell('GogoProtoMarshalizer calls msg.Reset() before unmarshal — prevents state leakage. sizeCheckUnmarshalizer enforces size delta check. JsonMarshalizer uses encoding/json. No issues found.')],
    [note_cell('Address Encoding (bech32/hex)'),status_cell('SECURE'),        note_cell('bech32PubkeyConverter validates prefix, length, and bit conversion. hexPubkeyConverter validates length after decode. Both return explicit errors on all failure paths. No issues found.')],
    [note_cell('Transaction Integrity'),        status_cell('SECURE'),        note_cell('Transaction.CheckIntegrity() validates nil signature, nil value, negative value, and username length. GetDataForSigning uses encoder and marshaller with nil checks. No issues found.')],
    [note_cell('Outport Block Topics'),         status_cell('SECURE'),        note_cell('data/outport/consts.go defines topic strings as typed constants. No injection surface. No issues found.')],
    [note_cell('Data Partitioning'),            status_cell('SECURE'),        note_cell('SizeDataPacker and SimpleDataPacker both validate limit >= minimumMaxPacketSizeInBytes and data != nil. Marshal errors are propagated. No issues found.')],
    [note_cell('Concurrency'),                  status_cell('SECURE'),        note_cell('core/atomic/ types use sync/atomic. core/sync/keymutex.go and rwmutex.go use sync.Mutex and sync.RWMutex. core/container/mutexMap.go uses sync.RWMutex. No data races detected.')],
    [note_cell('DRWA Package Isolation'),       status_cell('SECURE'),        note_cell('data/drwa/ package has zero imports beyond testing. No coupling to any other package. Confirmed by go build ./... and go test ./... passing clean.')],
]

feat_table = Table([feat_header] + feat_rows, colWidths=[45*mm, 28*mm, PAGE_WIDTH-73*mm], repeatRows=1)
feat_table.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), C_HEADER_BG),
    ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
    ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',      (0,0), (-1,0), 8),
    ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ('TOPPADDING',    (0,0), (-1,0), 6),
    ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
    ('FONTSIZE',      (0,1), (-1,-1), 7.5),
    ('TOPPADDING',    (0,1), (-1,-1), 5),
    ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ('LEFTPADDING',   (0,0), (-1,-1), 6),
    ('RIGHTPADDING',  (0,0), (-1,-1), 6),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.white, C_LIGHT_GREY]),
    ('GRID',          (0,0), (-1,-1), 0.4, C_BORDER),
    ('VALIGN',        (0,0), (-1,-1), 'TOP'),
]))
story.append(feat_table)
story.append(spacer(8))
story.append(hr())

print("Step 9: Section 4 built")

# ─── SECTION 5: ACTION PLAN ───────────────────────────────────────────────────

story.append(section_heading('SECTION 5 — ACTION PLAN'))
story.append(spacer(4))

# ── Mandatory Fixes table ──────────────────────────────────────────────────────

story.append(Paragraph('<b>Mandatory Fixes (Must Apply Before Production)</b>',
    ParagraphStyle('SubHead', fontName='Helvetica-Bold', fontSize=10,
                   textColor=C_RED, spaceAfter=6, spaceBefore=4, leading=13)))

def ap_cell(text, bold=False, color=C_DARK_GREY):
    def replace_code(m):
        return f'<font name="Courier" size="7">{escape(m.group(1))}</font>'
    text = re.sub(r'`([^`]+)`', replace_code, text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    fn = 'Helvetica-Bold' if bold else 'Helvetica'
    return Paragraph(text, ParagraphStyle('apc', fontName=fn, fontSize=7.5,
                                          textColor=color, leading=10))

mand_header = [
    Paragraph('<b>Priority</b>',   ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Action</b>',     ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>File</b>',       ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Line</b>',       ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Effort</b>',     ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Why Mandatory</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
]

mand_rows = [
    [ap_cell('P1 — CRITICAL', bold=True, color=C_RED),
     ap_cell('Change `IsValid()` to return `code.IsKnown()` only. Update test: `DenialUnknown.IsValid()` must be `false`.'),
     ap_cell('data/drwa/constants.go'),
     ap_cell('67'),
     ap_cell('5 min'),
     ap_cell('Regulatory violations accumulate permanently with every unrecognized denial code. MiCA filing failure.')],

    [ap_cell('P1 — CRITICAL', bold=True, color=C_RED),
     ap_cell('Move `defer f.Close()` to immediately after `OpenFile` succeeds, before `f.Stat()` call.'),
     ap_cell('core/file.go'),
     ap_cell('89'),
     ap_cell('5 min'),
     ap_cell('Node crashes silently under disk pressure or in containers. Permanent DoS until restart.')],

    [ap_cell('P1 — CRITICAL', bold=True, color=C_RED),
     ap_cell('Add `AllDenialCodes()` count assertion (`len == 15`) and `IsValid()` check per code.'),
     ap_cell('data/drwa/constants_test.go'),
     ap_cell('—'),
     ap_cell('5 min'),
     ap_cell('Regulatory compliance gap grows with every new denial code added without this guard.')],
]

mand_table = Table([mand_header] + mand_rows,
    colWidths=[22*mm, 48*mm, 38*mm, 12*mm, 14*mm, PAGE_WIDTH-134*mm], repeatRows=1)
mand_table.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), C_HEADER_BG),
    ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
    ('FONTSIZE',      (0,0), (-1,0), 8),
    ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ('TOPPADDING',    (0,0), (-1,0), 6),
    ('FONTSIZE',      (0,1), (-1,-1), 7.5),
    ('TOPPADDING',    (0,1), (-1,-1), 5),
    ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ('LEFTPADDING',   (0,0), (-1,-1), 5),
    ('RIGHTPADDING',  (0,0), (-1,-1), 5),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.HexColor('#fff5f5'), colors.HexColor('#fef0f0')]),
    ('GRID',          (0,0), (-1,-1), 0.4, C_BORDER),
    ('VALIGN',        (0,0), (-1,-1), 'TOP'),
]))
story.append(mand_table)
story.append(spacer(8))

# ── Recommended Fixes table ────────────────────────────────────────────────────

story.append(Paragraph('<b>Recommended Fixes (Apply Before Codebase Grows)</b>',
    ParagraphStyle('SubHead2', fontName='Helvetica-Bold', fontSize=10,
                   textColor=C_ORANGE, spaceAfter=6, spaceBefore=4, leading=13)))

rec_header = [
    Paragraph('<b>Priority</b>',        ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Action</b>',          ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>File</b>',            ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Line</b>',            ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Effort</b>',          ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Risk if Deferred</b>',ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
]

rec_rows = [
    [ap_cell('P2 — Recommended', color=C_ORANGE),
     ap_cell('Add `isValidPemPublicKeySuffix(identifier)` guard in `SaveSkToPemFile` before `pem.Encode`.'),
     ap_cell('core/file.go'), ap_cell('261'), ap_cell('10 min'),
     ap_cell('Latent node startup failure when any downstream developer passes invalid identifier.')],

    [ap_cell('P2 — Conditional', color=C_BLUE),
     ap_cell('Change `os.MkdirAll` permission from `os.ModePerm` to `0700`.'),
     ap_cell('core/file.go'), ap_cell('124'), ap_cell('2 min'),
     ap_cell('Only critical in containers with permissive umask. Verify deployment before applying.')],

    [ap_cell('P2 — Recommended', color=C_ORANGE),
     ap_cell('Add `consensusSize <= 0` guard returning `0` in both PBFT threshold functions.'),
     ap_cell('core/common.go'), ap_cell('46, 51'), ap_cell('5 min'),
     ap_cell('Critical consensus safety failure if upstream validation ever regresses.')],

    [ap_cell('P3 — Low', color=C_MID_GREY),
     ap_cell('Add trailing-space PEM suffix sub-tests to `TestLoadSkPkFromPemFile` and `TestLoadAllKeysFromPemFile`.'),
     ap_cell('core/file_test.go'), ap_cell('—'), ap_cell('10 min'),
     ap_cell('Test coverage gap only — no runtime risk.')],
]

rec_table = Table([rec_header] + rec_rows,
    colWidths=[22*mm, 48*mm, 38*mm, 12*mm, 14*mm, PAGE_WIDTH-134*mm], repeatRows=1)
rec_table.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), C_HEADER_BG),
    ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
    ('FONTSIZE',      (0,0), (-1,0), 8),
    ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ('TOPPADDING',    (0,0), (-1,0), 6),
    ('FONTSIZE',      (0,1), (-1,-1), 7.5),
    ('TOPPADDING',    (0,1), (-1,-1), 5),
    ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ('LEFTPADDING',   (0,0), (-1,-1), 5),
    ('RIGHTPADDING',  (0,0), (-1,-1), 5),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.white, C_LIGHT_GREY]),
    ('GRID',          (0,0), (-1,-1), 0.4, C_BORDER),
    ('VALIGN',        (0,0), (-1,-1), 'TOP'),
]))
story.append(rec_table)
story.append(spacer(8))

# ── Test Impact Summary table ──────────────────────────────────────────────────

story.append(Paragraph('<b>Test Impact Summary</b>',
    ParagraphStyle('SubHead3', fontName='Helvetica-Bold', fontSize=10,
                   textColor=C_DARK_GREY, spaceAfter=6, spaceBefore=4, leading=13)))

ti_header = [
    Paragraph('<b>Fix</b>',                  ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>File</b>',                 ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Test Action Required</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
]

ti_rows = [
    [ap_cell('Finding A — IsValid()'),         ap_cell('data/drwa/constants_test.go'), ap_cell('Change assertion: DenialUnknown.IsValid() must return false. Add TestDenialUnknown_IsNotStorable.')],
    [ap_cell('Finding B — fd leak'),           ap_cell('core/file_test.go'),           ap_cell('Add test: repeated error-path calls do not leak file descriptors. Verify with /proc/self/fd count.')],
    [ap_cell('Finding C — SaveSkToPemFile'),   ap_cell('core/file_test.go'),           ap_cell('Add 3 sub-tests: empty identifier → ErrPemFileIsInvalid; whitespace-padded → ErrPemFileIsInvalid; control char → ErrPemFileIsInvalid.')],
    [ap_cell('Finding D — ModePerm'),          ap_cell('core/file_test.go'),           ap_cell('Add test: created directory has mode 0700.')],
    [ap_cell('Finding E — PBFT guard'),        ap_cell('core/common_test.go'),         ap_cell('Add 4 assertions: GetPBFTThreshold(0)==0, GetPBFTThreshold(-1)==0, GetPBFTFallbackThreshold(0)==0, GetPBFTFallbackThreshold(-1)==0.')],
    [ap_cell('Section 7 — count test'),        ap_cell('data/drwa/constants_test.go'), ap_cell('Add TestAllDenialCodes_Complete asserting len==15 and all codes pass IsValid() (after Finding A fix applied).')],
    [ap_cell('Trailing-space PEM'),            ap_cell('core/file_test.go'),           ap_cell('Add trailing-space suffix sub-test to both TestLoadSkPkFromPemFile and TestLoadAllKeysFromPemFile.')],
]

ti_table = Table([ti_header] + ti_rows,
    colWidths=[38*mm, 42*mm, PAGE_WIDTH-80*mm], repeatRows=1)
ti_table.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), C_HEADER_BG),
    ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
    ('FONTSIZE',      (0,0), (-1,0), 8),
    ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ('TOPPADDING',    (0,0), (-1,0), 6),
    ('FONTSIZE',      (0,1), (-1,-1), 7.5),
    ('TOPPADDING',    (0,1), (-1,-1), 5),
    ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ('LEFTPADDING',   (0,0), (-1,-1), 5),
    ('RIGHTPADDING',  (0,0), (-1,-1), 5),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.white, C_LIGHT_GREY]),
    ('GRID',          (0,0), (-1,-1), 0.4, C_BORDER),
    ('VALIGN',        (0,0), (-1,-1), 'TOP'),
]))
story.append(ti_table)
story.append(spacer(8))

# ── Integration Impact Summary table ──────────────────────────────────────────

story.append(Paragraph('<b>Integration Impact Summary</b>',
    ParagraphStyle('SubHead4', fontName='Helvetica-Bold', fontSize=10,
                   textColor=C_DARK_GREY, spaceAfter=6, spaceBefore=4, leading=13)))

ii_header = [
    Paragraph('<b>Finding</b>',                        ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Mandatory?</b>',                     ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Breaks Existing Tests?</b>',         ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Breaks Existing Runtime Flow?</b>',  ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
    Paragraph('<b>Deployment Verification Required?</b>', ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)),
]

ii_rows = [
    [ap_cell('A — IsValid() fix'),        ap_cell('YES — fix before production', bold=True, color=C_RED), ap_cell('Yes — 1 test assertion must be updated first', color=C_ORANGE), ap_cell('No'), ap_cell('No')],
    [ap_cell('B — defer move'),           ap_cell('YES — fix before production', bold=True, color=C_RED), ap_cell('No'), ap_cell('No'), ap_cell('No')],
    [ap_cell('Section 7 — count test'),   ap_cell('YES — fix before production', bold=True, color=C_RED), ap_cell('No'), ap_cell('No'), ap_cell('No')],
    [ap_cell('C — SaveSkToPemFile guard'),ap_cell('Recommended', color=C_ORANGE),  ap_cell('No'), ap_cell('No'), ap_cell('No')],
    [ap_cell('D — 0777 → 0700'),          ap_cell('Conditional', color=C_BLUE),    ap_cell('No'), ap_cell('Only if another process reads the directory', color=C_ORANGE), ap_cell('Yes — verify no sidecar reads node directory', color=C_ORANGE)],
    [ap_cell('E — PBFT zero guard'),      ap_cell('Recommended', color=C_ORANGE),  ap_cell('No'), ap_cell('No'), ap_cell('No')],
]

ii_table = Table([ii_header] + ii_rows,
    colWidths=[30*mm, 28*mm, 32*mm, 34*mm, PAGE_WIDTH-124*mm], repeatRows=1)
ii_table.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), C_HEADER_BG),
    ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
    ('FONTSIZE',      (0,0), (-1,0), 8),
    ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ('TOPPADDING',    (0,0), (-1,0), 6),
    ('FONTSIZE',      (0,1), (-1,-1), 7.5),
    ('TOPPADDING',    (0,1), (-1,-1), 5),
    ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ('LEFTPADDING',   (0,0), (-1,-1), 5),
    ('RIGHTPADDING',  (0,0), (-1,-1), 5),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.white, C_LIGHT_GREY]),
    ('GRID',          (0,0), (-1,-1), 0.4, C_BORDER),
    ('VALIGN',        (0,0), (-1,-1), 'TOP'),
]))
story.append(ii_table)
story.append(spacer(8))
story.append(hr())

print("Step 10: Section 5 built")

# ─── SECTION 6: FINAL DECISION ────────────────────────────────────────────────

story.append(section_heading('SECTION 6 — FINAL DECISION'))
story.append(spacer(4))

# ── Mandatory group ────────────────────────────────────────────────────────────

story.append(Paragraph('<b>Mandatory — Must Fix Before Production</b>',
    ParagraphStyle('Group', fontName='Helvetica-Bold', fontSize=10,
                   textColor=C_RED, spaceAfter=6, spaceBefore=4, leading=13)))

mand_items = [
    '<b>Finding A (IsValid() accepts DenialUnknown): NOT FIXED — Medium severity — MANDATORY.</b> `IsValid()` at data/drwa/constants.go line 67 returns `true` for `DenialUnknown`. Every unrecognized denial code path permanently stores a `DRWA_UNKNOWN` record in the compliance index. These records accumulate with every transaction, cannot be retroactively corrected, and constitute a direct MiCA Article 45 regulatory filing violation. A downstream switch with no `case DenialUnknown:` branch silently allows transfers that should be denied. <b>Fix:</b> change `IsValid()` to return `code.IsKnown()` only. <b>Integration:</b> update one test assertion in constants_test.go line 28 before applying — no runtime flow breaks.',

    '<b>Finding B (LoadTomlFileToMap fd leak): NOT FIXED — Medium severity — MANDATORY.</b> `defer f.Close()` at core/file.go line 89 is placed after two early-return points (lines 78, 86). Under disk pressure or in containers with low fd limits, every error-path call leaks one file descriptor permanently. The node crashes with "too many open files" at an unpredictable point during the incident with no log trail pointing to the root cause. <b>Fix:</b> move defer to immediately after `OpenFile` succeeds. <b>Integration:</b> drop-in safe — no existing tests break, no runtime flow breaks, no API changes.',

    '<b>Section 7 Gap (No AllDenialCodes count test): NOT FIXED — Medium severity — MANDATORY.</b> `AllDenialCodes()` exists but no test asserts `len == 15`. The moment a new denial code is added to the constants block and omitted from `AllDenialCodes()`, the entire downstream enforcement pipeline silently misses it — no test fails, no compile error, no warning. Regulated transfers are either silently allowed or denied with a generic error that has no regulatory attribution. <b>Fix:</b> add `TestAllDenialCodes_Complete`. <b>Integration:</b> adding a new test never breaks existing flow — drop-in safe.',
]
for item in mand_items:
    story.append(bullet_para(item))
story.append(spacer(6))

# ── Recommended group ──────────────────────────────────────────────────────────

story.append(Paragraph('<b>Recommended — Fix Before Codebase Grows</b>',
    ParagraphStyle('Group2', fontName='Helvetica-Bold', fontSize=10,
                   textColor=C_ORANGE, spaceAfter=6, spaceBefore=4, leading=13)))

rec_items = [
    '<b>Finding C (SaveSkToPemFile no identifier validation): NOT FIXED — Low severity — RECOMMENDED.</b> No immediate production risk — all current callers pass valid identifiers. Becomes a hard-to-diagnose node startup failure the moment any downstream developer passes an invalid identifier. Write succeeds silently; node fails to start on next restart with `ErrPemFileIsInvalid` and no pointer to the write-time cause. <b>Fix:</b> add `isValidPemPublicKeySuffix` guard before `pem.Encode`. <b>Integration:</b> drop-in safe — all existing callers pass valid identifiers, no existing tests break, no API changes.',

    '<b>Finding E (PBFT threshold no zero guard): NOT FIXED — Low severity — RECOMMENDED.</b> No immediate production risk — all current callers pass sizes `>= 2`. Becomes a critical consensus safety failure if upstream validation ever regresses and passes `0` or negative — `GetPBFTThreshold(0)` returns `1`, a single node can reach consensus alone with no error, no log, no alert. <b>Fix:</b> add `consensusSize <= 0` guard returning `0`. <b>Integration:</b> drop-in safe — all existing callers pass sizes `>= 2`, no existing tests break, no API changes.',
]
for item in rec_items:
    story.append(bullet_para(item))
story.append(spacer(6))

# ── Conditional group ──────────────────────────────────────────────────────────

story.append(Paragraph('<b>Conditional — Verify Deployment Environment First</b>',
    ParagraphStyle('Group3', fontName='Helvetica-Bold', fontSize=10,
                   textColor=C_BLUE, spaceAfter=6, spaceBefore=4, leading=13)))

cond_items = [
    '<b>Finding D (CreateFile os.ModePerm): NOT FIXED — Low severity — CONDITIONAL.</b> On standard Linux with umask `0022` the effective directory permission is `0755` — not writable, low risk. In containers running as root with umask `0000` the directory is world-writable and any co-located process can tamper with log and key files. <b>Fix:</b> change to `0700`. <b>Integration:</b> verify no sidecar or log aggregator reads the node directory before applying — safe for standard single-process deployments.',
]
for item in cond_items:
    story.append(bullet_para(item))
story.append(spacer(6))

# ── Dismissed group ────────────────────────────────────────────────────────────

story.append(Paragraph('<b>Dismissed</b>',
    ParagraphStyle('Group4', fontName='Helvetica-Bold', fontSize=10,
                   textColor=C_GREEN, spaceAfter=6, spaceBefore=4, leading=13)))

dism_items = [
    '<b>Finding 6 (UniqueIdentifier non-printable bytes): DISMISSED — False positive.</b> Non-printable bytes in `UniqueIdentifier()` return value are intentional — the function returns an opaque random identifier, not human-readable text. No fix required at this location.',
]
for item in dism_items:
    story.append(bullet_para(item))
story.append(spacer(8))

# ── Fix Priority Summary ───────────────────────────────────────────────────────

story.append(Paragraph('<b>Fix Priority Summary</b>',
    ParagraphStyle('PriSum', fontName='Helvetica-Bold', fontSize=10,
                   textColor=C_DARK_GREY, spaceAfter=6, spaceBefore=6, leading=13)))

priority_items = [
    'Fixing <b>Finding A + B + Section 7</b> = <b>Minimum required for production</b> — regulatory violations stopped, node DoS under disk pressure eliminated, exhaustiveness contract enforced. Total effort: 15 minutes.',
    'Fixing <b>Finding C + E</b> additionally = <b>Recommended before codebase grows</b> — PEM write/read symmetry restored, PBFT threshold functions reject invalid input explicitly. Total additional effort: 15 minutes.',
    'Fixing <b>Finding D</b> additionally = <b>Apply after verifying deployment</b> — directory permissions tightened. Total additional effort: 2 minutes.',
    'Fixing <b>everything</b> = <b>Perfect at Peak</b> — zero known security issues, all latent traps closed, all defence-in-depth gaps filled.',
]
for item in priority_items:
    story.append(body_para(item, style_priority))
story.append(spacer(8))
story.append(hr())

print("Step 11: Section 6 built")

# ─── SECTION 7: DRWA FLOW GAP ─────────────────────────────────────────────────

story.append(section_heading('SECTION 7 — DRWA FLOW GAP — No AllDenialCodes Exhaustiveness Count Test Between mx-chain-core-go and Downstream Enforcement'))
story.append(spacer(4))

classif_7 = [
    ['CWE:', 'CWE-691 (Insufficient Control Flow Management)'],
    ['Severity:', 'Medium'],
    ['Fix Required:', 'Yes — MANDATORY'],
]
ct_7 = Table(classif_7, colWidths=[30*mm, PAGE_WIDTH-30*mm])
ct_7.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTNAME',     (1,0), (1,-1), 'Helvetica'),
    ('FONTSIZE',     (0,0), (-1,-1), 8),
    ('TOPPADDING',   (0,0), (-1,-1), 3),
    ('BOTTOMPADDING',(0,0), (-1,-1), 3),
    ('LEFTPADDING',  (0,0), (-1,-1), 5),
    ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ('BACKGROUND',   (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
    ('GRID',         (0,0), (-1,-1), 0.3, C_BORDER),
    ('TEXTCOLOR',    (0,0), (-1,-1), C_DARK_GREY),
    ('TEXTCOLOR',    (1,2), (1,2), C_RED),
]))
story.append(ct_7)
story.append(spacer(6))

story.append(label_para('The DRWA Flow Context:'))
story.append(body_para('mx-chain-core-go is the starting repo in the DRWA pipeline. Its role is to define the shared vocabulary — the `DenialCode` type and its 15 known values — that every downstream repo imports and uses to make compliance decisions. The pipeline is:'))
story.append(spacer(4))

story.append(make_code_block(
    'mx-chain-core-go          (defines DenialCode vocabulary)\n'
    '     \u2193 imported by\n'
    'mx-chain-vm-common-go     (compliance gate \u2014 evaluates transfers, assigns DenialCode)\n'
    '     \u2193 imported by\n'
    'mx-chain-go               (node \u2014 executes compliance gate on every regulated transfer)\n'
    '     \u2193 emits OutportBlock with denial events\n'
    'mx-chain-es-indexer-go    (indexes denial records to Elasticsearch)\n'
    '     \u2193\n'
    'Compliance dashboards / Regulatory reporting tools'
))
story.append(spacer(4))

story.append(label_para('The Gap:'))
story.append(body_para('mx-chain-core-go defines 15 `DenialCode` constants and `AllDenialCodes()` returns all 15. The compliance gate in mx-chain-vm-common-go contains switch statements that handle these codes. There is no test in mx-chain-core-go that asserts `AllDenialCodes()` returns exactly 15 codes. Without this count assertion, a developer can add a 16th denial code to the constants block and omit it from `AllDenialCodes()` without any test failing — the exhaustiveness contract between mx-chain-core-go and downstream enforcement repos is not mechanically enforced.'))
story.append(spacer(4))

story.append(body_para('Concretely: if a 16th denial code — for example `DenialSovereignChainBlocked DenialCode = "DRWA_SOVEREIGN_CHAIN_BLOCKED"` — is added to constants.go in mx-chain-core-go but not to `AllDenialCodes()`, the following happens:'))
story.append(spacer(2))

gap_steps = [
    'mx-chain-core-go compiles and tests pass — the new constant is non-empty and unique',
    '`AllDenialCodes()` still returns 15 codes — the new constant is silently excluded',
    'mx-chain-vm-common-go imports the updated mx-chain-core-go — it compiles with no error because Go does not require switch exhaustiveness on string types',
    'The compliance gate switch in mx-chain-vm-common-go has no `case DenialSovereignChainBlocked:` branch — the new code falls to default',
    'The default branch either logs a warning and allows the transfer, or returns a generic error — neither is the correct compliance behaviour for the new denial reason',
    'No test in mx-chain-vm-common-go fails — the new code was never in `AllDenialCodes()`',
    'Regulated transfers that should be denied with `DRWA_SOVEREIGN_CHAIN_BLOCKED` are either silently allowed or denied with a generic error that has no regulatory attribution',
]
for i, step in enumerate(gap_steps, 1):
    story.append(bullet_para(f'{i}. {step}'))
story.append(spacer(4))

story.append(body_para('This gap is not a code bug in mx-chain-core-go — `AllDenialCodes()` is correctly implemented. It is a design gap between what mx-chain-core-go promises (a complete, authoritative vocabulary of denial reasons) and what it can guarantee (that `AllDenialCodes()` always reflects every constant in the block).'))
story.append(spacer(4))

story.append(label_para('Who Is Affected:'))
for item in [
    '<b>Compliance gate maintainers in mx-chain-vm-common-go</b> — they have no automated signal when a new `DenialCode` is added to mx-chain-core-go that is missing from `AllDenialCodes()`',
    '<b>Regulatory reporting tools</b> — they receive denial records with a code that has no corresponding enforcement rule in the gate, making the record unattributable',
    '<b>Compliance / Regulatory Officers</b> — regulatory filings contain denial events attributed to a code that the compliance gate never explicitly handled',
    '<b>On-call engineers</b> — default branch behaviour is unpredictable; some implementations allow the transfer, others deny it generically — the on-call cannot determine correct behaviour without reading both repos',
]:
    story.append(bullet_para(item))
story.append(spacer(4))

story.append(label_para('The Fix:'))
story.append(body_para('<b>Step 1</b> — add a test in data/drwa/constants_test.go that verifies `AllDenialCodes()` returns exactly 15 codes and that every code passes `IsValid()` (after Finding A fix is applied):'))
story.append(make_code_block(
    'func TestAllDenialCodes_Complete(t *testing.T) {\n'
    '    all := AllDenialCodes()\n'
    '    if len(all) != 15 {\n'
    '        t.Fatalf("expected 15 denial codes, got %d \u2014 update this test and "+\n'
    '            "the compliance gate switch in mx-chain-vm-common-go", len(all))\n'
    '    }\n'
    '    for _, code := range all {\n'
    '        if !code.IsValid() {\n'
    '            t.Fatalf("AllDenialCodes() returned invalid code: %s", code)\n'
    '        }\n'
    '    }\n'
    '}'
))
story.append(body_para('<b>Step 2</b> — add a test in mx-chain-vm-common-go that calls `drwa.AllDenialCodes()` and asserts that the compliance gate switch handles every returned code with a non-default branch. This test fails automatically when a new code is added to mx-chain-core-go without a corresponding enforcement branch in mx-chain-vm-common-go.'))
story.append(spacer(4))

story.append(label_para('Why This Gap Is Specific to This Repo:'))
story.append(body_para('mx-chain-core-go is the only repo in the DRWA pipeline that defines the denial code vocabulary. It is the single source of truth for what denial reasons exist. Every other repo in the pipeline is a consumer of this vocabulary. The gap exists because Go string-typed switches are not exhaustive — the compiler does not warn when a new string constant is added to an imported package and the importing package\'s switch does not handle it. This gap does not exist in mx-chain-vm-common-go or mx-chain-es-indexer-go — they are consumers, not definers.'))
story.append(spacer(4))

story.append(label_para('Why This Gap Matters for Regulatory Compliance:'))
story.append(body_para('MiCA Article 45 and equivalent regulations require that every transfer denial be attributed to a specific, documented compliance rule. A denial code that exists in the vocabulary but is excluded from `AllDenialCodes()` is invisible to the exhaustiveness contract — downstream enforcement repos have no automated signal to handle it. This is not a theoretical risk — it is the exact failure mode that occurs every time a new denial reason is added to mx-chain-core-go without a corresponding entry in `AllDenialCodes()` and a corresponding update to mx-chain-vm-common-go.'))
story.append(spacer(8))

print("Step 12: Section 7 built")

# ─── PAGE NUMBERS ─────────────────────────────────────────────────────────────

def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(C_MID_GREY)
    page_num = canvas.getPageNumber()
    text = f'Security Findings & Fix Report — mx-chain-core-go    |    Page {page_num}'
    canvas.drawCentredString(A4[0] / 2, 10*mm, text)
    # Top border line
    canvas.setStrokeColor(C_BORDER)
    canvas.setLineWidth(0.3)
    canvas.line(20*mm, A4[1] - 15*mm, A4[0] - 20*mm, A4[1] - 15*mm)
    canvas.restoreState()

# ─── BUILD PDF ────────────────────────────────────────────────────────────────

print("Building PDF...")
doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f"PDF generated successfully: {output_pdf}")
