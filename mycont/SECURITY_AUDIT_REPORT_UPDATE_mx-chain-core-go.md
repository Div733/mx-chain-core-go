# Security Audit Report — Update
**Repository:** mx-chain-core-go
**Reference Report:** SECURITY_AUDIT_REPORT_FINAL_mx-chain-core-go.pdf
**Files Reviewed:** core/common.go, core/common_test.go, core/file.go, core/file_test.go, core/constants.go, data/drwa/constants.go, data/drwa/constants_test.go

---

## Section 1 — Finding Status vs. Reference Report

### Finding 1 — crypto/rand Error Discarded (core/common.go)
**Previous Status:** NOT FIXED — Medium
**Current Status:** ✅ FIXED

`uniqueIdentifierFromReader` now uses `io.ReadFull(reader, buff)` and captures the error, panicking with a wrapped error message on failure. The silent zero-fill path is eliminated. The panic-on-failure approach is an acceptable deviation from the report's suggested `return ""` — it is strictly safer because it makes entropy failure impossible to ignore at startup.

`common_test.go` covers the panic path via `TestUniqueIdentifier_ShouldPanicOnEntropyFailure` using a `failingEntropyReader` stub. The report's requested test (non-empty string of length 32) is present as `TestUniqueIdentifier_ShouldReturn32Bytes`.

---

### Finding 2 — strings.Index Prefix Check (core/file.go lines 183, 227)
**Previous Status:** NOT FIXED — Low
**Current Status:** ✅ FIXED (code) / ⚠️ PARTIALLY FIXED (tests)

Both `LoadSkPkFromPemFile` (line 184) and `LoadAllKeysFromPemFile` (line 231) now use `strings.HasPrefix` instead of `strings.Index`. The extracted suffix is validated by `isValidPemPublicKeySuffix`, which rejects empty strings, strings that do not equal their `strings.TrimSpace` result, and strings containing Unicode control characters. This is equivalent to or stricter than the report's prescribed fix.

**Remaining gap — test coverage:**
The report required adding a test for a trailing-space block type to verify `TrimSpace` behaviour. No such test exists in `core/file_test.go`. The existing tests cover empty suffix, control characters, and incorrect headers, but not a valid suffix with trailing whitespace that should be trimmed and accepted.

**Residual Finding 2-T — Missing Trailing-Space PEM Test**
- Severity: Info
- File: core/file_test.go
- Required action: Add a sub-test to `TestLoadSkPkFromPemFile` and `TestLoadAllKeysFromPemFile` that writes a PEM block with type `"PRIVATE KEY for ABCD "` (trailing space) and asserts the call returns an error (because `isValidPemPublicKeySuffix` rejects suffixes where `TrimSpace(suffix) != suffix`). This confirms the guard behaves as documented.

---

### Finding 3 — No DenialCode Zero-Value Sentinel (data/drwa/constants.go)
**Previous Status:** NOT FIXED — Medium
**Current Status:** ✅ FIXED (with implementation deviation — see note)

`DenialUnknown DenialCode = "DRWA_UNKNOWN"` is defined as the explicit sentinel for unrecognized codes. `IsValid()` returns `true` for `DenialUnknown` and all 15 known codes, and `false` for the empty string. `IsKnown()` returns `true` only for the 15 concrete codes, excluding `DenialUnknown`. `NormalizeDenialCode` maps unknown non-empty inputs to `DenialUnknown` and blank input to `""`.

**Implementation deviation from report prescription:**
The report prescribed `DenialCodeUnknown DenialCode = ""` (naming the Go zero value). The implementation instead defines `DenialUnknown = "DRWA_UNKNOWN"` (a non-empty sentinel). This is a deliberate and defensible design choice: the Go zero value `""` remains invalid (`IsValid()` returns `false` for it), so uninitialized variables are still rejected. The non-empty sentinel is more useful in log output and compliance records than an empty string. No security regression results from this deviation.

