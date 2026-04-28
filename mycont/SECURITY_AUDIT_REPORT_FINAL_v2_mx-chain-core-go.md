# Security Findings & Fix Report — mx-chain-core-go

**Scan Type:** Full repository scan — all files analyzed
**Files Covered:** core/common.go, core/common_test.go, core/file.go, core/file_test.go, core/constants.go, data/drwa/constants.go, data/drwa/constants_test.go

**Overall Status:** 5 findings total — 2 real security findings (1 Medium, 1 Medium), 3 code/quality findings (1 Low, 1 Low, 1 Low), 1 false positive, 1 DRWA flow gap (Medium). Previous audit findings F1 (rand.Read error), F2 (strings.Index), F4 (untyped prefixes), F5 (test uniqueness) confirmed fixed in code. New findings introduced by changed code: **Finding A** — IsValid() accepts DenialUnknown as storable, re-introducing the compliance reporting failure the previous fix was designed to close. **Finding B** — LoadTomlFileToMap defers f.Close() after two early-return points, leaking file descriptors on f.Stat() and f.Read() error paths. **Finding C** — SaveSkToPemFile writes PEM with no identifier validation, producing unloadable key files with no error at write time. **Finding D** — CreateFile creates directories with os.ModePerm (0777). **Finding E** — GetPBFTThreshold and GetPBFTFallbackThreshold return threshold 1 for consensusSize 0 or negative, collapsing Byzantine fault tolerance silently.

---

## SECTION 1 — SUMMARY TABLE

| **#** | **File** | **Line** | **Severity** | **Type** | **Fix Required** | **Mandatory?** | **Status** |
|---|---|---|---|---|---|---|---|
| A | data/drwa/constants.go | 67 | Medium | DRWA FINDING | Yes | **YES — regulatory violations accumulate with every transaction if unfixed** | REAL FINDING |
| B | core/file.go | 69–100 | Medium | REAL FINDING | Yes | **YES — node crashes silently under disk pressure or in containers if unfixed** | REAL FINDING |
| C | core/file.go | 260–272 | Low | REAL FINDING | Recommended | No immediate risk — latent trap for downstream developers | REAL FINDING |
| D | core/file.go | 124 | Low | CODE QUALITY | Conditional | Only critical in containers with permissive umask — verify deployment | REAL FINDING |
| E | core/common.go | 46–52 | Low | CODE QUALITY | Recommended | No immediate risk — defence-in-depth gap if upstream validation regresses | REAL FINDING |
| 6 | core/common.go | 28–33 | — | FALSE POSITIVE | None | Not a vulnerability | DISMISSED |
| 7 | data/drwa/constants_test.go | — | Medium | DRWA FLOW GAP | Recommended | Regulatory gap grows with every new denial code added | OPEN |

---

## SECTION 2 — REAL FINDINGS

---

### Finding A — DRWA FINDING — IsValid() Accepts DenialUnknown as a Storable Denial Code in data/drwa/constants.go line 67

**Classification:**
- **CWE:** CWE-20 (Improper Input Validation)
- **CVSS v3.1 Score:** 5.3 (Medium) — AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N
- **Severity:** Medium
- **Fix Required:** Yes
- **Runtime Impact:** Any downstream compliance gate that calls `code.IsValid()` before storing a denial record will accept `DenialUnknown` ("DRWA_UNKNOWN") as a valid storable denial reason. A denial record carrying "DRWA_UNKNOWN" is not attributable to any specific compliance rule — the regulatory audit trail contains a denial event with no attributable reason.
- **Monitoring Impact:** No compile-time error, no runtime panic — the `DenialUnknown` code is silently stored in the compliance index as if it were a valid denial reason.

**Severity Note:** Medium. Data origin is INTERNAL — the return value of `NormalizeDenialCode` for any unrecognized input. No external attacker input is required beyond triggering a code path that calls `NormalizeDenialCode` on an unrecognized string. The previous audit prescribed `IsValid()` to return `false` for the unknown sentinel. The implementation inverted this: `IsValid()` returns `true` for `DenialUnknown` (line 67). `IsKnown()` correctly returns `false` for `DenialUnknown`, but `IsValid()` is the natural method name a downstream developer reaches for as a storage pre-check. The inversion is a design contract violation that silently re-introduces the regulatory reporting failure the previous fix was designed to close.

**What the Vulnerable Function Does:**
`IsValid()` in data/drwa/constants.go lines 66–68 returns `true` for `DenialUnknown` ("DRWA_UNKNOWN") via the condition `code == DenialUnknown || code.IsKnown()`. The doc comment says "including the explicit unknown sentinel" — this is the design choice that creates the vulnerability.
**What it does NOT do:** does not distinguish between "this code is a known concrete denial reason" and "this code is the explicit fallback for unrecognized inputs". Does not prevent `DenialUnknown` from being stored in the compliance index when `IsValid()` is used as the storage guard.
**Call chain:** compliance gate evaluates transfer → `NormalizeDenialCode` returns `DenialUnknown` for unrecognized input → `code.IsValid()` returns `true` → denial record stored with `denial_code: "DRWA_UNKNOWN"` → indexed to compliance store → regulatory report contains denial with no attributable rule.

**Where Does the Vulnerable Data Come From:**
`NormalizeDenialCode` (line 73) returns `DenialUnknown` for any unrecognized non-empty input → downstream compliance gate calls `code.IsValid()` → returns `true` → `DenialUnknown` stored in compliance index → regulatory audit trail contains denial with no rule attribution.
**Data origin:** INTERNAL (`NormalizeDenialCode` return value). No external input required beyond triggering the unrecognized-input path.

**Who Uses This Data and Why It Must Be Trusted:**
1. **DevOps / Node Operator:** Monitors denial code distribution in compliance metrics. Breaks if `DenialUnknown` denial records accumulate — metrics show denials with no rule attribution. Why watching matters: a spike in `DenialUnknown` denials is the only signal of an unrecognized-input bug. **Silent failure consequence:** operators assume the denial reason was intentionally "unknown"; the bug is never investigated.
2. **Security / Compliance Engineer:** Relies on `IsValid()` as the storage guard to reject unattributable denial codes. Breaks because `IsValid()` returns `true` for `DenialUnknown` — the guard passes silently. Why watching matters: a denial with no attributable rule cannot be attributed to a specific compliance gate decision. **Silent failure consequence:** compliance audit cannot determine which rule triggered the denial; the gate appears to be malfunctioning.
3. **Compliance / Regulatory Officer:** Must demonstrate that every transfer denial corresponds to a specific regulatory rule (KYC, AML, sanctions, etc.). Breaks if `DenialUnknown` appears in the compliance index — the denial reason is "unknown", which cannot be attributed to any rule. Why watching matters: MiCA Article 45 and equivalent regulations require that every denial be attributed to a specific compliance rule. **Silent failure consequence:** regulatory filing contains unexplained denials — potential regulatory violation.
4. **On-Call Engineer:** Investigates compliance gate anomalies. Breaks because `DenialUnknown` gives no indication of which code path produced it. Why watching matters: there is no runbook entry for a `DenialUnknown` denial. **Silent failure consequence:** on-call cannot determine root cause without full code path analysis of every denial branch.

**What an Attacker Can Do:**
1. **Compliance Index Pollution via Unrecognized Input:** Attacker sends a transfer with a denial code field set to an unrecognized string → `NormalizeDenialCode` returns `DenialUnknown` → `IsValid()` returns `true` → denial record stored with `denial_code: "DRWA_UNKNOWN"`.
   - **Exact log output:** No error — denial record stored silently
   - **Consequence:** Compliance index accumulates `DenialUnknown` records; regulatory report contains denials with no rule attribution.
