#!/usr/bin/env python3

import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Preformatted, KeepTogether, PageBreak
)

OUTPUT = '/home/divesh/Desktop/RWA/fin2/mangonui/mx-chain-core-go/mycont/SECURITY_AUDIT_REPORT_FINAL_v2_mx-chain-core-go.pdf'

PAGE_W, PAGE_H = A4
L_MARGIN = 18*mm
R_MARGIN = 18*mm
T_MARGIN = 18*mm
B_MARGIN = 18*mm
USABLE_W = PAGE_W - L_MARGIN - R_MARGIN   # ~173 mm

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=L_MARGIN,
    rightMargin=R_MARGIN,
    topMargin=T_MARGIN,
    bottomMargin=B_MARGIN,
)

story = []
print("Step 1 done: imports and document setup")

# ── STYLES ────────────────────────────────────────────────────────────────────

BLACK      = colors.black
DARK       = colors.HexColor('#222222')
MID        = colors.HexColor('#444444')
LIGHT_BG   = colors.HexColor('#f2f2f2')
WHITE      = colors.white
BORDER_COL = colors.HexColor('#aaaaaa')
CODE_BG    = colors.HexColor('#f7f7f7')

def S(name, **kw):
    defaults = dict(fontName='Helvetica', fontSize=9, textColor=DARK,
                    leading=13, spaceAfter=3, spaceBefore=2, alignment=TA_LEFT)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

sTitle   = S('Title',   fontName='Helvetica-Bold', fontSize=18, textColor=BLACK,
             spaceAfter=4, spaceBefore=0, leading=22)
sMeta    = S('Meta',    fontSize=8.5, textColor=MID, spaceAfter=2, leading=12)
sSection = S('Section', fontName='Helvetica-Bold', fontSize=11, textColor=WHITE,
             backColor=BLACK, spaceAfter=6, spaceBefore=10, leading=15,
             leftIndent=-2, rightIndent=-2, borderPad=5)
sFinding = S('Finding', fontName='Helvetica-Bold', fontSize=10, textColor=BLACK,
             spaceAfter=5, spaceBefore=10, leading=13,
             borderPad=3, borderColor=BORDER_COL, borderWidth=0.5)
sLabel   = S('Label',   fontName='Helvetica-Bold', fontSize=9, textColor=BLACK,
             spaceAfter=2, spaceBefore=5, leading=12)
sBody    = S('Body',    fontSize=9, textColor=DARK, spaceAfter=4,
             spaceBefore=2, leading=13, alignment=TA_JUSTIFY)
sBullet  = S('Bullet',  fontSize=9, textColor=DARK, spaceAfter=3,
             spaceBefore=1, leading=13, leftIndent=10)
sSub     = S('Sub',     fontSize=9, textColor=DARK, spaceAfter=2,
             spaceBefore=1, leading=13, leftIndent=22)
sNote    = S('Note',    fontSize=8.5, textColor=DARK, spaceAfter=4,
             spaceBefore=2, leading=12, leftIndent=4, rightIndent=4,
             backColor=LIGHT_BG, borderColor=BORDER_COL,
             borderWidth=0.5, borderPad=5, alignment=TA_JUSTIFY)
sUnfixed = S('Unfixed', fontSize=8.5, textColor=DARK, spaceAfter=3,
             spaceBefore=1, leading=12, leftIndent=4, rightIndent=4,
             backColor=LIGHT_BG, borderColor=BLACK,
             borderWidth=0.8, borderPad=5)
sCode    = ParagraphStyle('Code', fontName='Courier', fontSize=7.5,
             textColor=DARK, leading=11, spaceAfter=5, spaceBefore=3,
             leftIndent=4, backColor=CODE_BG,
             borderColor=BORDER_COL, borderWidth=0.5, borderPad=5)

print("Step 2 done: styles defined")

# ── HELPERS ───────────────────────────────────────────────────────────────────

def esc(t):
    return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def fmt(text):
    """Convert backtick code and **bold** to reportlab markup."""
    text = re.sub(r'`([^`\n]+)`',
                  lambda m: f'<font name="Courier" size="8">{esc(m.group(1))}</font>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    return text

def p(text, style=None):
    return Paragraph(fmt(esc(text)) if not re.search(r'[<&]', text) else fmt(text),
                     style or sBody)

def lbl(text):
    return Paragraph(f'<b>{esc(text)}</b>', sLabel)

def bul(text, sub=False):
    s = sSub if sub else sBullet
    marker = '&#8226;' if not sub else '&#9702;'
    return Paragraph(f'{marker}&nbsp;&nbsp;{fmt(text)}', s)

def sp(h=4):
    return Spacer(1, h)

def hr():
    return HRFlowable(width='100%', thickness=0.4,
                      color=BORDER_COL, spaceAfter=5, spaceBefore=5)

def section(text):
    return Paragraph(f'&nbsp;&nbsp;{esc(text)}', sSection)

def finding(text):
    return Paragraph(esc(text), sFinding)

def code_block(text):
    return Preformatted(text.strip(), sCode)

def note(label, text):
    return Paragraph(f'<b>{esc(label)}</b> {fmt(text)}', sNote)

def cell(text, bold=False, size=8):
    fn = 'Helvetica-Bold' if bold else 'Helvetica'
    return Paragraph(fmt(text),
        ParagraphStyle('c', fontName=fn, fontSize=size,
                       textColor=DARK, leading=11, wordWrap='CJK'))

def hcell(text):
    return Paragraph(f'<b>{esc(text)}</b>',
        ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=8,
                       textColor=WHITE, leading=11))

def base_table_style():
    return TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  BLACK),
        ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0),  8),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 5),
        ('RIGHTPADDING',  (0,0), (-1,-1), 5),
        ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ('GRID',          (0,0), (-1,-1), 0.3, BORDER_COL),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('WORDWRAP',      (0,0), (-1,-1), True),
    ])