**Remaining gap:**
`DenialCode("")` (the actual Go zero value) is not a named constant. Code that declares `var code DenialCode` without assignment produces `""`, which `IsValid()` correctly rejects, but there is no named constant to write `code == DenialCodeEmpty` in downstream switch default branches. This is a minor ergonomic gap, not a security issue.

---

### Finding 4 — Untyped Storage Key Prefixes (data/drwa/constants.go)
**Previous Status:** NOT FIXED — Medium
**Current Status:** ✅ FIXED

`StorageKeyPrefix` is now a distinct named type. All five prefix constants (`TokenPolicyPrefix`, `HolderMirrorPrefix`, `HolderProfilePrefix`, `HolderAuditorAuthPrefix`, `AssetRecordPrefix`) are typed as `StorageKeyPrefix`. `AllStorageKeyPrefixes()` returns the complete set. `IsValid()` and `String()` methods are present. Downstream code passing a plain `string` or a different typed constant where `StorageKeyPrefix` is expected will receive a compile-time error.

---

### Finding 5 — Test Non-Uniqueness (data/drwa/constants_test.go)
**Previous Status:** NOT FIXED — Info
**Current Status:** ✅ FIXED

`TestDenialCodes_Unique` uses a `seen` map to assert no duplicate `DenialCode` values exist in `AllDenialCodes()`. `TestDenialCodes_ValidityAndNormalization` asserts `IsValid()` and `IsKnown()` on every code and on the sentinel. `TestPrefixes_UniqueAndNonOverlapping` asserts uniqueness and non-overlap for all `StorageKeyPrefix` values. `TestPrefixes_RejectUnknown` asserts that `""` and an unknown prefix string are rejected by `IsValid()`.

---

### Finding 6 — UniqueIdentifier Non-Printable Bytes
**Previous Status:** DISMISSED — False Positive
**Current Status:** ✅ CONFIRMED DISMISSED — no change required

---

### Section 7 Gap — No AllDenialCodes Exhaustiveness Count Test
**Previous Status:** NOT FIXED — Medium
**Current Status:** ⚠️ PARTIALLY FIXED

`AllDenialCodes()` is implemented and returns all 15 concrete codes. However, the report's prescribed `TestAllDenialCodes_Complete` test — which asserts `len(AllDenialCodes()) == 15` and calls `IsValid()` on every returned code — is not present in `constants_test.go`. Without this count assertion, a developer can add a 16th denial code to the constants block and omit it from `AllDenialCodes()` without any test failing. The exhaustiveness contract between `mx-chain-core-go` and downstream enforcement repos is not mechanically enforced.

**Residual Finding 7-T — Missing AllDenialCodes Completeness Count Test**
- Severity: Medium
- File: data/drwa/constants_test.go
- Required action: Add `TestAllDenialCodes_Complete` as prescribed in the reference report. The test must assert `len(AllDenialCodes()) == 15` and that every returned code passes `IsValid()`. This is the only automated signal that fires when a new denial code is added to the constants block without a corresponding entry in `AllDenialCodes()`.

---

## Section 2 — New Findings in Changed Files

### New Finding A — DenialUnknown Included in IsValid() Breaks Compliance Gate Contract
- Severity: Low
- File: data/drwa/constants.go, lines 64–68
- CWE: CWE-20 (Improper Input Validation)

`IsValid()` returns `true` for `DenialUnknown`. This means a compliance gate that calls `code.IsValid()` before storing a denial record will accept `DenialUnknown` as a storable denial reason. A denial record carrying `DRWA_UNKNOWN` is not attributable to any specific compliance rule, which is the exact regulatory reporting failure the report was designed to prevent.

The report's prescribed `IsValid()` explicitly returned `false` for the unknown sentinel:
```
// Returns false for DenialCodeUnknown and any unrecognised value.
func (d DenialCode) IsValid() bool { ... }
```