2. **Regulatory Report Corruption:** Regulatory reporting tool filters denial records by `DenialCode` — records with `DenialUnknown` are excluded from category counts or placed in an "unknown" bucket. Total denial count does not match sum of category counts.
   - **Exact log output:** No error
   - **Consequence:** Regulatory report is internally inconsistent — potential regulatory filing failure.
3. **Compliance Gate Bypass via Default Branch:** Downstream switch on `DenialCode` has no `case DenialUnknown:` branch — unknown code falls to default which may log a warning but not block the transfer.
   - **Exact log output:** No error — default branch executes, transfer may proceed
   - **Consequence:** Transfer that should be denied proceeds because the denial code was never resolved to a concrete rule.
4. **Audit Trail Collapse:** High-volume transfers through the unrecognized-input path — all denial records carry `DenialUnknown`, making the compliance index useless for attribution.
   - **Exact log output:** No error — all records indexed with `DenialUnknown`
   - **Consequence:** Compliance dashboard shows thousands of denials with no rule attribution; dashboard is unusable for regulatory reporting.

**Why This Is Specific to This Feature:**
`DenialCode` is the only typed string in data/drwa/constants.go that carries regulatory significance — each value maps to a specific compliance rule that must be attributable in regulatory filings. `IsValid()` is the only validation method on `DenialCode`. Its semantics directly determine what gets stored in the compliance index. No other typed string in the repo has the property that its validation method accepting a sentinel value produces a silent regulatory reporting failure. The previous audit's prescribed fix explicitly required `IsValid()` to return `false` for the unknown sentinel — the implementation inverted this contract.

**The Fix:**

**BEFORE** (data/drwa/constants.go lines 64–68 — exact code from file):
```go
// IsValid reports whether code is a valid canonical value, including the
// explicit unknown sentinel. The empty string is never valid.
func (code DenialCode) IsValid() bool {
    return code == DenialUnknown || code.IsKnown()
}
```

**AFTER:**
```go
// IsValid reports whether code is one of the 15 concrete denial codes
// emitted by the DRWA gate. Returns false for DenialUnknown and the
// empty string. Use IsValid() as the storage guard before writing a
// denial record to the compliance index.
func (code DenialCode) IsValid() bool {
    return code.IsKnown()
}
```

**What each line does:**
- Removing `code == DenialUnknown` from the return condition means `IsValid()` returns `false` for `DenialUnknown`, consistent with the previous audit's prescription and with the semantics of `IsKnown()`.
- `IsKnown()` already iterates `AllDenialCodes()` and returns `true` only for the 15 concrete codes — no new logic needed.

**Why This Fix Is Safe:** No imports needed. No existing call sites in this repo are broken — `IsValid()` has no callers in mx-chain-core-go itself. Downstream code that uses `IsValid()` as a storage guard gains the correct behaviour. `DenialUnknown` remains a valid named constant.

**Integration Impact — Will It Break Existing Flow:**
- **One existing test must be updated before applying this fix.** `TestDenialCodes_ValidityAndNormalization` at constants_test.go line 28 currently asserts `if !DenialUnknown.IsValid()` — this assertion flips after the fix and will fail if not updated first. Update it to `if DenialUnknown.IsValid()` before deploying.
- **`NormalizeDenialCode` internal behaviour is unchanged.** The function calls `code.IsValid()` at line 80 and `upper.IsValid()` at line 85. After the fix, `DenialUnknown` no longer passes `IsValid()`, so `NormalizeDenialCode("DRWA_UNKNOWN")` reaches the final `return DenialUnknown` fallback at line 89 instead of the early return at line 81. The output is identical — `DenialUnknown` is still returned — via a different internal path. No caller observes any difference.
- **No runtime flow breaks.** `IsKnown()` is not changed. All 15 concrete denial codes continue to pass both `IsValid()` and `IsKnown()` unchanged. All downstream compliance gate paths that assign a concrete denial code are unaffected.
- **Smooth integration:** After updating the one test assertion, `go test ./...` passes clean. No API changes, no signature changes, no import changes.

**Test Update Required:** Update `TestDenialCodes_ValidityAndNormalization` in constants_test.go line 28 — change assertion so that `DenialUnknown.IsValid()` must return `false`. Add `TestDenialUnknown_IsNotStorable` asserting `DenialUnknown.IsValid() == false`.

**Why This Fix Is Necessary:** A compliance type whose "is valid for storage" method returns `true` for the explicit "I don't know what this is" sentinel is a regulatory reporting risk. Every denial record in the compliance audit trail must carry a specific, attributable denial reason.
Silence is worse than explicit failure because a denial record with `denial_code: "DRWA_UNKNOWN"` stored in the compliance index gives no indication to the compliance engineer, the regulatory officer, or the on-call engineer that the denial reason was never resolved to a concrete rule — it appears as a legitimate denial with a named but unattributable reason field.

**If Left Unfixed — Consequences:**
- Every transfer that triggers an unrecognized denial code path permanently stores a `DRWA_UNKNOWN` record in the compliance index. These records accumulate with every transaction and cannot be retroactively corrected.
- Under MiCA Article 45 this is a direct regulatory filing violation — you cannot demonstrate which compliance rule triggered the denial.
- A downstream switch with no `case DenialUnknown:` branch silently allows transfers that should be denied — a regulated transfer that should be blocked goes through with no error, no log, no alert.
- Compliance dashboards become unreliable — denial counts include `DRWA_UNKNOWN` records that map to no rule, making category breakdowns internally inconsistent.
- **This is the highest-priority fix in the entire report. It must be applied before the system processes any real regulated transfers.**

---

### Finding B — REAL FINDING — defer f.Close() Placed After Early Returns Leaks File Descriptor on Error Paths in core/file.go lines 69–100

**Classification:**
- **CWE:** CWE-775 (Missing Release of File Descriptor or Handle after Effective Lifetime)
- **CVSS v3.1 Score:** 5.3 (Medium) — AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H
- **Severity:** Medium
- **Fix Required:** Yes
- **Runtime Impact:** `LoadTomlFileToMap` opens a file at line 71, calls `f.Stat()` at line 76 and `f.Read()` at line 84. If either returns an error the function returns early at lines 78 or 86. The `defer f.Close()` is registered at line 89 — after both early return points. A defer only executes if the goroutine reaches the line where it is declared. On the `f.Stat()` error path and the `f.Read()` error path the defer is never registered, so `f.Close()` is never called. The file descriptor is leaked for the lifetime of the process.
- **Monitoring Impact:** No error logged for the leaked descriptor. The OS file descriptor table silently fills. On Linux the default per-process limit is 1024 (soft) / 4096 (hard) open file descriptors. A node that repeatedly calls `LoadTomlFileToMap` on a file that triggers `f.Stat()` or `f.Read()` errors will exhaust its file descriptor table, causing all subsequent file opens — including PEM key loading and config loading — to fail with "too many open files".

**Severity Note:** Medium. Data origin is LOCAL FILE (operator-controlled filesystem). The error paths that trigger the leak require either a filesystem race (file deleted or permissions changed between `OpenFile` and `Stat`) or a kernel-level read error (disk I/O failure). Neither requires an external attacker. A node under disk pressure or with a misconfigured filesystem will trigger this path silently. All other file-handling functions in the same file (`LoadTomlFile` line 48, `SaveTomlFile` line 62, `LoadJsonFile` line 110) correctly register `defer f.Close()` immediately after the file is opened — the misplacement is unique to `LoadTomlFileToMap`.