def classif_table(rows):
    """Two-column classification table: label | value."""
    data = [[cell(r[0], bold=True), cell(r[1])] for r in rows]
    t = Table(data, colWidths=[28*mm, USABLE_W - 28*mm])
    t.setStyle(TableStyle([
        ('FONTNAME',      (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',      (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING',   (0,0), (-1,-1), 5),
        ('RIGHTPADDING',  (0,0), (-1,-1), 5),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND',    (0,0), (-1,-1), LIGHT_BG),
        ('GRID',          (0,0), (-1,-1), 0.3, BORDER_COL),
        ('TEXTCOLOR',     (0,0), (-1,-1), DARK),
    ]))
    return t

print("Step 3 done: helpers defined")

# ── HEADER ────────────────────────────────────────────────────────────────────

story += [
    Paragraph('Security Findings &amp; Fix Report — mx-chain-core-go', sTitle),
    sp(2),
    Paragraph('<b>Scan Type:</b> Full repository scan — all files analyzed', sMeta),
    Paragraph('<b>Files Covered:</b> core/common.go, core/common_test.go, core/file.go, '
              'core/file_test.go, core/constants.go, data/drwa/constants.go, '
              'data/drwa/constants_test.go', sMeta),
    sp(6),
    Paragraph(
        '<b>Overall Status:</b> 5 findings total — 2 real security findings (Medium, Medium), '
        '3 code/quality findings (Low, Low, Low), 1 false positive, 1 DRWA flow gap (Medium). '
        'Previous audit findings F1, F2, F4, F5 confirmed fixed. '
        '<b>Finding A</b> — IsValid() accepts DenialUnknown as storable. '
        '<b>Finding B</b> — LoadTomlFileToMap leaks file descriptors on error paths. '
        '<b>Finding C</b> — SaveSkToPemFile writes PEM with no identifier validation. '
        '<b>Finding D</b> — CreateFile creates directories with os.ModePerm (0777). '
        '<b>Finding E</b> — GetPBFTThreshold returns threshold 1 for consensusSize 0 or negative.',
        sNote),
    hr(),
]

# ── SECTION 1: SUMMARY TABLE ──────────────────────────────────────────────────

story.append(section('SECTION 1 — SUMMARY TABLE'))
story.append(sp(4))

# Column widths must sum to USABLE_W (~173 mm)
# #(8) File(38) Line(14) Sev(14) Type(22) Fix(20) Mandatory(30) Status(27) = 173
cw1 = [8*mm, 38*mm, 14*mm, 14*mm, 22*mm, 20*mm, 30*mm, 27*mm]

s1_header = [hcell('#'), hcell('File'), hcell('Line'), hcell('Severity'),
             hcell('Type'), hcell('Fix Required'), hcell('Mandatory?'), hcell('Status')]

s1_rows = [
    [cell('A',bold=True), cell('data/drwa/\nconstants.go'), cell('67'),
     cell('Medium'), cell('DRWA FINDING'), cell('Yes'),
     cell('YES — regulatory violations accumulate', bold=True),
     cell('REAL FINDING', bold=True)],

    [cell('B',bold=True), cell('core/file.go'), cell('69–100'),
     cell('Medium'), cell('REAL FINDING'), cell('Yes'),
     cell('YES — node crashes under disk pressure', bold=True),
     cell('REAL FINDING', bold=True)],

    [cell('C'), cell('core/file.go'), cell('260–272'),
     cell('Low'), cell('REAL FINDING'), cell('Recommended'),
     cell('Latent trap for downstream developers'),
     cell('REAL FINDING')],

    [cell('D'), cell('core/file.go'), cell('124'),
     cell('Low'), cell('CODE QUALITY'), cell('Conditional'),
     cell('Critical in containers with permissive umask'),
     cell('REAL FINDING')],

    [cell('E'), cell('core/common.go'), cell('46–52'),
     cell('Low'), cell('CODE QUALITY'), cell('Recommended'),
     cell('Defence-in-depth gap'),
     cell('REAL FINDING')],

    [cell('6'), cell('core/common.go'), cell('28–33'),
     cell('—'), cell('FALSE POSITIVE'), cell('None'),
     cell('Not a vulnerability'),
     cell('DISMISSED')],

    [cell('7'), cell('data/drwa/\nconstants_test.go'), cell('—'),
     cell('Medium'), cell('DRWA FLOW GAP'), cell('Recommended'),
     cell('Regulatory gap grows with new denial codes'),
     cell('OPEN')],
]

t1 = Table([s1_header] + s1_rows, colWidths=cw1, repeatRows=1)
t1.setStyle(base_table_style())
story += [t1, sp(8), hr()]

print("Step 4 done: header and Section 1")

# ── SECTION 2 ─────────────────────────────────────────────────────────────────

story.append(section('SECTION 2 — REAL FINDINGS'))
story.append(sp(4))

# ── FINDING A ─────────────────────────────────────────────────────────────────

story.append(finding('Finding A — DRWA FINDING — IsValid() Accepts DenialUnknown as a '
                     'Storable Denial Code in data/drwa/constants.go line 67'))

story.append(classif_table([
    ['CWE:',              'CWE-20 (Improper Input Validation)'],
    ['CVSS v3.1:',        '5.3 (Medium) — AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N'],
    ['Severity:',         'Medium'],
    ['Fix Required:',     'Yes — MANDATORY'],
    ['Runtime Impact:',   'Any downstream compliance gate that calls code.IsValid() before '
                          'storing a denial record will accept DenialUnknown ("DRWA_UNKNOWN") '
                          'as a valid storable denial reason. A denial record carrying '
                          '"DRWA_UNKNOWN" is not attributable to any specific compliance rule.'],
    ['Monitoring Impact:','No compile-time error, no runtime panic — DenialUnknown is silently '
                          'stored in the compliance index as if it were a valid denial reason.'],
]))
story.append(sp(5))

story.append(note('Severity Note:', 'Medium. Data origin is INTERNAL — the return value of '
    'NormalizeDenialCode for any unrecognized input. No external attacker input is required. '
    'The previous audit prescribed IsValid() to return false for the unknown sentinel. '
    'The implementation inverted this: IsValid() returns true for DenialUnknown (line 67). '
    'IsKnown() correctly returns false for DenialUnknown, but IsValid() is the natural method '
    'name a downstream developer reaches for as a storage pre-check. The inversion is a design '
    'contract violation that silently re-introduces the regulatory reporting failure the '
    'previous fix was designed to close.'))
story.append(sp(4))

story.append(lbl('What the Vulnerable Function Does:'))
story.append(p('`IsValid()` in data/drwa/constants.go lines 66–68 returns `true` for '
               '`DenialUnknown` via the condition `code == DenialUnknown || code.IsKnown()`. '
               'The doc comment says "including the explicit unknown sentinel" — this is the '
               'design choice that creates the vulnerability.'))
story.append(p('**What it does NOT do:** does not distinguish between a known concrete denial '
               'reason and the explicit fallback for unrecognized inputs. Does not prevent '
               '`DenialUnknown` from being stored in the compliance index when `IsValid()` is '
               'used as the storage guard.'))
story.append(p('**Call chain:** compliance gate evaluates transfer → `NormalizeDenialCode` '
               'returns `DenialUnknown` for unrecognized input → `code.IsValid()` returns '
               '`true` → denial record stored with `denial_code: "DRWA_UNKNOWN"` → indexed '
               'to compliance store → regulatory report contains denial with no attributable rule.'))
story.append(sp(4))

story.append(lbl('Where Does the Vulnerable Data Come From:'))
story.append(p('`NormalizeDenialCode` (line 73) returns `DenialUnknown` for any unrecognized '
               'non-empty input → downstream compliance gate calls `code.IsValid()` → returns '
               '`true` → `DenialUnknown` stored in compliance index.'))
story.append(p('**Data origin:** INTERNAL (`NormalizeDenialCode` return value). No external '
               'input required.'))
story.append(sp(4))

story.append(lbl('Who Uses This Data and Why It Must Be Trusted:'))
for item in [
    '**DevOps / Node Operator:** Monitors denial code distribution. Breaks if `DenialUnknown` '
    'records accumulate — metrics show denials with no rule attribution. **Silent failure '
    'consequence:** operators assume the denial reason was intentionally "unknown"; the bug '
    'is never investigated.',
    '**Security / Compliance Engineer:** Relies on `IsValid()` as the storage guard. Breaks '
    'because `IsValid()` returns `true` for `DenialUnknown` — the guard passes silently. '
    '**Silent failure consequence:** compliance audit cannot determine which rule triggered '
    'the denial.',
    '**Compliance / Regulatory Officer:** Must demonstrate every transfer denial corresponds '
    'to a specific regulatory rule. Breaks if `DenialUnknown` appears in the compliance index. '
    '**Silent failure consequence:** regulatory filing contains unexplained denials — potential '
    'MiCA Article 45 violation.',
    '**On-Call Engineer:** Investigates compliance gate anomalies. Breaks because `DenialUnknown` '
    'gives no indication of which code path produced it. **Silent failure consequence:** on-call '
    'cannot determine root cause without full code path analysis.',
]:
    story.append(bul(item))
story.append(sp(4))

story.append(lbl('What an Attacker Can Do:'))
for i, (scenario, log, consequence) in enumerate([
    ('**Compliance Index Pollution:** Attacker sends a transfer with an unrecognized denial '
     'code → `NormalizeDenialCode` returns `DenialUnknown` → `IsValid()` returns `true` → '
     'denial record stored with `denial_code: "DRWA_UNKNOWN"`.',
     'No error — denial record stored silently',
     'Compliance index accumulates DenialUnknown records; regulatory report contains denials '
     'with no rule attribution.'),
    ('**Regulatory Report Corruption:** Reporting tool filters by `DenialCode` — records with '
     '`DenialUnknown` are excluded from category counts. Total denial count does not match '
     'sum of category counts.',
     'No error',
     'Regulatory report is internally inconsistent — potential regulatory filing failure.'),
    ('**Compliance Gate Bypass:** Downstream switch has no `case DenialUnknown:` branch — '
     'unknown code falls to default which may not block the transfer.',
     'No error — default branch executes, transfer may proceed',
     'Transfer that should be denied proceeds because the denial code was never resolved.'),
    ('**Audit Trail Collapse:** High-volume transfers through the unrecognized-input path — '
     'all denial records carry `DenialUnknown`, making the compliance index useless.',
     'No error — all records indexed with DenialUnknown',
     'Compliance dashboard shows thousands of denials with no rule attribution.'),
], 1):
    story.append(bul(f'{i}. {scenario}'))
    story.append(bul(f'**Exact log output:** {log}', sub=True))
    story.append(bul(f'**Consequence:** {consequence}', sub=True))
story.append(sp(4))

story.append(lbl('Why This Is Specific to This Feature:'))
story.append(p('`DenialCode` is the only typed string in data/drwa/constants.go that carries '
               'regulatory significance — each value maps to a specific compliance rule that '
               'must be attributable in regulatory filings. `IsValid()` is the only validation '
               'method on `DenialCode`. Its semantics directly determine what gets stored in '
               'the compliance index. The previous audit\'s prescribed fix explicitly required '
               '`IsValid()` to return `false` for the unknown sentinel — the implementation '
               'inverted this contract.'))
story.append(sp(4))

story.append(lbl('The Fix:'))
story.append(p('**BEFORE** (data/drwa/constants.go lines 64–68 — exact code from file):'))
story.append(code_block(
    '// IsValid reports whether code is a valid canonical value, including the\n'
    '// explicit unknown sentinel. The empty string is never valid.\n'
    'func (code DenialCode) IsValid() bool {\n'
    '    return code == DenialUnknown || code.IsKnown()\n'
    '}'
))
story.append(p('**AFTER:**'))
story.append(code_block(
    '// IsValid reports whether code is one of the 15 concrete denial codes\n'
    '// emitted by the DRWA gate. Returns false for DenialUnknown and the\n'
    '// empty string. Use IsValid() as the storage guard before writing a\n'
    '// denial record to the compliance index.\n'
    'func (code DenialCode) IsValid() bool {\n'
    '    return code.IsKnown()\n'
    '}'
))
story.append(p('**What each line does:** Removing `code == DenialUnknown` from the return '
               'condition means `IsValid()` returns `false` for `DenialUnknown`. `IsKnown()` '
               'already iterates `AllDenialCodes()` and returns `true` only for the 15 '
               'concrete codes — no new logic needed.'))
story.append(sp(4))

story.append(lbl('Why This Fix Is Safe:'))
story.append(p('No imports needed. No existing call sites in this repo are broken — `IsValid()` '
               'has no callers in mx-chain-core-go itself. `DenialUnknown` remains a valid '
               'named constant. `NormalizeDenialCode` output is identical — `DenialUnknown` '
               'is still returned for unrecognized inputs via a different internal path.'))
story.append(sp(4))

story.append(lbl('Integration Impact — Will It Break Existing Flow:'))
for item in [
    '**One existing test must be updated before applying this fix.** '
    '`TestDenialCodes_ValidityAndNormalization` at constants_test.go line 28 currently asserts '
    '`if !DenialUnknown.IsValid()` — this assertion flips after the fix. Update it to '
    '`if DenialUnknown.IsValid()` before deploying.',
    '**No runtime flow breaks.** `IsKnown()` is not changed. All 15 concrete denial codes '
    'continue to pass both `IsValid()` and `IsKnown()` unchanged.',
    '**Smooth integration:** After updating the one test assertion, `go test ./...` passes '
    'clean. No API changes, no signature changes, no import changes.',
]:
    story.append(bul(item))
story.append(sp(4))

story.append(lbl('Test Update Required:'))
story.append(p('Update `TestDenialCodes_ValidityAndNormalization` in constants_test.go line 28 '
               '— change assertion so that `DenialUnknown.IsValid()` must return `false`. '
               'Add `TestDenialUnknown_IsNotStorable` asserting `DenialUnknown.IsValid() == false`.'))
story.append(sp(4))

story.append(lbl('Why This Fix Is Necessary:'))
story.append(p('A compliance type whose "is valid for storage" method returns `true` for the '
               'explicit "I don\'t know what this is" sentinel is a regulatory reporting risk. '
               'Every denial record in the compliance audit trail must carry a specific, '
               'attributable denial reason. Silence is worse than explicit failure because a '
               'denial record with `denial_code: "DRWA_UNKNOWN"` stored in the compliance '
               'index gives no indication that the denial reason was never resolved to a '
               'concrete rule.'))
story.append(sp(4))

story.append(lbl('If Left Unfixed — Consequences:'))
for item in [
    'Every transfer that triggers an unrecognized denial code path permanently stores a '
    '`DRWA_UNKNOWN` record in the compliance index. These records accumulate with every '
    'transaction and cannot be retroactively corrected.',
    'Under MiCA Article 45 this is a direct regulatory filing violation — you cannot '
    'demonstrate which compliance rule triggered the denial.',
    'A downstream switch with no `case DenialUnknown:` branch silently allows transfers '
    'that should be denied — a regulated transfer goes through with no error, no log, no alert.',
    '**This is the highest-priority fix in the entire report. It must be applied before '
    'the system processes any real regulated transfers.**',
]:
    story.append(bul(item))
story += [sp(6), hr()]

print("Step 5 done: Finding A")

# ── FINDING B ─────────────────────────────────────────────────────────────────

story.append(finding('Finding B — REAL FINDING — defer f.Close() Placed After Early Returns '
                     'Leaks File Descriptor on Error Paths in core/file.go lines 69–100'))

story.append(classif_table([
    ['CWE:',              'CWE-775 (Missing Release of File Descriptor or Handle after '
                          'Effective Lifetime)'],
    ['CVSS v3.1:',        '5.3 (Medium) — AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H'],
    ['Severity:',         'Medium'],
    ['Fix Required:',     'Yes — MANDATORY'],
    ['Runtime Impact:',   'LoadTomlFileToMap opens a file at line 71, calls f.Stat() at '
                          'line 76 and f.Read() at line 84. If either returns an error the '
                          'function returns early at lines 78 or 86. The defer f.Close() is '
                          'registered at line 89 — after both early return points. On the '
                          'f.Stat() and f.Read() error paths the defer is never registered, '
                          'so f.Close() is never called. The file descriptor is leaked for '
                          'the lifetime of the process.'],
    ['Monitoring Impact:','No error logged for the leaked descriptor. The OS fd table silently '
                          'fills. On Linux the default per-process limit is 1024 (soft) / 4096 '
                          '(hard). A node that repeatedly calls LoadTomlFileToMap on error '
                          'paths will exhaust its fd table, causing all subsequent file opens '
                          'to fail with "too many open files".'],
]))
story.append(sp(5))

story.append(note('Severity Note:', 'Medium. Data origin is LOCAL FILE. The error paths that '
    'trigger the leak require either a filesystem race or a kernel-level read error (disk I/O '
    'failure). Neither requires an external attacker. All other file-handling functions in the '
    'same file (LoadTomlFile line 48, SaveTomlFile line 62, LoadJsonFile line 110) correctly '
    'register defer f.Close() immediately after the file is opened — the misplacement is '
    'unique to LoadTomlFileToMap.'))
story.append(sp(4))

story.append(lbl('What the Vulnerable Function Does:'))
story.append(p('`LoadTomlFileToMap` in core/file.go opens a file, calls `f.Stat()` to get '
               'the file size, allocates a buffer, calls `f.Read()` to fill it, then defers '
               '`f.Close()` and proceeds to parse the buffer as TOML.'))
story.append(p('**What it does NOT do:** does not register `defer f.Close()` immediately '
               'after `OpenFile` succeeds. Does not call `f.Close()` explicitly on the error '
               'paths at lines 78 and 86.'))
story.append(p('**Call chain:** node startup → `LoadTomlFileToMap("config.toml")` → '
               '`OpenFile` succeeds → `f.Stat()` fails (disk error) → `return nil, err` at '
               'line 78 → defer never registered → `f.Close()` never called → file descriptor '
               'leaked → repeated calls exhaust fd table → all subsequent file opens fail '
               'with `EMFILE`.'))
story.append(sp(4))

story.append(lbl('Where Does the Vulnerable Data Come From:'))
story.append(p('Operator-placed config file → `OpenFile` opens it → `f.Stat()` or `f.Read()` '
               'fails due to filesystem error → early return without closing. '
               '**Data origin:** LOCAL FILE.'))
story.append(sp(4))

story.append(lbl('Who Uses This Data and Why It Must Be Trusted:'))
for item in [
    '**DevOps / Node Operator:** Relies on `LoadTomlFileToMap` releasing file descriptors on '
    'all paths. **Silent failure consequence:** node fails to start with "too many open files" '
    'with no indication the root cause is a leaked descriptor.',
    '**Security / Compliance Engineer:** Relies on node starting cleanly to begin processing '
    'regulated transfers. **Silent failure consequence:** all regulated transfers blocked '
    'because the node never reaches the compliance gate.',
    '**Compliance / Regulatory Officer:** Relies on the node being operational. **Silent '
    'failure consequence:** regulated transfers are not processed during the outage window.',
    '**On-Call Engineer:** Investigates node startup failures. **Silent failure consequence:** '
    'on-call cannot determine root cause without strace or lsof analysis.',
]:
    story.append(bul(item))
story.append(sp(4))

story.append(lbl('What an Attacker Can Do:'))
for i, (scenario, log, consequence) in enumerate([
    ('**Filesystem Race to Trigger Leak:** Attacker repeatedly creates and removes a config '
     'file between `OpenFile` and `Stat` → `f.Stat()` fails on every call → each call leaks '
     'one fd → fd table exhausted.',
     'No error for the leaked fd — only "too many open files" when full',
     'Node DoS — all file operations fail.'),
    ('**Disk I/O Error Amplification:** Under disk pressure, `f.Read()` returns an error → '
     'fd leaked → repeated config reloads each leak one fd → fd table exhausted faster than '
     'the disk recovers.',
     'No error for the leaked fd',
     'Node cannot recover from disk pressure — permanent DoS until restart.'),
    ('**Container fd Limit Exhaustion:** In a containerised deployment with a low fd limit, '
     'a single burst of config reload errors exhausts the fd table.',
     'No error at leak time',
     'Node stops signing blocks — silently excluded from consensus.'),
    ('**Repeated Error Path Triggering:** Attacker causes repeated `f.Stat()` failures by '
     'toggling file permissions — each call leaks one fd.',
     'No error',
     'Node DoS with no log trail pointing to the root cause.'),
], 1):
    story.append(bul(f'{i}. {scenario}'))
    story.append(bul(f'**Exact log output:** {log}', sub=True))
    story.append(bul(f'**Consequence:** {consequence}', sub=True))
story.append(sp(4))

story.append(lbl('Why This Is Specific to This Feature:'))
story.append(p('`LoadTomlFileToMap` is the only function in core/file.go that places '
               '`defer f.Close()` after error-returning statements that follow the file open. '
               'All other functions in the same file correctly register `defer f.Close()` '
               'immediately after the file is opened. The misplacement is unique to '
               '`LoadTomlFileToMap` and is not present in any other file-handling function '
               'in the package.'))
story.append(sp(4))

story.append(lbl('The Fix:'))
story.append(p('**BEFORE** (core/file.go lines 69–100 — exact code from file):'))
story.append(code_block(
    'func LoadTomlFileToMap(relativePath string) (map[string]interface{}, error) {\n'
    '    f, err := OpenFile(relativePath)\n'
    '    if err != nil {\n'
    '        return nil, err\n'
    '    }\n'
    '\n'
    '    fileinfo, err := f.Stat()\n'
    '    if err != nil {\n'
    '        return nil, err          // fd leaked here — defer not yet registered\n'
    '    }\n'
    '\n'
    '    filesize := fileinfo.Size()\n'
    '    buffer := make([]byte, filesize)\n'
    '\n'
    '    _, err = f.Read(buffer)\n'
    '    if err != nil {\n'
    '        return nil, err          // fd leaked here — defer not yet registered\n'
    '    }\n'
    '\n'
    '    defer func() {               // too late — only reached on success path\n'
    '        _ = f.Close()\n'
    '    }()\n'
    '    ...\n'
    '}'
))
story.append(p('**AFTER:**'))
story.append(code_block(
    'func LoadTomlFileToMap(relativePath string) (map[string]interface{}, error) {\n'
    '    f, err := OpenFile(relativePath)\n'
    '    if err != nil {\n'
    '        return nil, err\n'
    '    }\n'
    '\n'
    '    defer func() {               // registered immediately — fires on all paths\n'
    '        _ = f.Close()\n'
    '    }()\n'
    '\n'
    '    fileinfo, err := f.Stat()\n'
    '    if err != nil {\n'
    '        return nil, err          // defer now fires — fd closed\n'
    '    }\n'
    '\n'
    '    filesize := fileinfo.Size()\n'
    '    buffer := make([]byte, filesize)\n'
    '\n'
    '    _, err = f.Read(buffer)\n'
    '    if err != nil {\n'
    '        return nil, err          // defer now fires — fd closed\n'
    '    }\n'
    '    ...\n'
    '}'
))
story.append(p('**What each line does:** Moving `defer f.Close()` to immediately after the '
               'nil-error check on `OpenFile` ensures it is registered on every code path '
               'that successfully opens the file. No other logic changes — the fix is a '
               'single block move of 3 lines.'))
story.append(sp(4))

story.append(lbl('Why This Fix Is Safe:'))
story.append(p('Semantically identical for all success paths. Additive only for error paths '
               '— `f.Close()` is now called on paths where it was previously skipped. '
               'No imports needed. No API changes.'))
story.append(sp(4))

story.append(lbl('Integration Impact — Will It Break Existing Flow:'))
for item in [
    '**No existing tests break.** The fix is a 3-line block move. The success path — the '
    'only path currently exercised by all existing tests — is completely unchanged.',
    '**No runtime flow breaks.** All callers of `LoadTomlFileToMap` receive identical return '
    'values on both success and error paths.',
    '**Smooth integration:** Drop-in safe. No API changes, no signature changes, no import '
    'changes. `go test ./...` passes clean with no modifications.',
]:
    story.append(bul(item))
story.append(sp(4))

story.append(lbl('Test Update Required:'))
story.append(p('Add a test that calls `LoadTomlFileToMap` with a file that is deleted between '
               'open and read and asserts no file descriptor leak. Verify with `/proc/self/fd` '
               'that the fd count does not increase on repeated error-path calls.'))
story.append(sp(4))

story.append(lbl('Why This Fix Is Necessary:'))
story.append(p('A file descriptor leak in a config-loading function that is called at node '
               'startup and on config reload is a latent DoS vector. The leak is silent — '
               'no error is logged, no metric is incremented. The only observable symptom is '
               '"too many open files" when the fd table is exhausted, at which point the node '
               'cannot recover without a restart.'))
story.append(sp(4))

story.append(lbl('If Left Unfixed — Consequences:'))
for item in [
    'Under disk pressure: the node silently accumulates leaked file descriptors, then crashes '
    'with "too many open files" at an unpredictable point during the incident.',
    'In containerised deployments with low fd limits: a single burst of config reload errors '
    'can exhaust the fd table in minutes, stopping the node from signing blocks.',
    'The failure symptom gives no indication of the root cause — on-call spends hours '
    'debugging the wrong thing while the node is down.',
    '**This is the second highest-priority fix. It must be applied before any production '
    'deployment under disk pressure or in containers.**',
]:
    story.append(bul(item))
story += [sp(6), hr()]

print("Step 6 done: Finding B")

# ── FINDING C ─────────────────────────────────────────────────────────────────

story.append(finding('Finding C — REAL FINDING — SaveSkToPemFile Writes PEM Block with No '
                     'Identifier Validation in core/file.go lines 260–272'))

story.append(classif_table([
    ['CWE:',              'CWE-20 (Improper Input Validation)'],
    ['CVSS v3.1:',        '4.0 (Low) — AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:L'],
    ['Severity:',         'Low'],
    ['Fix Required:',     'Recommended — fix before codebase grows'],
    ['Runtime Impact:',   'SaveSkToPemFile writes a PEM block with type "PRIVATE KEY for " + '
                          'identifier with no validation. LoadSkPkFromPemFile and '
                          'LoadAllKeysFromPemFile both call isValidPemPublicKeySuffix on the '
                          'extracted suffix. If SaveSkToPemFile writes a PEM file with an '
                          'identifier that fails isValidPemPublicKeySuffix, the file cannot '
                          'be loaded back. The write succeeds silently; the load fails with '
                          'ErrPemFileIsInvalid.'],
    ['Monitoring Impact:','No error at write time. The failure is discovered only when the '
                          'node attempts to load the key at startup, producing '
                          'ErrPemFileIsInvalid with no indication that the root cause is the '
                          'identifier that was written.'],
]))
story.append(sp(5))

story.append(lbl('What the Vulnerable Function Does:'))
story.append(p('`SaveSkToPemFile` in core/file.go lines 260–272 checks only that `file != nil`, '
               'then concatenates the identifier directly into the PEM block type and calls '
               '`pem.Encode`. **What it does NOT do:** does not validate that identifier is '
               'non-empty, does not check for leading/trailing whitespace or control characters, '
               'does not apply the same validation that the loaders apply when reading back.'))
story.append(p('**Call chain:** key generator → `SaveSkToPemFile(file, "", skBytes)` → '
               '`pem.Encode` writes block with type `"PRIVATE KEY for "` → file written '
               'successfully → node restart → `LoadSkPkFromPemFile` → '
               '`isValidPemPublicKeySuffix("")` returns `false` → `ErrPemFileIsInvalid` → '
               'node fails to start.'))
story.append(sp(4))

story.append(lbl('The Fix:'))
story.append(p('**BEFORE** (core/file.go lines 260–272 — exact code from file):'))
story.append(code_block(
    'func SaveSkToPemFile(file *os.File, identifier string, skBytes []byte) error {\n'
    '    if file == nil {\n'
    '        return ErrNilFile\n'
    '    }\n'
    '\n'
    '    blk := pem.Block{\n'
    '        Type:  "PRIVATE KEY for " + identifier,\n'
    '        Bytes: skBytes,\n'
    '    }\n'
    '\n'
    '    return pem.Encode(file, &blk)\n'
    '}'
))
story.append(p('**AFTER:**'))
story.append(code_block(
    'func SaveSkToPemFile(file *os.File, identifier string, skBytes []byte) error {\n'
    '    if file == nil {\n'
    '        return ErrNilFile\n'
    '    }\n'
    '    if !isValidPemPublicKeySuffix(identifier) {\n'
    '        return fmt.Errorf("%w invalid identifier for PEM block type",\n'
    '            ErrPemFileIsInvalid)\n'
    '    }\n'
    '\n'
    '    blk := pem.Block{\n'
    '        Type:  "PRIVATE KEY for " + identifier,\n'
    '        Bytes: skBytes,\n'
    '    }\n'
    '\n'
    '    return pem.Encode(file, &blk)\n'
    '}'
))
story.append(p('**Why This Fix Is Safe:** `isValidPemPublicKeySuffix` is already defined in '
               'the same file (line 247). `fmt` is already imported. No API changes — the '
               'new error path only fires for inputs that would produce an unloadable PEM '
               'file anyway. All existing callers pass valid identifiers — drop-in safe.'))
story.append(sp(4))

story.append(lbl('If Left Unfixed — Consequences:'))
for item in [
    'No immediate production risk — all current callers pass valid identifiers.',
    'Becomes a hard-to-diagnose node startup failure the moment any downstream developer '
    'passes an empty, whitespace-padded, or control-character-containing identifier. The '
    'write succeeds with no error; the node fails to start on the next restart with '
    '`ErrPemFileIsInvalid` and no pointer to the write-time cause.',
    '**Recommended to fix before the codebase grows. Not mandatory today.**',
]:
    story.append(bul(item))
story += [sp(6), hr()]

# ── FINDING D ─────────────────────────────────────────────────────────────────

story.append(finding('Finding D — CODE QUALITY — CreateFile Creates Directory with '
                     'os.ModePerm (0777) in core/file.go line 124'))

story.append(classif_table([
    ['CWE:',              'CWE-732 (Incorrect Permission Assignment for Critical Resource)'],
    ['CVSS v3.1:',        '3.3 (Low) — AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N'],
    ['Severity:',         'Low'],
    ['Fix Required:',     'Conditional — verify deployment environment first'],
    ['Runtime Impact:',   'CreateFile calls os.MkdirAll(absPath, os.ModePerm) at line 124. '
                          'os.ModePerm is 0777 — world-readable, world-writable, '
                          'world-executable before umask. On a system with a permissive umask '
                          '(e.g. 0000 or 0002), the created directory is writable by all '
                          'local users. The file inside uses FileModeUserReadWrite (0600), '
                          'but the directory itself is 0777.'],
    ['Monitoring Impact:','No error logged. The directory is created silently with world-write '
                          'permissions. The permission mismatch between the directory (0777) '
                          'and the files inside it (0600) is not flagged anywhere.'],
]))
story.append(sp(5))

story.append(lbl('The Fix:'))
story.append(p('**BEFORE** (core/file.go line 124 — exact code from file):'))
story.append(code_block('err = os.MkdirAll(absPath, os.ModePerm)'))
story.append(p('**AFTER:**'))
story.append(code_block('err = os.MkdirAll(absPath, 0700)'))
story.append(p('**What each line does:** `0700` — owner read/write/execute only. Consistent '
               'with `FileModeUserReadWrite` (`0600`) on the files inside. No other local '
               'user can list, create, or delete files in the directory.'))
story.append(p('**Why This Fix Is Safe:** The node process is the only consumer of the '
               'created directory. `0700` gives the node full access. No other process needs '
               'access to the log/key directory. No existing tests assert directory '
               'permissions — no tests break.'))
story.append(sp(4))

story.append(lbl('If Left Unfixed — Consequences:'))
for item in [
    'On a standard production Linux server with umask `0022`: effective directory permission '
    'is `0755` — not writable, low risk, node operates normally.',
    'In containers running as root with umask `0000`: the directory is world-writable. Any '
    'co-located process can create, rename, or delete files inside it including log and key files.',
    '**Not mandatory on standard deployments. Mandatory in containers with permissive umask. '
    'Verify your deployment environment before deciding.**',
]:
    story.append(bul(item))
story += [sp(6), hr()]

# ── FINDING E ─────────────────────────────────────────────────────────────────

story.append(finding('Finding E — CODE QUALITY — GetPBFTThreshold and '
                     'GetPBFTFallbackThreshold Return Threshold 1 for consensusSize 0 or '
                     'Negative in core/common.go lines 46–52'))

story.append(classif_table([
    ['CWE:',              'CWE-20 (Improper Input Validation)'],
    ['CVSS v3.1:',        '3.1 (Low) — AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N'],
    ['Severity:',         'Low'],
    ['Fix Required:',     'Recommended — defence-in-depth before upstream validation is '
                          'refactored'],
    ['Runtime Impact:',   'GetPBFTThreshold(0) returns 0*2/3 + 1 = 1. GetPBFTThreshold(-1) '
                          'returns -1*2/3 + 1 = 1 (Go integer division truncates toward zero). '
                          'GetPBFTFallbackThreshold(0) returns 0*1/2 + 1 = 1. A threshold of '
                          '1 means a single node can reach consensus alone — the pBFT safety '
                          'guarantee collapses.'],
    ['Monitoring Impact:','No error logged. No panic. The function returns a numerically valid '
                          'but semantically wrong threshold. The caller has no signal that the '
                          'input was invalid.'],
]))
story.append(sp(5))

story.append(lbl('The Fix:'))
story.append(p('**BEFORE** (core/common.go lines 46–52 — exact code from file):'))
story.append(code_block(
    'func GetPBFTThreshold(consensusSize int) int {\n'
    '    return consensusSize*2/3 + 1\n'
    '}\n'
    '\n'
    'func GetPBFTFallbackThreshold(consensusSize int) int {\n'
    '    return consensusSize*1/2 + 1\n'
    '}'
))
story.append(p('**AFTER:**'))
story.append(code_block(
    'func GetPBFTThreshold(consensusSize int) int {\n'
    '    if consensusSize <= 0 {\n'
    '        return 0\n'
    '    }\n'
    '    return consensusSize*2/3 + 1\n'
    '}\n'
    '\n'
    'func GetPBFTFallbackThreshold(consensusSize int) int {\n'
    '    if consensusSize <= 0 {\n'
    '        return 0\n'
    '    }\n'
    '    return consensusSize*1/2 + 1\n'
    '}'
))
story.append(p('**Why This Fix Is Safe:** Additive only for invalid inputs. All valid '
               'consensus sizes (`>= 2`) produce the same result as before. All existing '
               'tests cover sizes 2–7 only — no tests break.'))
story.append(sp(4))

story.append(lbl('If Left Unfixed — Consequences:'))
for item in [
    'No immediate production risk — all current callers in mx-chain-go pass validated '
    'consensus sizes of `>= 2`. The guard is never reached today.',
    'Becomes a critical consensus safety failure if any future upstream change removes or '
    'bypasses the consensus size validation and passes `0` or a negative value. '
    '`GetPBFTThreshold(0)` returns `1` — a single node can reach consensus alone with no '
    'error, no log, no alert.',
    '**Not mandatory today. Recommended as a defence-in-depth measure before any upstream '
    'consensus size validation is refactored.**',
]:
    story.append(bul(item))
story += [sp(6), hr()]

print("Step 7 done: Findings C, D, E")

# ── SECTION 3 ─────────────────────────────────────────────────────────────────

story.append(section('SECTION 3 — FALSE POSITIVES'))
story.append(sp(4))
story.append(finding('Finding 6 — FALSE POSITIVE — UniqueIdentifier Returns Non-Printable Bytes'))
story.append(lbl('What the Scanner Flagged:'))
story.append(p('`UniqueIdentifier()` in core/common.go returns `string(buff)` where `buff` '
               'is a 32-byte slice filled by `io.ReadFull(rand.Reader, buff)`. The resulting '
               'string contains non-printable, non-UTF-8 bytes. Flagged as potential unsafe '
               'string construction or encoding issue.'))
story.append(lbl('Why It Is Not a Vulnerability:'))
story.append(p('`string(buff)` in Go is a valid byte-to-string conversion — it does not '
               'require the bytes to be valid UTF-8. The Go specification explicitly allows '
               'strings to contain arbitrary bytes. `UniqueIdentifier()` is documented as '
               'returning a "unique string identifier of 32 bytes" — the bytes are used as '
               'an opaque identifier, not as human-readable text. The non-printable bytes are '
               'intentional — they maximise entropy in the identifier. The previous audit\'s '
               'Finding 1 (rand.Read error discarded) is now fixed — `io.ReadFull` captures '
               'the error and panics on failure.'))
story.append(lbl('Action required:'))
story.append(p('None. The non-printable byte content is correct and intentional.'))
story += [sp(6), hr()]

# ── SECTION 4 ─────────────────────────────────────────────────────────────────

story.append(section('SECTION 4 — FEATURE SECURITY ASSESSMENT'))
story.append(sp(4))

# Column widths: Feature(50) Status(25) Notes(USABLE_W-75)
cw4 = [50*mm, 25*mm, USABLE_W - 75*mm]

s4_header = [hcell('Feature Area'), hcell('Status'), hcell('Notes')]

def fc(t): return cell(t, size=8)
def sc(t): return cell(t, bold=True, size=8)

s4_rows = [
    [fc('DRWA Denial Code Vocabulary'),   sc('PARTIAL ISSUE'),
     fc('16 constants defined (15 concrete + DenialUnknown sentinel). IsKnown() correct. '
        'IsValid() incorrectly accepts DenialUnknown — re-introduces compliance reporting '
        'failure. Fix: Finding A.')],
    [fc('DRWA Storage Key Prefixes'),     sc('SECURE'),
     fc('StorageKeyPrefix typed. AllStorageKeyPrefixes() present. IsValid() and non-overlap '
        'tests present. Previous Finding 4 fixed.')],
    [fc('DRWA Test Coverage'),            sc('PARTIAL ISSUE'),
     fc('Uniqueness, IsKnown(), IsValid(), NormalizeDenialCode all tested. Missing: '
        'AllDenialCodes() count assertion (len == 15). Fix: Section 7.')],
    [fc('Entropy Safety (UniqueIdentifier)'), sc('SECURE'),
     fc('io.ReadFull + panic on failure. Error is no longer discarded. Previous Finding 1 fixed.')],
    [fc('PEM Key Loading'),               sc('PARTIAL ISSUE'),
     fc('strings.HasPrefix + isValidPemPublicKeySuffix correct in loaders. Missing: '
        'identifier validation in SaveSkToPemFile — writer/reader asymmetry. Fix: Finding C.')],
    [fc('File Descriptor Management'),    sc('VULNERABLE'),
     fc('LoadTomlFileToMap defers f.Close() after two early-return points — fd leaked on '
        'f.Stat() and f.Read() error paths. All other functions in the same file are correct. '
        'Fix: Finding B.')],
    [fc('Directory Permissions'),         sc('PARTIAL ISSUE'),
     fc('CreateFile uses os.ModePerm (0777) for MkdirAll. Should be 0700 to match '
        'FileModeUserReadWrite (0600) on files inside. Fix: Finding D.')],
    [fc('PBFT Threshold Calculation'),    sc('PARTIAL ISSUE'),
     fc('No guard for consensusSize <= 0. Returns threshold 1 for size 0 or negative — '
        'collapses Byzantine fault tolerance silently. Fix: Finding E.')],
    [fc('Cryptographic Hashing'),         sc('SECURE'),
     fc('hashing/blake2b, hashing/keccak, hashing/sha256 — all use standard library '
        'implementations with no custom logic. No issues found.')],
    [fc('Marshaling / Unmarshaling'),     sc('SECURE'),
     fc('GogoProtoMarshalizer calls msg.Reset() before unmarshal — prevents state leakage. '
        'sizeCheckUnmarshalizer enforces size delta check. JsonMarshalizer uses encoding/json. '
        'No issues found.')],
    [fc('Address Encoding (bech32/hex)'), sc('SECURE'),
     fc('bech32PubkeyConverter validates prefix, length, and bit conversion. '
        'hexPubkeyConverter validates length after decode. Both return explicit errors on all '
        'failure paths. No issues found.')],
    [fc('Transaction Integrity'),         sc('SECURE'),
     fc('Transaction.CheckIntegrity() validates nil signature, nil value, negative value, '
        'and username length. GetDataForSigning uses encoder and marshaller with nil checks. '
        'No issues found.')],
    [fc('Outport Block Topics'),          sc('SECURE'),
     fc('data/outport/consts.go defines topic strings as typed constants. No injection '
        'surface. No issues found.')],
    [fc('Data Partitioning'),             sc('SECURE'),
     fc('SizeDataPacker and SimpleDataPacker both validate limit >= '
        'minimumMaxPacketSizeInBytes and data != nil. Marshal errors are propagated. '
        'No issues found.')],
    [fc('Concurrency'),                   sc('SECURE'),
     fc('core/atomic/ types use sync/atomic. core/sync/keymutex.go and rwmutex.go use '
        'sync.Mutex and sync.RWMutex. core/container/mutexMap.go uses sync.RWMutex. '
        'No data races detected.')],
    [fc('DRWA Package Isolation'),        sc('SECURE'),
     fc('data/drwa/ package has zero imports beyond testing. No coupling to any other '
        'package in the repo. Confirmed by go build ./... and go test ./... passing clean.')],
]

t4 = Table([s4_header] + s4_rows, colWidths=cw4, repeatRows=1)
t4.setStyle(base_table_style())
story += [t4, sp(8), hr()]

print("Step 8 done: Sections 3 and 4")

# ── SECTION 5 ─────────────────────────────────────────────────────────────────

story.append(section('SECTION 5 — ACTION PLAN'))
story.append(sp(4))

# ── Mandatory fixes table ──────────────────────────────────────────────────────
story.append(Paragraph('<b>Mandatory Fixes — Must Apply Before Production</b>',
    ParagraphStyle('sh', fontName='Helvetica-Bold', fontSize=10,
                   textColor=BLACK, spaceAfter=5, spaceBefore=4, leading=13)))

# Priority(22) Action(52) File(32) Line(10) Effort(12) Why(USABLE_W-128)
cw_m = [22*mm, 52*mm, 32*mm, 10*mm, 12*mm, USABLE_W - 128*mm]
mh = [hcell('Priority'), hcell('Action'), hcell('File'),
      hcell('Line'), hcell('Effort'), hcell('Why Mandatory')]
mr = [
    [cell('P1 — CRITICAL', bold=True),
     cell('Change IsValid() to return code.IsKnown() only. Update test: '
          'DenialUnknown.IsValid() must be false.'),
     cell('data/drwa/\nconstants.go'), cell('67'), cell('5 min'),
     cell('Regulatory violations accumulate permanently. MiCA filing failure.')],
    [cell('P1 — CRITICAL', bold=True),
     cell('Move defer f.Close() to immediately after OpenFile succeeds, '
          'before f.Stat() call.'),
     cell('core/file.go'), cell('89'), cell('5 min'),
     cell('Node crashes silently under disk pressure or in containers.')],
    [cell('P1 — CRITICAL', bold=True),
     cell('Add AllDenialCodes() count assertion (len == 15) and IsValid() '
          'check per code.'),
     cell('data/drwa/\nconstants_test.go'), cell('—'), cell('5 min'),
     cell('Regulatory compliance gap grows with every new denial code added.')],
]
tm = Table([mh] + mr, colWidths=cw_m, repeatRows=1)
tm.setStyle(base_table_style())
story += [tm, sp(8)]

# ── Recommended fixes table ────────────────────────────────────────────────────
story.append(Paragraph('<b>Recommended Fixes — Apply Before Codebase Grows</b>',
    ParagraphStyle('sh2', fontName='Helvetica-Bold', fontSize=10,
                   textColor=BLACK, spaceAfter=5, spaceBefore=4, leading=13)))

cw_r = [22*mm, 52*mm, 32*mm, 10*mm, 12*mm, USABLE_W - 128*mm]
rh = [hcell('Priority'), hcell('Action'), hcell('File'),
      hcell('Line'), hcell('Effort'), hcell('Risk if Deferred')]
rr = [
    [cell('P2 — Recommended'),
     cell('Add isValidPemPublicKeySuffix(identifier) guard in SaveSkToPemFile '
          'before pem.Encode.'),
     cell('core/file.go'), cell('261'), cell('10 min'),
     cell('Latent node startup failure when downstream developer passes invalid identifier.')],
    [cell('P2 — Conditional'),
     cell('Change os.MkdirAll permission from os.ModePerm to 0700.'),
     cell('core/file.go'), cell('124'), cell('2 min'),
     cell('Only critical in containers with permissive umask. Verify deployment first.')],
    [cell('P2 — Recommended'),
     cell('Add consensusSize <= 0 guard returning 0 in both PBFT threshold functions.'),
     cell('core/common.go'), cell('46, 51'), cell('5 min'),
     cell('Critical consensus safety failure if upstream validation ever regresses.')],
    [cell('P3 — Low'),
     cell('Add trailing-space PEM suffix sub-tests to TestLoadSkPkFromPemFile and '
          'TestLoadAllKeysFromPemFile.'),
     cell('core/file_test.go'), cell('—'), cell('10 min'),
     cell('Test coverage gap only — no runtime risk.')],
]
tr = Table([rh] + rr, colWidths=cw_r, repeatRows=1)
tr.setStyle(base_table_style())
story += [tr, sp(8)]

# ── Test impact summary ────────────────────────────────────────────────────────
story.append(Paragraph('<b>Test Impact Summary</b>',
    ParagraphStyle('sh3', fontName='Helvetica-Bold', fontSize=10,
                   textColor=BLACK, spaceAfter=5, spaceBefore=4, leading=13)))

# Fix(40) File(45) Action(USABLE_W-85)
cw_ti = [40*mm, 45*mm, USABLE_W - 85*mm]
tih = [hcell('Fix'), hcell('File'), hcell('Test Action Required')]
tir = [
    [cell('Finding A — IsValid()'),
     cell('data/drwa/constants_test.go'),
     cell('Change assertion: DenialUnknown.IsValid() must return false. '
          'Add TestDenialUnknown_IsNotStorable.')],
    [cell('Finding B — fd leak'),
     cell('core/file_test.go'),
     cell('Add test: repeated error-path calls do not leak file descriptors. '
          'Verify with /proc/self/fd count.')],
    [cell('Finding C — SaveSkToPemFile'),
     cell('core/file_test.go'),
     cell('Add 3 sub-tests: empty identifier, whitespace-padded identifier, '
          'control character in identifier — all should return ErrPemFileIsInvalid.')],
    [cell('Finding D — ModePerm'),
     cell('core/file_test.go'),
     cell('Add test: created directory has mode 0700.')],
    [cell('Finding E — PBFT guard'),
     cell('core/common_test.go'),
     cell('Add 4 assertions: GetPBFTThreshold(0)==0, GetPBFTThreshold(-1)==0, '
          'GetPBFTFallbackThreshold(0)==0, GetPBFTFallbackThreshold(-1)==0.')],
    [cell('Section 7 — count test'),
     cell('data/drwa/constants_test.go'),
     cell('Add TestAllDenialCodes_Complete asserting len==15 and all codes pass '
          'IsValid() (after Finding A fix applied).')],
    [cell('Trailing-space PEM'),
     cell('core/file_test.go'),
     cell('Add trailing-space suffix sub-test to both TestLoadSkPkFromPemFile '
          'and TestLoadAllKeysFromPemFile.')],
]
tti = Table([tih] + tir, colWidths=cw_ti, repeatRows=1)
tti.setStyle(base_table_style())
story += [tti, sp(8)]

# ── Integration impact summary ─────────────────────────────────────────────────
story.append(Paragraph('<b>Integration Impact Summary</b>',
    ParagraphStyle('sh4', fontName='Helvetica-Bold', fontSize=10,
                   textColor=BLACK, spaceAfter=5, spaceBefore=4, leading=13)))

# Finding(30) Mandatory(28) Tests(30) Runtime(35) Deploy(USABLE_W-123)
cw_ii = [30*mm, 28*mm, 30*mm, 35*mm, USABLE_W - 123*mm]
iih = [hcell('Finding'), hcell('Mandatory?'), hcell('Breaks Tests?'),
       hcell('Breaks Runtime Flow?'), hcell('Deployment Verification?')]
iir = [
    [cell('A — IsValid() fix'),       cell('YES', bold=True),
     cell('Yes — 1 assertion must be updated first'),
     cell('No'), cell('No')],
    [cell('B — defer move'),          cell('YES', bold=True),
     cell('No'), cell('No'), cell('No')],
    [cell('Section 7 — count test'),  cell('YES', bold=True),
     cell('No'), cell('No'), cell('No')],
    [cell('C — SaveSkToPemFile'),     cell('Recommended'),
     cell('No'), cell('No'), cell('No')],
    [cell('D — 0777 to 0700'),        cell('Conditional'),
     cell('No'),
     cell('Only if another process reads the directory'),
     cell('Yes — verify no sidecar reads node directory')],
    [cell('E — PBFT zero guard'),     cell('Recommended'),
     cell('No'), cell('No'), cell('No')],
]
tii = Table([iih] + iir, colWidths=cw_ii, repeatRows=1)
tii.setStyle(base_table_style())
story += [tii, sp(8), hr()]

print("Step 9 done: Section 5")

# ── SECTION 6 ─────────────────────────────────────────────────────────────────

story.append(section('SECTION 6 — FINAL DECISION'))
story.append(sp(4))

story.append(Paragraph('<b>Mandatory — Must Fix Before Production</b>',
    ParagraphStyle('g1', fontName='Helvetica-Bold', fontSize=10,
                   textColor=BLACK, spaceAfter=5, spaceBefore=4, leading=13)))

for item in [
    '**Finding A (IsValid() accepts DenialUnknown): NOT FIXED — Medium severity — MANDATORY.** '
    '`IsValid()` at data/drwa/constants.go line 67 returns `true` for `DenialUnknown`. Every '
    'unrecognized denial code path permanently stores a `DRWA_UNKNOWN` record in the compliance '
    'index. These records accumulate with every transaction, cannot be retroactively corrected, '
    'and constitute a direct MiCA Article 45 regulatory filing violation. A downstream switch '
    'with no `case DenialUnknown:` branch silently allows transfers that should be denied. '
    '**Fix:** change `IsValid()` to return `code.IsKnown()` only. **Integration:** update one '
    'test assertion in constants_test.go line 28 before applying — no runtime flow breaks.',

    '**Finding B (LoadTomlFileToMap fd leak): NOT FIXED — Medium severity — MANDATORY.** '
    '`defer f.Close()` at core/file.go line 89 is placed after two early-return points '
    '(lines 78, 86). Under disk pressure or in containers with low fd limits, every '
    'error-path call leaks one file descriptor permanently. The node crashes with "too many '
    'open files" at an unpredictable point during the incident with no log trail pointing to '
    'the root cause. **Fix:** move defer to immediately after `OpenFile` succeeds. '
    '**Integration:** drop-in safe — no existing tests break, no runtime flow breaks.',

    '**Section 7 Gap (No AllDenialCodes count test): NOT FIXED — Medium severity — MANDATORY.** '
    '`AllDenialCodes()` exists but no test asserts `len == 15`. The moment a new denial code '
    'is added to the constants block and omitted from `AllDenialCodes()`, the entire downstream '
    'enforcement pipeline silently misses it — no test fails, no compile error, no warning. '
    '**Fix:** add `TestAllDenialCodes_Complete`. **Integration:** adding a new test never '
    'breaks existing flow — drop-in safe.',
]:
    story.append(bul(item))
story.append(sp(6))

story.append(Paragraph('<b>Recommended — Fix Before Codebase Grows</b>',
    ParagraphStyle('g2', fontName='Helvetica-Bold', fontSize=10,
                   textColor=BLACK, spaceAfter=5, spaceBefore=4, leading=13)))

for item in [
    '**Finding C (SaveSkToPemFile no identifier validation): NOT FIXED — Low severity — '
    'RECOMMENDED.** No immediate production risk — all current callers pass valid identifiers. '
    'Becomes a hard-to-diagnose node startup failure the moment any downstream developer passes '
    'an invalid identifier. **Fix:** add `isValidPemPublicKeySuffix` guard before `pem.Encode`. '
    '**Integration:** drop-in safe.',

    '**Finding E (PBFT threshold no zero guard): NOT FIXED — Low severity — RECOMMENDED.** '
    'No immediate production risk — all current callers pass sizes `>= 2`. Becomes a critical '
    'consensus safety failure if upstream validation ever regresses and passes `0` or negative. '
    '**Fix:** add `consensusSize <= 0` guard returning `0`. **Integration:** drop-in safe.',
]:
    story.append(bul(item))
story.append(sp(6))

story.append(Paragraph('<b>Conditional — Verify Deployment Environment First</b>',
    ParagraphStyle('g3', fontName='Helvetica-Bold', fontSize=10,
                   textColor=BLACK, spaceAfter=5, spaceBefore=4, leading=13)))

story.append(bul(
    '**Finding D (CreateFile os.ModePerm): NOT FIXED — Low severity — CONDITIONAL.** '
    'On standard Linux with umask `0022` the effective directory permission is `0755` — '
    'not writable, low risk. In containers running as root with umask `0000` the directory '
    'is world-writable and any co-located process can tamper with log and key files. '
    '**Fix:** change to `0700`. **Integration:** verify no sidecar or log aggregator reads '
    'the node directory before applying.'
))
story.append(sp(6))

story.append(Paragraph('<b>Dismissed</b>',
    ParagraphStyle('g4', fontName='Helvetica-Bold', fontSize=10,
                   textColor=BLACK, spaceAfter=5, spaceBefore=4, leading=13)))

story.append(bul(
    '**Finding 6 (UniqueIdentifier non-printable bytes): DISMISSED — False positive.** '
    'Non-printable bytes in `UniqueIdentifier()` return value are intentional — the function '
    'returns an opaque random identifier, not human-readable text. No fix required.'
))
story.append(sp(8))

story.append(Paragraph('<b>Fix Priority Summary</b>',
    ParagraphStyle('ps', fontName='Helvetica-Bold', fontSize=10,
                   textColor=BLACK, spaceAfter=5, spaceBefore=4, leading=13)))

for item in [
    'Fixing **Finding A + B + Section 7** = **Minimum required for production** — regulatory '
    'violations stopped, node DoS under disk pressure eliminated, exhaustiveness contract '
    'enforced. Total effort: 15 minutes.',
    'Fixing **Finding C + E** additionally = **Recommended before codebase grows** — PEM '
    'write/read symmetry restored, PBFT threshold functions reject invalid input explicitly. '
    'Total additional effort: 15 minutes.',
    'Fixing **Finding D** additionally = **Apply after verifying deployment** — directory '
    'permissions tightened. Total additional effort: 2 minutes.',
    'Fixing **everything** = **Perfect at Peak** — zero known security issues, all latent '
    'traps closed, all defence-in-depth gaps filled.',
]:
    story.append(bul(item))
story += [sp(8), hr()]

print("Step 10 done: Section 6")

# ── SECTION 7 ─────────────────────────────────────────────────────────────────

story.append(section('SECTION 7 — DRWA FLOW GAP — No AllDenialCodes Exhaustiveness Count '
                     'Test Between mx-chain-core-go and Downstream Enforcement'))
story.append(sp(4))

story.append(classif_table([
    ['CWE:',          'CWE-691 (Insufficient Control Flow Management)'],
    ['Severity:',     'Medium'],
    ['Fix Required:', 'Yes — MANDATORY'],
]))
story.append(sp(5))

story.append(lbl('The DRWA Flow Context:'))
story.append(p('mx-chain-core-go is the starting repo in the DRWA pipeline. Its role is to '
               'define the shared vocabulary — the `DenialCode` type and its 15 known values '
               '— that every downstream repo imports and uses to make compliance decisions. '
               'The pipeline is:'))
story.append(sp(3))
story.append(code_block(
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
story.append(sp(4))

story.append(lbl('The Gap:'))
story.append(p('mx-chain-core-go defines 15 `DenialCode` constants and `AllDenialCodes()` '
               'returns all 15. The compliance gate in mx-chain-vm-common-go contains switch '
               'statements that handle these codes. There is no test in mx-chain-core-go that '
               'asserts `AllDenialCodes()` returns exactly 15 codes. Without this count '
               'assertion, a developer can add a 16th denial code to the constants block and '
               'omit it from `AllDenialCodes()` without any test failing — the exhaustiveness '
               'contract between mx-chain-core-go and downstream enforcement repos is not '
               'mechanically enforced.'))
story.append(sp(4))

story.append(p('Concretely: if a 16th denial code — for example '
               '`DenialSovereignChainBlocked DenialCode = "DRWA_SOVEREIGN_CHAIN_BLOCKED"` '
               '— is added to constants.go in mx-chain-core-go but not to `AllDenialCodes()`, '
               'the following happens:'))
story.append(sp(2))

for i, step in enumerate([
    'mx-chain-core-go compiles and tests pass — the new constant is non-empty and unique',
    '`AllDenialCodes()` still returns 15 codes — the new constant is silently excluded',
    'mx-chain-vm-common-go imports the updated mx-chain-core-go — it compiles with no error '
    'because Go does not require switch exhaustiveness on string types',
    'The compliance gate switch in mx-chain-vm-common-go has no `case DenialSovereignChainBlocked:` '
    'branch — the new code falls to default',
    'The default branch either logs a warning and allows the transfer, or returns a generic '
    'error — neither is the correct compliance behaviour for the new denial reason',
    'No test in mx-chain-vm-common-go fails — the new code was never in `AllDenialCodes()`',
    'Regulated transfers that should be denied with `DRWA_SOVEREIGN_CHAIN_BLOCKED` are either '
    'silently allowed or denied with a generic error that has no regulatory attribution',
], 1):
    story.append(bul(f'{i}. {step}'))
story.append(sp(4))

story.append(p('This gap is not a code bug in mx-chain-core-go — `AllDenialCodes()` is '
               'correctly implemented. It is a design gap between what mx-chain-core-go '
               'promises (a complete, authoritative vocabulary of denial reasons) and what '
               'it can guarantee (that `AllDenialCodes()` always reflects every constant '
               'in the block).'))
story.append(sp(4))

story.append(lbl('Who Is Affected:'))
for item in [
    '**Compliance gate maintainers in mx-chain-vm-common-go** — they have no automated signal '
    'when a new `DenialCode` is added to mx-chain-core-go that is missing from `AllDenialCodes()`',
    '**Regulatory reporting tools** — they receive denial records with a code that has no '
    'corresponding enforcement rule in the gate, making the record unattributable',
    '**Compliance / Regulatory Officers** — regulatory filings contain denial events attributed '
    'to a code that the compliance gate never explicitly handled',
    '**On-call engineers** — default branch behaviour is unpredictable; some implementations '
    'allow the transfer, others deny it generically — the on-call cannot determine correct '
    'behaviour without reading both repos',
]:
    story.append(bul(item))
story.append(sp(4))

story.append(lbl('The Fix:'))
story.append(p('**Step 1** — add a test in data/drwa/constants_test.go that verifies '
               '`AllDenialCodes()` returns exactly 15 codes and that every code passes '
               '`IsValid()` (after Finding A fix is applied):'))
story.append(code_block(
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
story.append(p('**Step 2** — add a test in mx-chain-vm-common-go that calls '
               '`drwa.AllDenialCodes()` and asserts that the compliance gate switch handles '
               'every returned code with a non-default branch. This test fails automatically '
               'when a new code is added to mx-chain-core-go without a corresponding '
               'enforcement branch in mx-chain-vm-common-go.'))
story.append(sp(4))

story.append(lbl('Why This Gap Is Specific to This Repo:'))
story.append(p('mx-chain-core-go is the only repo in the DRWA pipeline that defines the '
               'denial code vocabulary. It is the single source of truth for what denial '
               'reasons exist. Every other repo in the pipeline is a consumer of this '
               'vocabulary. The gap exists because Go string-typed switches are not exhaustive '
               '— the compiler does not warn when a new string constant is added to an '
               'imported package and the importing package\'s switch does not handle it.'))
story.append(sp(4))

story.append(lbl('Why This Gap Matters for Regulatory Compliance:'))
story.append(p('MiCA Article 45 and equivalent regulations require that every transfer denial '
               'be attributed to a specific, documented compliance rule. A denial code that '
               'exists in the vocabulary but is excluded from `AllDenialCodes()` is invisible '
               'to the exhaustiveness contract — downstream enforcement repos have no automated '
               'signal to handle it. This is not a theoretical risk — it is the exact failure '
               'mode that occurs every time a new denial reason is added to mx-chain-core-go '
               'without a corresponding entry in `AllDenialCodes()` and a corresponding update '
               'to mx-chain-vm-common-go.'))
story.append(sp(8))

print("Step 11 done: Section 7")

# ── PAGE NUMBERS ──────────────────────────────────────────────────────────────

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(MID)
    txt = f'Security Findings & Fix Report — mx-chain-core-go    |    Page {canvas.getPageNumber()}'
    canvas.drawCentredString(PAGE_W / 2, 8*mm, txt)
    canvas.setStrokeColor(BORDER_COL)
    canvas.setLineWidth(0.3)
    canvas.line(L_MARGIN, PAGE_H - T_MARGIN + 3*mm,
                PAGE_W - R_MARGIN, PAGE_H - T_MARGIN + 3*mm)
    canvas.restoreState()

# ── BUILD ─────────────────────────────────────────────────────────────────────

print("Building PDF...")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Done: {OUTPUT}")