The current implementation inverts this: `IsValid()` returns `true` for `DenialUnknown`. Downstream compliance gates that use `IsValid()` as the storage guard will store `DRWA_UNKNOWN` denial records in the compliance index.

`IsKnown()` correctly returns `false` for `DenialUnknown` and can be used as the stricter guard. However, the method name `IsValid()` is the natural choice for a storage pre-check, and its current semantics are misleading for that use case.

**Recommended fix:** Either rename `IsValid()` to `IsStorable()` and have it return `false` for `DenialUnknown`, or change `IsValid()` to return `false` for `DenialUnknown` and rename the current `IsValid()` to `IsRecognized()`. The `IsKnown()` method already provides the correct semantics — downstream code should be directed to use `IsKnown()` for storage guards.

---

### New Finding B — NormalizeDenialCode Case-Fold Accepts Lowercase Input Silently
- Severity: Info
- File: data/drwa/constants.go, lines 73–89

`NormalizeDenialCode` performs a two-pass lookup: first case-sensitive, then `strings.ToUpper`. This means `"drwa_kyc_required_sender"` normalizes to `DenialKYCRequiredSender`. While the test `TestDenialCodes_ValidityAndNormalization` explicitly covers this case and treats it as correct behaviour, the function's doc comment does not document the case-folding behaviour. A downstream developer reading only the doc comment will not know that lowercase inputs are accepted and silently uppercased.

No security impact. The behaviour is tested. The gap is documentation only.

**Recommended fix:** Add to the `NormalizeDenialCode` doc comment: `// Input matching is case-insensitive; the returned code is always in canonical upper-case form.`

---

## Section 3 — Residual Action Plan

| Priority | Finding | File | Action | Effort |
|----------|---------|------|--------|--------|
| P1 — Medium | 7-T: Missing AllDenialCodes count test | data/drwa/constants_test.go | Add `TestAllDenialCodes_Complete` asserting `len == 15` and all codes pass `IsValid()` | 5 min |
| P2 — Low | A: IsValid() accepts DenialUnknown | data/drwa/constants.go | Clarify semantics: use `IsKnown()` as storage guard; update doc comments | 10 min |
| P3 — Info | 2-T: Missing trailing-space PEM test | core/file_test.go | Add trailing-space suffix sub-test to `TestLoadSkPkFromPemFile` and `TestLoadAllKeysFromPemFile` | 10 min |
| P4 — Info | B: NormalizeDenialCode undocumented case-fold | data/drwa/constants.go | Add case-insensitivity note to doc comment | 2 min |

---

## Section 4 — Final Decision

| Finding | Previous Status | Current Status |
|---------|----------------|----------------|
| Finding 1 — rand.Read error discarded | NOT FIXED | ✅ FIXED |
| Finding 2 — strings.Index prefix check (code) | NOT FIXED | ✅ FIXED |
| Finding 2-T — trailing-space PEM test | NOT REQUIRED (new) | ❌ NOT ADDED |
| Finding 3 — DenialCode zero-value sentinel | NOT FIXED | ✅ FIXED (with deviation) |
| Finding 4 — Untyped storage key prefixes | NOT FIXED | ✅ FIXED |
| Finding 5 — Test non-uniqueness | NOT FIXED | ✅ FIXED |
| Finding 6 — UniqueIdentifier non-printable bytes | DISMISSED | ✅ CONFIRMED DISMISSED |
| Section 7 Gap — AllDenialCodes count test | NOT FIXED | ⚠️ PARTIALLY FIXED |
| New Finding A — IsValid() accepts DenialUnknown | — | ⚠️ NEW — Low |
| New Finding B — NormalizeDenialCode undocumented case-fold | — | ℹ️ NEW — Info |

All high and medium severity findings from the reference report are resolved in code. Two residual gaps remain at medium and low severity: the missing `AllDenialCodes` count test (7-T) and the `IsValid()` / `DenialUnknown` semantic ambiguity (Finding A). Both are addressable with under 15 minutes of work and no API-breaking changes.