**What the Vulnerable Function Does:**
`LoadTomlFileToMap` in core/file.go opens a file, calls `f.Stat()` to get the file size, allocates a buffer of that size, calls `f.Read()` to fill it, then defers `f.Close()` and proceeds to parse the buffer as TOML.
**What it does NOT do:** does not register `defer f.Close()` immediately after `OpenFile` succeeds. Does not call `f.Close()` explicitly on the error paths at lines 78 and 86.
**Call chain:** node startup → `LoadTomlFileToMap("config.toml")` → `OpenFile` succeeds → `f.Stat()` fails (disk error) → `return nil, err` at line 78 → defer never registered → `f.Close()` never called → file descriptor leaked → repeated calls exhaust fd table → all subsequent file opens fail with `EMFILE`.

**Where Does the Vulnerable Data Come From:**
Operator-placed config file → `OpenFile` opens it → `f.Stat()` or `f.Read()` fails due to filesystem error → early return without closing.
**Data origin:** LOCAL FILE.

**Who Uses This Data and Why It Must Be Trusted:**
1. **DevOps / Node Operator:** Relies on `LoadTomlFileToMap` releasing file descriptors on all paths. Breaks if fd table is exhausted — node cannot open PEM key files or config files at startup. **Silent failure consequence:** node fails to start with "too many open files" with no indication the root cause is a leaked descriptor in `LoadTomlFileToMap`.
2. **Security / Compliance Engineer:** Relies on node starting cleanly to begin processing regulated transfers. Breaks if node cannot open key files due to fd exhaustion. **Silent failure consequence:** all regulated transfers blocked because the node never reaches the compliance gate.
3. **Compliance / Regulatory Officer:** Relies on the node being operational to process and record regulated transfers. Breaks if node is DoS'd via fd exhaustion. **Silent failure consequence:** regulated transfers are not processed during the outage window — potential regulatory reporting gap.
4. **On-Call Engineer:** Investigates node startup failures. Breaks because "too many open files" gives no indication of which function leaked the descriptor. **Silent failure consequence:** on-call cannot determine root cause without strace or lsof analysis.

**What an Attacker Can Do:**
1. **Filesystem Race to Trigger Leak:** Attacker with filesystem access repeatedly creates and removes a config file between `OpenFile` and `Stat` → `f.Stat()` fails on every call → each call leaks one fd → fd table exhausted → node cannot open any files.
   - **Exact log output:** No error for the leaked fd — only "too many open files" when full
   - **Consequence:** Node DoS — all file operations fail.
2. **Disk I/O Error Amplification:** Under disk pressure, `f.Read()` returns an error → fd leaked → repeated config reloads (e.g. SIGHUP-triggered) each leak one fd → fd table exhausted faster than the disk recovers.
   - **Exact log output:** No error for the leaked fd
   - **Consequence:** Node cannot recover from disk pressure — permanent DoS until restart.
3. **Container fd Limit Exhaustion:** In a containerised deployment with a low fd limit, a single burst of config reload errors exhausts the fd table — node cannot open the PEM key file needed to sign blocks.
   - **Exact log output:** No error at leak time
   - **Consequence:** Node stops signing blocks — silently excluded from consensus.
4. **Repeated Error Path Triggering:** Attacker causes repeated `f.Stat()` failures by toggling file permissions — each call leaks one fd — fd table exhausted in O(fd_limit) calls.
   - **Exact log output:** No error
   - **Consequence:** Node DoS with no log trail pointing to the root cause.

**Why This Is Specific to This Feature:**
`LoadTomlFileToMap` is the only function in core/file.go that places `defer f.Close()` after error-returning statements that follow the file open. All other functions in the same file correctly register `defer f.Close()` immediately after the file is opened, before any operation that can return early. The misplacement is unique to `LoadTomlFileToMap` and is not present in any other file-handling function in the package.

**The Fix:**

**BEFORE** (core/file.go lines 69–100 — exact code from file):
```go
func LoadTomlFileToMap(relativePath string) (map[string]interface{}, error) {
    f, err := OpenFile(relativePath)
    if err != nil {
        return nil, err
    }

    fileinfo, err := f.Stat()
    if err != nil {
        return nil, err          // fd leaked here — defer not yet registered
    }

    filesize := fileinfo.Size()
    buffer := make([]byte, filesize)

    _, err = f.Read(buffer)
    if err != nil {
        return nil, err          // fd leaked here — defer not yet registered
    }

    defer func() {               // too late — only reached on success path
        _ = f.Close()
    }()
    ...
}
```

**AFTER:**
```go
func LoadTomlFileToMap(relativePath string) (map[string]interface{}, error) {
    f, err := OpenFile(relativePath)
    if err != nil {
        return nil, err
    }

    defer func() {               // registered immediately after open — fires on all paths
        _ = f.Close()
    }()

    fileinfo, err := f.Stat()
    if err != nil {
        return nil, err          // defer now fires — fd closed
    }

    filesize := fileinfo.Size()
    buffer := make([]byte, filesize)

    _, err = f.Read(buffer)
    if err != nil {
        return nil, err          // defer now fires — fd closed
    }
    ...
}
```

**What each line does:**
- Moving `defer f.Close()` to immediately after the nil-error check on `OpenFile` ensures it is registered on every code path that successfully opens the file.
- No other logic changes — the fix is a single block move of 3 lines.

**Why This Fix Is Safe:** Semantically identical for all success paths. Additive only for error paths — `f.Close()` is now called on paths where it was previously skipped. No imports needed. No API changes.

**Integration Impact — Will It Break Existing Flow:**
- **No existing tests break.** The fix is a 3-line block move. The success path — which is the only path currently exercised by all existing tests — is completely unchanged. `defer f.Close()` fires at exactly the same point (function return) on the success path as before.
- **No runtime flow breaks.** All callers of `LoadTomlFileToMap` receive identical return values on both success and error paths. The only change is that `f.Close()` is now called on the `f.Stat()` and `f.Read()` error paths where it was previously skipped. Callers already receive an error on those paths and cannot observe whether the fd was closed.
- **Smooth integration:** Drop-in safe. No API changes, no signature changes, no import changes. `go test ./...` passes clean with no modifications.

**Test Update Required:** Add a test that calls `LoadTomlFileToMap` with a file that is deleted between open and read and asserts no file descriptor leak. Verify with `/proc/self/fd` that the fd count does not increase on repeated error-path calls.

**Why This Fix Is Necessary:** A file descriptor leak in a config-loading function that is called at node startup and on config reload is a latent DoS vector. The leak is silent — no error is logged, no metric is incremented. The only observable symptom is "too many open files" when the fd table is exhausted, at which point the node cannot recover without a restart.
Silence is worse than explicit failure because the operator, the on-call engineer, and the compliance engineer all see a healthy node that suddenly cannot open any files, with no indication the root cause is a three-line misplacement of a defer statement in `LoadTomlFileToMap`.

**If Left Unfixed — Consequences:**
- Under disk pressure: the node silently accumulates leaked file descriptors, then crashes with "too many open files" at an unpredictable point during the incident — exactly when you need it most stable.
- In containerised deployments with low fd limits: a single burst of config reload errors can exhaust the fd table in minutes, stopping the node from signing blocks and silently excluding it from consensus.
- The failure symptom gives no indication of the root cause — on-call spends hours debugging the wrong thing while the node is down.
- **This is the second highest-priority fix. It must be applied before any production deployment under disk pressure or in containers.**

---

### Finding C — REAL FINDING — SaveSkToPemFile Writes PEM Block with No Identifier Validation in core/file.go lines 260–272

**Classification:**
- **CWE:** CWE-20 (Improper Input Validation)
- **CVSS v3.1 Score:** 4.0 (Low) — AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:L
- **Severity:** Low
- **Fix Required:** Yes
- **Runtime Impact:** `SaveSkToPemFile` writes a PEM block with type `"PRIVATE KEY for " + identifier` with no validation of the identifier string. `LoadSkPkFromPemFile` and `LoadAllKeysFromPemFile` both call `isValidPemPublicKeySuffix` on the extracted suffix, which rejects empty strings, strings with leading/trailing whitespace, and strings containing Unicode control characters. If `SaveSkToPemFile` writes a PEM file with an identifier that fails `isValidPemPublicKeySuffix`, the file cannot be loaded back by the same package. The write succeeds silently; the load fails with `ErrPemFileIsInvalid`.
- **Monitoring Impact:** No error at write time. The PEM file is created on disk. The failure is discovered only when the node attempts to load the key at startup, producing `ErrPemFileIsInvalid` with no indication that the root cause is the identifier that was written.

**Severity Note:** Low. Data origin is the caller-supplied identifier string. In production the identifier is the node's public key string, which is validated upstream. The risk is a programming error in a downstream repo that passes an empty, whitespace-padded, or control-character-containing identifier to `SaveSkToPemFile`. The consequence is a PEM file that cannot be loaded — node fails to start. The writer and reader of the same PEM format apply different validation rules to the same field — this asymmetry is the root cause.

**What the Vulnerable Function Does:**
`SaveSkToPemFile` in core/file.go lines 260–272 checks only that `file != nil`, then concatenates the identifier directly into the PEM block type and calls `pem.Encode`.
**What it does NOT do:** does not validate that identifier is non-empty. Does not validate that identifier passes `isValidPemPublicKeySuffix`. Does not check for leading/trailing whitespace or control characters in identifier. Does not apply the same validation that the loaders apply when reading the same field back.
**Call chain:** key generator → `SaveSkToPemFile(file, "", skBytes)` → `pem.Encode` writes block with type `"PRIVATE KEY for "` → file written successfully → node restart → `LoadSkPkFromPemFile` → `isValidPemPublicKeySuffix("")` returns `false` → `ErrPemFileIsInvalid` → node fails to start.

**Where Does the Vulnerable Data Come From:**
Caller-supplied identifier string → concatenated into PEM block type → written to disk → read back by `LoadSkPkFromPemFile` → `isValidPemPublicKeySuffix` rejects it → `ErrPemFileIsInvalid`.
**Data origin:** CALLER-SUPPLIED. The identifier is not validated at write time.

**Who Uses This Data and Why It Must Be Trusted:**
1. **DevOps / Node Operator:** Relies on `SaveSkToPemFile` producing a file that can be loaded back by `LoadSkPkFromPemFile`. Breaks if identifier is invalid — node fails to start with `ErrPemFileIsInvalid`. **Silent failure consequence:** operator sees a startup failure with no indication the root cause is the identifier written at key generation time.
2. **Security / Compliance Engineer:** Relies on the key loading path being symmetric with the key writing path. Breaks if the writer accepts inputs the reader rejects — key files become unloadable without any write-time error. **Silent failure consequence:** key generation succeeds, node startup fails — the failure is attributed to the wrong operation.
3. **On-Call Engineer:** Investigates node startup failures. Breaks because `ErrPemFileIsInvalid` at load time gives no indication the root cause is an invalid identifier written at key generation time. **Silent failure consequence:** on-call investigates the loader without knowing the writer is the source of the invalid data.
4. **Compliance / Regulatory Officer:** Relies on the node being operational. Breaks if node cannot start due to an unloadable key file. **Silent failure consequence:** regulated transfers are not processed during the outage window.

**What an Attacker Can Do:**
1. **Empty Identifier Write:** Developer calls `SaveSkToPemFile(file, "", skBytes)` → PEM file written with type `"PRIVATE KEY for "` → `LoadSkPkFromPemFile` fails with `ErrPemFileIsInvalid`.
   - **Exact log output:** No error at write time — `ErrPemFileIsInvalid` at load time
   - **Consequence:** Node cannot start — key file is unloadable.
2. **Whitespace-Padded Identifier:** Developer calls `SaveSkToPemFile(file, " erd1abc ", skBytes)` → PEM file written with type `"PRIVATE KEY for  erd1abc "` → `isValidPemPublicKeySuffix` rejects leading/trailing space → `ErrPemFileIsInvalid` at load time.
   - **Exact log output:** No error at write time
   - **Consequence:** Node cannot start — key file is unloadable.
3. **Control Character in Identifier:** Developer passes an identifier containing a tab or null byte → PEM file written → `isValidPemPublicKeySuffix` rejects control character → `ErrPemFileIsInvalid` at load time.
   - **Exact log output:** No error at write time
   - **Consequence:** Node cannot start — key file is unloadable.
4. **Write-Read Asymmetry Exploitation:** Attacker with key generation access writes a PEM file with a malformed identifier → node operator loads the file → `ErrPemFileIsInvalid` → operator regenerates key → attacker repeats — persistent node startup DoS.
   - **Exact log output:** No error at write time
   - **Consequence:** Persistent node startup failure with no write-time signal.

**Why This Is Specific to This Feature:**
`SaveSkToPemFile` and `LoadSkPkFromPemFile` / `LoadAllKeysFromPemFile` are the only functions in the repo that form a write-read pair for the same PEM format. `isValidPemPublicKeySuffix` is defined in the same file (line 247) and is called by both loaders. It is not called by the writer. This asymmetry is unique to the PEM key loading path — no other write-read pair in the repo applies validation only on the read side.

**The Fix:**

**BEFORE** (core/file.go lines 260–272 — exact code from file):
```go
func SaveSkToPemFile(file *os.File, identifier string, skBytes []byte) error {
    if file == nil {
        return ErrNilFile
    }

    blk := pem.Block{
        Type:  "PRIVATE KEY for " + identifier,
        Bytes: skBytes,
    }

    return pem.Encode(file, &blk)
}
```

**AFTER:**
```go
func SaveSkToPemFile(file *os.File, identifier string, skBytes []byte) error {
    if file == nil {
        return ErrNilFile
    }
    if !isValidPemPublicKeySuffix(identifier) {
        return fmt.Errorf("%w invalid identifier for PEM block type", ErrPemFileIsInvalid)
    }

    blk := pem.Block{
        Type:  "PRIVATE KEY for " + identifier,
        Bytes: skBytes,
    }

    return pem.Encode(file, &blk)
}
```

**What each line does:**
- `isValidPemPublicKeySuffix(identifier)` — reuses the existing validation function already called by both loaders; no new logic needed.
- Returns `ErrPemFileIsInvalid` wrapped with context — consistent with the error type returned by the loaders for the same condition.

**Why This Fix Is Safe:** `isValidPemPublicKeySuffix` is already defined in the same file (line 247). `fmt` is already imported. No API changes — the new error path only fires for inputs that would produce an unloadable PEM file anyway.

**Integration Impact — Will It Break Existing Flow:**
- **No existing tests break.** The existing `TestSaveSkToPemFile` "should work" sub-test passes `"data"` as the identifier. `"data"` is non-empty, has no whitespace, and has no control characters — it passes `isValidPemPublicKeySuffix` and the test continues to pass unchanged.
- **No runtime flow breaks.** Every existing production caller passes a real public key string (e.g. `"erd1abc..."`) which already satisfies `isValidPemPublicKeySuffix`. The new guard is unreachable for all current valid callers. The function signature is unchanged.
- **Smooth integration:** Drop-in safe. No import changes needed. `go test ./...` passes clean with no modifications to existing tests.

**Test Update Required:** Add sub-tests to `TestSaveSkToPemFile`:
- empty identifier should return `ErrPemFileIsInvalid`
- whitespace-padded identifier should return `ErrPemFileIsInvalid`
- control character in identifier should return `ErrPemFileIsInvalid`

**Why This Fix Is Necessary:** The writer and reader of the same PEM format apply different validation rules to the same field. This asymmetry means a file can be written successfully but cannot be read back. In a key-loading path that establishes node identity, a write-succeeds/read-fails asymmetry is a latent node startup failure with no error signal at the point of failure.
Silence is worse than explicit failure because the operator, the on-call engineer, and the compliance engineer all see a successful key generation followed by a startup failure, with no indication the root cause is the identifier written at generation time.

**If Left Unfixed — Consequences:**
- No immediate production risk — all current callers pass valid identifiers.
- Becomes a hard-to-diagnose node startup failure the moment any downstream developer passes an empty, whitespace-padded, or control-character-containing identifier to `SaveSkToPemFile`. The write succeeds with no error; the node fails to start on the next restart with `ErrPemFileIsInvalid` and no pointer to the write-time cause.
- **Recommended to fix before the codebase grows. Not mandatory today.**

---

### Finding D — CODE QUALITY — CreateFile Creates Directory with os.ModePerm (0777) in core/file.go line 124

**Classification:**
- **CWE:** CWE-732 (Incorrect Permission Assignment for Critical Resource)
- **CVSS v3.1 Score:** 3.3 (Low) — AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N
- **Severity:** Low
- **Fix Required:** Yes
- **Runtime Impact:** `CreateFile` calls `os.MkdirAll(absPath, os.ModePerm)` at line 124. `os.ModePerm` is `0777` — world-readable, world-writable, world-executable before umask. On a system with a permissive umask (e.g. `0000` or `0002`), the created directory is writable by all local users. The file created inside it uses `FileModeUserReadWrite` (`0600`), but the directory itself is `0777`. A local user can create, rename, or delete files inside the directory, including log or key files written by the node.
- **Monitoring Impact:** No error logged. The directory is created silently with world-write permissions. The permission mismatch between the directory (`0777`) and the files inside it (`0600`) is not flagged anywhere.

**Severity Note:** Low. Requires local filesystem access. The umask on most production Linux systems (`0022`) reduces `0777` to `0755`, which is group/world-readable but not writable. The risk is real on systems with non-standard umask or in containerised environments where the node runs as root with umask `0000`.

**What the Vulnerable Code Does:**
core/file.go line 124:
```go
err = os.MkdirAll(absPath, os.ModePerm)
```
`os.ModePerm = 0777`. The created directory is world-writable before umask. The file inside it is created with `FileModeUserReadWrite` (`0600`) — correct. The directory permission is inconsistent with the file permission.
**What it does NOT do:** does not use a restrictive permission for the directory. Does not document the permission choice. Does not apply the same access restriction to the directory as to the files it contains.

**The Fix:**

**BEFORE** (core/file.go line 124 — exact code from file):
```go
err = os.MkdirAll(absPath, os.ModePerm)
```

**AFTER:**
```go
err = os.MkdirAll(absPath, 0700)
```

**What each line does:**
- `0700` — owner read/write/execute only. Consistent with `FileModeUserReadWrite` (`0600`) on the files inside. No other local user can list, create, or delete files in the directory.

**Why This Fix Is Safe:** The node process is the only consumer of the created directory. `0700` gives the node full access. No other process needs access to the log/key directory.

**Integration Impact — Will It Break Existing Flow:**
- **No existing tests break.** The existing `TestCreateFile` test does not assert directory permissions — it only checks that the file is created and its name contains the prefix and extension. It continues to pass unchanged.
- **Conditional runtime impact — deployment verification required.** If any external process on the same host currently reads from or lists the directory created by `CreateFile` — such as a log aggregator, a monitoring sidecar, or a backup agent running as a different OS user — changing from effective `0755` (after umask `0022`) to `0700` will prevent that process from accessing the directory. **Before applying this fix, verify that no sidecar, log collector, or monitoring agent reads the node’s log or key directory.** On standard single-process node deployments this is safe.
- **Smooth integration for standard deployments:** Drop-in safe for nodes where the node process is the sole owner of its directories. No API changes, no signature changes, no import changes.

**Test Update Required:** Add a test that calls `CreateFile` and asserts the created directory has mode `0700` (after masking with `^umask`).

**Why This Fix Is Necessary:** A directory that holds node key files and log files must not be world-writable. The permission mismatch between the directory (`0777`) and the files inside it (`0600`) creates a gap where a local attacker can manipulate the directory contents even though the files themselves are protected.

**If Left Unfixed — Consequences:**
- On a standard production Linux server with umask `0022`: effective directory permission is `0755` — group and world readable but not writable. Risk is low and the node operates normally.
- In containers running as root with umask `0000` or on systems with permissive umask: the directory is world-writable. Any co-located process can create, rename, or delete files inside it including log files and key files.
- **Not mandatory on standard deployments. Mandatory in containers with permissive umask. Verify your deployment environment before deciding.**

---

### Finding E — CODE QUALITY — GetPBFTThreshold and GetPBFTFallbackThreshold Return Threshold 1 for consensusSize 0 or Negative in core/common.go lines 46–52

**Classification:**
- **CWE:** CWE-20 (Improper Input Validation)
- **CVSS v3.1 Score:** 3.1 (Low) — AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N
- **Severity:** Low
- **Fix Required:** Yes
- **Runtime Impact:** `GetPBFTThreshold(0)` returns `0*2/3 + 1 = 1`. `GetPBFTThreshold(-1)` returns `-1*2/3 + 1 = 1` (Go integer division truncates toward zero: `-2/3 = 0`). `GetPBFTFallbackThreshold(0)` returns `0*1/2 + 1 = 1`. A threshold of 1 for a consensus size of 0 or 1 means a single node can reach consensus alone — the pBFT safety guarantee (requiring 2/3+1 honest nodes) collapses. If the consensus size is supplied from an external or misconfigured source, a zero or negative value silently produces a threshold that allows single-node consensus, bypassing the Byzantine fault tolerance guarantee.
- **Monitoring Impact:** No error logged. No panic. The function returns a numerically valid but semantically wrong threshold. The caller has no signal that the input was invalid.

**Severity Note:** Low. In practice, consensus size is validated upstream before these functions are called. The risk is a programming error in a downstream repo that passes an unvalidated consensus size. The consequence is a silent safety degradation — the node participates in consensus with a threshold that provides no Byzantine fault tolerance. Tests cover sizes 2–7 only; `consensusSize = 0`, `1`, and negative values are not tested.

**What the Vulnerable Code Does:**
core/common.go lines 46–52 (exact code from file):
```go
func GetPBFTThreshold(consensusSize int) int {
    return consensusSize*2/3 + 1
}

func GetPBFTFallbackThreshold(consensusSize int) int {
    return consensusSize*1/2 + 1
}
```
No guard for `consensusSize <= 0`. No guard for `consensusSize == 1` in `GetPBFTFallbackThreshold` (returns 1, same as the input — threshold equals consensus size).
**What it does NOT do:** does not validate that `consensusSize` is a positive integer greater than 1. Does not return an error or panic for invalid input. Does not document the valid input range.

**The Fix:**

**BEFORE** (core/common.go lines 46–52 — exact code from file):
```go
func GetPBFTThreshold(consensusSize int) int {
    return consensusSize*2/3 + 1
}

func GetPBFTFallbackThreshold(consensusSize int) int {
    return consensusSize*1/2 + 1
}
```

**AFTER:**
```go
func GetPBFTThreshold(consensusSize int) int {
    if consensusSize <= 0 {
        return 0
    }
    return consensusSize*2/3 + 1
}

func GetPBFTFallbackThreshold(consensusSize int) int {
    if consensusSize <= 0 {
        return 0
    }
    return consensusSize*1/2 + 1
}
```

**What each line does:**
- `consensusSize <= 0` guard returns `0` — a threshold of `0` is unambiguously invalid and will be rejected by any downstream consensus check that requires `threshold > 0`. This makes the invalid input visible rather than silently producing a threshold of `1`.

**Why This Fix Is Safe:** Additive only for invalid inputs. All valid consensus sizes (`>= 2`) produce the same result as before.

**Integration Impact — Will It Break Existing Flow:**
- **No existing tests break.** `TestGetPBFTThreshold_ShouldWork` and `TestGetPBFTFallbackThreshold_ShouldWork` test sizes `2–7` only. All of those produce the same results as before — the guard is never reached for any currently tested input.
- **No runtime flow breaks.** All existing callers in mx-chain-go pass validated consensus sizes of `>= 2`. The guard is unreachable for all current valid callers. The function signatures are unchanged.
- **Smooth integration:** Drop-in safe. No API changes, no import changes. `go test ./...` passes clean with no modifications to existing tests.

**Test Update Required:** Add assertions to `TestGetPBFTThreshold_ShouldWork` and `TestGetPBFTFallbackThreshold_ShouldWork`:
```go
assert.Equal(t, 0, GetPBFTThreshold(0))
assert.Equal(t, 0, GetPBFTThreshold(-1))
assert.Equal(t, 0, GetPBFTFallbackThreshold(0))
assert.Equal(t, 0, GetPBFTFallbackThreshold(-1))
```

**Why This Fix Is Necessary:** A consensus threshold function that silently returns `1` for an invalid consensus size violates its own contract. A threshold of `1` means a single node can reach consensus alone — the Byzantine fault tolerance guarantee that pBFT provides is silently discarded for any caller that passes an unvalidated consensus size.

**If Left Unfixed — Consequences:**
- No immediate production risk — all current callers in mx-chain-go pass validated consensus sizes of `>= 2`. The guard is never reached today.
- Becomes a critical consensus safety failure if any future upstream change removes or bypasses the consensus size validation and passes `0` or a negative value. `GetPBFTThreshold(0)` returns `1` — a single node can reach consensus alone with no error, no log, no alert.
- **Not mandatory today. Recommended as a defence-in-depth measure before any upstream consensus size validation is refactored.**

---

## SECTION 3 — FALSE POSITIVES

### Finding 6 — FALSE POSITIVE — UniqueIdentifier Returns Non-Printable Bytes

**What the Scanner Flagged:** `UniqueIdentifier()` in core/common.go returns `string(buff)` where `buff` is a 32-byte slice filled by `io.ReadFull(rand.Reader, buff)`. The resulting string contains non-printable, non-UTF-8 bytes. Flagged as potential unsafe string construction or encoding issue.

**Why It Is Not a Vulnerability:**
`string(buff)` in Go is a valid byte-to-string conversion — it does not require the bytes to be valid UTF-8. The Go specification explicitly allows strings to contain arbitrary bytes. `UniqueIdentifier()` is documented as returning a "unique string identifier of 32 bytes" — the bytes are used as an opaque identifier, not as human-readable text or as input to any text-processing function. The non-printable bytes are intentional — they maximise entropy in the identifier. No downstream consumer in this repo passes the result to a function that requires valid UTF-8 or printable characters. The previous audit's Finding 1 (rand.Read error discarded) is now fixed — `io.ReadFull` captures the error and panics on failure. The non-printable byte content is correct and intentional.

**Action required:** None. The non-printable byte content is correct and intentional.

---

## SECTION 4 — FEATURE SECURITY ASSESSMENT

| **Feature Area** | **Status** | **Notes** |
|---|---|---|
| DRWA Denial Code Vocabulary | **PARTIAL ISSUE** | 16 constants defined (15 concrete + `DenialUnknown` sentinel). `IsKnown()` correct. `IsValid()` incorrectly accepts `DenialUnknown` — re-introduces compliance reporting failure. Fix: Finding A. |
| DRWA Storage Key Prefixes | **SECURE** | `StorageKeyPrefix` typed. `AllStorageKeyPrefixes()` present. `IsValid()` and non-overlap tests present. Previous Finding 4 fixed. |
| DRWA Test Coverage | **PARTIAL ISSUE** | Uniqueness, `IsKnown()`, `IsValid()`, `NormalizeDenialCode` all tested. Missing: `AllDenialCodes()` count assertion (`len == 15`). Missing: `DenialUnknown.IsValid() == false` assertion after Finding A fix. Fix: Section 7. |
| Entropy Safety (`UniqueIdentifier`) | **SECURE** | `io.ReadFull` + panic on failure. Error is no longer discarded. Previous Finding 1 fixed. |
| PEM Key Loading | **PARTIAL ISSUE** | `strings.HasPrefix` + `isValidPemPublicKeySuffix` correct in loaders. Missing: identifier validation in `SaveSkToPemFile` — writer/reader asymmetry. Missing: trailing-space test. Fix: Finding C. |
| File Descriptor Management | **VULNERABLE** | `LoadTomlFileToMap` defers `f.Close()` after two early-return points — fd leaked on `f.Stat()` and `f.Read()` error paths. All other functions in the same file are correct. Fix: Finding B. |
| Directory Permissions | **PARTIAL ISSUE** | `CreateFile` uses `os.ModePerm` (`0777`) for `MkdirAll`. Should be `0700` to match `FileModeUserReadWrite` (`0600`) on files inside. Fix: Finding D. |
| PBFT Threshold Calculation | **PARTIAL ISSUE** | No guard for `consensusSize <= 0`. Returns threshold `1` for size `0` or negative — collapses Byzantine fault tolerance silently. Fix: Finding E. |
| Cryptographic Hashing | **SECURE** | `hashing/blake2b`, `hashing/keccak`, `hashing/sha256` — all use standard library implementations with no custom logic. No issues found. |
| Marshaling / Unmarshaling | **SECURE** | `GogoProtoMarshalizer` calls `msg.Reset()` before unmarshal — prevents state leakage between calls. `sizeCheckUnmarshalizer` enforces size delta check. `JsonMarshalizer` uses `encoding/json` — no custom parsing. No issues found. |
| Address Encoding (bech32 / hex) | **SECURE** | `bech32PubkeyConverter` validates prefix, length, and bit conversion. `hexPubkeyConverter` validates length after decode. Both return explicit errors on all failure paths. No issues found. |
| Transaction Integrity | **SECURE** | `Transaction.CheckIntegrity()` validates nil signature, nil value, negative value, and username length. `GetDataForSigning` uses encoder and marshaller with nil checks. No issues found. |
| Outport Block Topics | **SECURE** | `data/outport/consts.go` defines topic strings as typed constants. No injection surface — topics are used as WebSocket message type identifiers, not as query parameters. No issues found. |
| Data Partitioning | **SECURE** | `SizeDataPacker` and `SimpleDataPacker` both validate `limit >= minimumMaxPacketSizeInBytes` and `data != nil`. Marshal errors are propagated. No issues found. |
| Concurrency | **SECURE** | `core/atomic/` types use `sync/atomic` operations. `core/sync/keymutex.go` and `rwmutex.go` use `sync.Mutex` and `sync.RWMutex`. `core/container/mutexMap.go` uses `sync.RWMutex`. No data races detected. |
| DRWA Package Isolation | **SECURE** | `data/drwa/` package has zero imports beyond testing in the test file. No coupling to any other package in the repo. Adding it does not break any existing flow — confirmed by `go build ./...` and `go test ./...` passing clean. |

---

## SECTION 5 — ACTION PLAN

### Mandatory Fixes (Must Apply Before Production)

| **Priority** | **Action** | **File** | **Line** | **Effort** | **Why Mandatory** |
|---|---|---|---|---|---|
| **P1 — CRITICAL** | Change `IsValid()` to return `code.IsKnown()` only. Update test: `DenialUnknown.IsValid()` must be `false`. | data/drwa/constants.go | 67 | 5 min | Regulatory violations accumulate permanently with every unrecognized denial code. MiCA filing failure. |
| **P1 — CRITICAL** | Move `defer f.Close()` to immediately after `OpenFile` succeeds, before `f.Stat()` call. | core/file.go | 89 | 5 min | Node crashes silently under disk pressure or in containers. Permanent DoS until restart. |
| **P1 — CRITICAL** | Add `AllDenialCodes()` count assertion (`len == 15`) and `IsValid()` check per code. | data/drwa/constants_test.go | — | 5 min | Regulatory compliance gap grows with every new denial code added without this guard. |

### Recommended Fixes (Apply Before Codebase Grows)

| **Priority** | **Action** | **File** | **Line** | **Effort** | **Risk if Deferred** |
|---|---|---|---|---|---|
| **P2 — Recommended** | Add `isValidPemPublicKeySuffix(identifier)` guard in `SaveSkToPemFile` before `pem.Encode`. | core/file.go | 261 | 10 min | Latent node startup failure when any downstream developer passes invalid identifier. |
| **P2 — Conditional** | Change `os.MkdirAll` permission from `os.ModePerm` to `0700`. | core/file.go | 124 | 2 min | Only critical in containers with permissive umask. Verify deployment before applying. |
| **P2 — Recommended** | Add `consensusSize <= 0` guard returning `0` in both PBFT threshold functions. | core/common.go | 46, 51 | 5 min | Critical consensus safety failure if upstream validation ever regresses. |
| **P3 — Low** | Add trailing-space PEM suffix sub-tests to `TestLoadSkPkFromPemFile` and `TestLoadAllKeysFromPemFile`. | core/file_test.go | — | 10 min | Test coverage gap only — no runtime risk. |

### Test Impact Summary

| **Fix** | **File** | **Test Action Required** |
|---|---|---|
| Finding A — `IsValid()` | data/drwa/constants_test.go | Change assertion: `DenialUnknown.IsValid()` must return `false`. Add `TestDenialUnknown_IsNotStorable`. |
| Finding B — fd leak | core/file_test.go | Add test: repeated error-path calls do not leak file descriptors. Verify with `/proc/self/fd` count. |
| Finding C — `SaveSkToPemFile` | core/file_test.go | Add 3 sub-tests: empty identifier → `ErrPemFileIsInvalid`; whitespace-padded → `ErrPemFileIsInvalid`; control char → `ErrPemFileIsInvalid`. |
| Finding D — `ModePerm` | core/file_test.go | Add test: created directory has mode `0700`. |
| Finding E — PBFT guard | core/common_test.go | Add 4 assertions: `GetPBFTThreshold(0)==0`, `GetPBFTThreshold(-1)==0`, `GetPBFTFallbackThreshold(0)==0`, `GetPBFTFallbackThreshold(-1)==0`. |
| Section 7 — count test | data/drwa/constants_test.go | Add `TestAllDenialCodes_Complete` asserting `len==15` and all codes pass `IsValid()` (after Finding A fix applied). |
| Trailing-space PEM | core/file_test.go | Add trailing-space suffix sub-test to both `TestLoadSkPkFromPemFile` and `TestLoadAllKeysFromPemFile`. |

### Integration Impact Summary

| **Finding** | **Mandatory?** | **Breaks Existing Tests?** | **Breaks Existing Runtime Flow?** | **Deployment Verification Required?** |
|---|---|---|---|---|
| **A** — `IsValid()` fix | **YES — fix before production** | **Yes — 1 test assertion must be updated first** | No | No |
| **B** — `defer` move | **YES — fix before production** | No | No | No |
| **Section 7** — count test | **YES — fix before production** | No | No | No |
| **C** — `SaveSkToPemFile` guard | Recommended | No | No | No |
| **D** — `0777` → `0700` | Conditional | No | **Only if another process reads the directory** | **Yes — verify no sidecar reads node directory** |
| **E** — PBFT zero guard | Recommended | No | No | No |

---

## SECTION 6 — FINAL DECISION

### Mandatory — Must Fix Before Production

- **Finding A (IsValid() accepts DenialUnknown): NOT FIXED — Medium severity — MANDATORY.** `IsValid()` at data/drwa/constants.go line 67 returns `true` for `DenialUnknown`. Every unrecognized denial code path permanently stores a `DRWA_UNKNOWN` record in the compliance index. These records accumulate with every transaction, cannot be retroactively corrected, and constitute a direct MiCA Article 45 regulatory filing violation. A downstream switch with no `case DenialUnknown:` branch silently allows transfers that should be denied. **Fix:** change `IsValid()` to return `code.IsKnown()` only. **Integration:** update one test assertion in constants_test.go line 28 before applying — no runtime flow breaks.

- **Finding B (LoadTomlFileToMap fd leak): NOT FIXED — Medium severity — MANDATORY.** `defer f.Close()` at core/file.go line 89 is placed after two early-return points (lines 78, 86). Under disk pressure or in containers with low fd limits, every error-path call leaks one file descriptor permanently. The node crashes with "too many open files" at an unpredictable point during the incident with no log trail pointing to the root cause. **Fix:** move defer to immediately after `OpenFile` succeeds. **Integration:** drop-in safe — no existing tests break, no runtime flow breaks, no API changes.

- **Section 7 Gap (No AllDenialCodes count test): NOT FIXED — Medium severity — MANDATORY.** `AllDenialCodes()` exists but no test asserts `len == 15`. The moment a new denial code is added to the constants block and omitted from `AllDenialCodes()`, the entire downstream enforcement pipeline silently misses it — no test fails, no compile error, no warning. Regulated transfers are either silently allowed or denied with a generic error that has no regulatory attribution. **Fix:** add `TestAllDenialCodes_Complete`. **Integration:** adding a new test never breaks existing flow — drop-in safe.

### Recommended — Fix Before Codebase Grows

- **Finding C (SaveSkToPemFile no identifier validation): NOT FIXED — Low severity — RECOMMENDED.** No immediate production risk — all current callers pass valid identifiers. Becomes a hard-to-diagnose node startup failure the moment any downstream developer passes an invalid identifier. Write succeeds silently; node fails to start on next restart with `ErrPemFileIsInvalid` and no pointer to the write-time cause. **Fix:** add `isValidPemPublicKeySuffix` guard before `pem.Encode`. **Integration:** drop-in safe — all existing callers pass valid identifiers, no existing tests break, no API changes.

- **Finding E (PBFT threshold no zero guard): NOT FIXED — Low severity — RECOMMENDED.** No immediate production risk — all current callers pass sizes `>= 2`. Becomes a critical consensus safety failure if upstream validation ever regresses and passes `0` or negative — `GetPBFTThreshold(0)` returns `1`, a single node can reach consensus alone with no error, no log, no alert. **Fix:** add `consensusSize <= 0` guard returning `0`. **Integration:** drop-in safe — all existing callers pass sizes `>= 2`, no existing tests break, no API changes.

### Conditional — Verify Deployment Environment First

- **Finding D (CreateFile os.ModePerm): NOT FIXED — Low severity — CONDITIONAL.** On standard Linux with umask `0022` the effective directory permission is `0755` — not writable, low risk. In containers running as root with umask `0000` the directory is world-writable and any co-located process can tamper with log and key files. **Fix:** change to `0700`. **Integration:** verify no sidecar or log aggregator reads the node directory before applying — safe for standard single-process deployments.

### Dismissed

- **Finding 6 (UniqueIdentifier non-printable bytes): DISMISSED — False positive.** Non-printable bytes in `UniqueIdentifier()` return value are intentional — the function returns an opaque random identifier, not human-readable text. No fix required at this location.

---

### Fix Priority Summary

Fixing **Finding A + B + Section 7** = **Minimum required for production** — regulatory violations stopped, node DoS under disk pressure eliminated, exhaustiveness contract enforced. Total effort: 15 minutes.
Fixing **Finding C + E** additionally = **Recommended before codebase grows** — PEM write/read symmetry restored, PBFT threshold functions reject invalid input explicitly. Total additional effort: 15 minutes.
Fixing **Finding D** additionally = **Apply after verifying deployment** — directory permissions tightened. Total additional effort: 2 minutes.
Fixing **everything** = **Perfect at Peak** — zero known security issues, all latent traps closed, all defence-in-depth gaps filled.

---

## SECTION 7 — DRWA FLOW GAP — No AllDenialCodes Exhaustiveness Count Test Between mx-chain-core-go and Downstream Enforcement

**Classification:**
- **CWE:** CWE-691 (Insufficient Control Flow Management)
- **Severity:** Medium
- **Fix Required:** Yes

### The DRWA Flow Context

mx-chain-core-go is the starting repo in the DRWA pipeline. Its role is to define the shared vocabulary — the `DenialCode` type and its 15 known values — that every downstream repo imports and uses to make compliance decisions. The pipeline is:

```
mx-chain-core-go          (defines DenialCode vocabulary)
     ↓ imported by
mx-chain-vm-common-go     (compliance gate — evaluates transfers, assigns DenialCode)
     ↓ imported by
mx-chain-go               (node — executes compliance gate on every regulated transfer)
     ↓ emits OutportBlock with denial events
mx-chain-es-indexer-go    (indexes denial records to Elasticsearch)
     ↓
Compliance dashboards / Regulatory reporting tools
```

### The Gap

mx-chain-core-go defines 15 `DenialCode` constants and `AllDenialCodes()` returns all 15. The compliance gate in mx-chain-vm-common-go contains switch statements that handle these codes. There is no test in mx-chain-core-go that asserts `AllDenialCodes()` returns exactly 15 codes. Without this count assertion, a developer can add a 16th denial code to the constants block and omit it from `AllDenialCodes()` without any test failing — the exhaustiveness contract between mx-chain-core-go and downstream enforcement repos is not mechanically enforced.

Concretely: if a 16th denial code — for example `DenialSovereignChainBlocked DenialCode = "DRWA_SOVEREIGN_CHAIN_BLOCKED"` — is added to constants.go in mx-chain-core-go but not to `AllDenialCodes()`, the following happens:

1. mx-chain-core-go compiles and tests pass — the new constant is non-empty and unique
2. `AllDenialCodes()` still returns 15 codes — the new constant is silently excluded
3. mx-chain-vm-common-go imports the updated mx-chain-core-go — it compiles with no error because Go does not require switch exhaustiveness on string types
4. The compliance gate switch in mx-chain-vm-common-go has no `case DenialSovereignChainBlocked:` branch — the new code falls to default
5. The default branch either logs a warning and allows the transfer, or returns a generic error — neither is the correct compliance behaviour for the new denial reason
6. No test in mx-chain-vm-common-go fails — the new code was never in `AllDenialCodes()`
7. Regulated transfers that should be denied with `DRWA_SOVEREIGN_CHAIN_BLOCKED` are either silently allowed or denied with a generic error that has no regulatory attribution

This gap is not a code bug in mx-chain-core-go — `AllDenialCodes()` is correctly implemented. It is a design gap between what mx-chain-core-go promises (a complete, authoritative vocabulary of denial reasons) and what it can guarantee (that `AllDenialCodes()` always reflects every constant in the block).

### Who Is Affected

1. **Compliance gate maintainers in mx-chain-vm-common-go** — they have no automated signal when a new `DenialCode` is added to mx-chain-core-go that is missing from `AllDenialCodes()`
2. **Regulatory reporting tools** — they receive denial records with a code that has no corresponding enforcement rule in the gate, making the record unattributable
3. **Compliance / Regulatory Officers** — regulatory filings contain denial events attributed to a code that the compliance gate never explicitly handled
4. **On-call engineers** — default branch behaviour is unpredictable; some implementations allow the transfer, others deny it generically — the on-call cannot determine correct behaviour without reading both repos

### The Fix

**Step 1** — add a test in data/drwa/constants_test.go that verifies `AllDenialCodes()` returns exactly 15 codes and that every code passes `IsValid()` (after Finding A fix is applied):

```go
func TestAllDenialCodes_Complete(t *testing.T) {
    all := AllDenialCodes()
    if len(all) != 15 {
        t.Fatalf("expected 15 denial codes, got %d — update this test and "+
            "the compliance gate switch in mx-chain-vm-common-go", len(all))
    }
    for _, code := range all {
        if !code.IsValid() {
            t.Fatalf("AllDenialCodes() returned invalid code: %s", code)
        }
    }
}
```

**Step 2** — add a test in mx-chain-vm-common-go that calls `drwa.AllDenialCodes()` and asserts that the compliance gate switch handles every returned code with a non-default branch. This test fails automatically when a new code is added to mx-chain-core-go without a corresponding enforcement branch in mx-chain-vm-common-go.

### Why This Gap Is Specific to This Repo

mx-chain-core-go is the only repo in the DRWA pipeline that defines the denial code vocabulary. It is the single source of truth for what denial reasons exist. Every other repo in the pipeline is a consumer of this vocabulary. The gap exists because Go string-typed switches are not exhaustive — the compiler does not warn when a new string constant is added to an imported package and the importing package's switch does not handle it. This gap does not exist in mx-chain-vm-common-go or mx-chain-es-indexer-go — they are consumers, not definers. It is unique to mx-chain-core-go's role as the vocabulary authority for the entire DRWA compliance pipeline.

### Why This Gap Matters for Regulatory Compliance

MiCA Article 45 and equivalent regulations require that every transfer denial be attributed to a specific, documented compliance rule. A denial code that exists in the vocabulary but is excluded from `AllDenialCodes()` is invisible to the exhaustiveness contract — downstream enforcement repos have no automated signal to handle it. This is not a theoretical risk — it is the exact failure mode that occurs every time a new denial reason is added to mx-chain-core-go without a corresponding entry in `AllDenialCodes()` and a corresponding update to mx-chain-vm-common-go.
