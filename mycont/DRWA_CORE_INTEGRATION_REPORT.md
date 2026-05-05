# mx-chain-core-go — DRWA Integration Report

**Repo:** `/home/divesh/Desktop/RWA/right/core/mx-chain-core-go`
**Date:** 2026
**Build status:** `go build ./...` — PASS
**Test status:** `go test ./...` — ALL 45 PACKAGES PASS

---

## Section 1 — What This Repo Is

`mx-chain-core-go` is the shared primitives library for the entire Dharitri
ecosystem. Every other repo in the stack imports it. Nothing imports it from
below — it sits at the very bottom of the dependency chain.

```
mx-chain-core-go          ← THIS REPO — shared types, no upstream deps
       ↓ imported by
mx-chain-vm-common-go     ← VM, DRWA gate (15 compliance checks)
       ↓ imported by
mx-chain-go               ← full node, sync adapter, native mirror
       ↓ imported by
mx-sdk-go                 ← Go SDK
       ↓ imported by
mx-chain-es-indexer-go    ← Elasticsearch indexer
mx-chain-notifier-go      ← event push service
mx-api-service            ← REST API
```

Its job is to define types, constants, and errors that every layer above it
needs — without pulling in any of their logic. It is the shared language of
the system. If a string, a type, or an error needs to be used by more than
one repo, it belongs here.

---

## Section 2 — What Was in the Repo Before We Touched It

### `data/drwa/` — 2 files

**`constants.go`** — already existed, already well-built:
- `DenialCode` typed string alias for the 15 denial codes
- `DenialUnknown` sentinel for unknown/unrecognized codes
- `knownDenialCodes` map for O(1) lookup
- `AllDenialCodes()` — stable-order slice of all 15 codes
- `IsKnown()` and `IsValid()` methods on `DenialCode`
- `NormalizeDenialCode()` — canonicalizes raw strings, case-insensitive,
  maps unknown values to `DenialUnknown` instead of leaking arbitrary strings
- `StorageKeyPrefix` typed string alias
- **5** storage key prefix constants (`drwa:token:`, `drwa:holder:`, etc.)
- `AllStorageKeyPrefixes()` — stable-order slice
- `IsValid()` method on `StorageKeyPrefix`

**`constants_test.go`** — already existed, already thorough:
- Tests denial codes are non-empty and unique
- Tests `IsKnown()`, `IsValid()`, `NormalizeDenialCode()` including edge cases
- Tests prefixes are non-empty, unique, non-overlapping, and reject unknowns

### `data/outport/` — no DRWA content

`consts.go` had 8 existing topic constants for block/account/validator events.
No DRWA topics. No DRWA event structs.

### What was missing before we started

| Missing piece | Impact |
|---|---|
| Typed error sentinels | SDK and indexer used string matching — fragile, breaks on wrapping |
| DRWA outport topic constants | Gate denials invisible to indexers and dashboards |
| DRWA outport event structs | No typed payload for compliance audit trail |
| `ActiveMarkerPrefix` (`drwa:active:`) | 6th storage prefix was a private string in vm-common — drift risk for compliance escape prevention |
| `DRWAEnforcementFlag` | Epoch flag string was only in vm-common — mx-chain-go had no canonical reference, causing launch blocker F-1 |

---

## Section 3 — What We Did and Why (All 5 Changes)

### Change 1 — `data/drwa/errors.go` (new file)

**What:** 11 typed error sentinel variables using `errors.New()`.

```
ErrTokenPolicyNotFound    — no policy at drwa:token:<tokenID>:policy
ErrHolderProfileNotFound  — no profile at drwa:profile:<address>
ErrHolderMirrorNotFound   — no mirror at drwa:holder:<tokenID>:<address>
ErrAuditorAuthNotFound    — no auth at drwa:auditor:<tokenID>:<address>
ErrAssetRecordNotFound    — no record at drwa:asset:<tokenID>:record
ErrAuditorAuthExpired     — record exists but authorization has expired
ErrKYCExpired             — record exists but KYC has passed expiry round
ErrNilTokenPolicy         — nil *TokenPolicy passed to a function
ErrNilHolderProfile       — nil *HolderProfile passed to a function
ErrInvalidSyncEnvelope    — binary envelope from Rust contract is malformed
ErrSyncHashMismatch       — keccak256 hash in envelope does not match payload
```

**Why this was needed:**

Before this fix, the Go SDK (`mx-sdk-go/drwa/compliance.go`) had a 30-entry
string map to parse denial codes:

```go
var knownDenialCodes = map[string]string{
    "DRWA_KYC_REQUIRED": "kyc_required",
    "DRWA_TOKEN_PAUSED": "token_paused",
    // 28 more entries including legacy aliases that already drifted...
}
```

This map already had drift — it contained aliases like `DRWA_KYC_REQUIRED`
that don't match the canonical `DRWA_KYC_REQUIRED_SENDER` in core. String
matching also breaks silently when errors are wrapped:

```go
// FAILS when the error is wrapped with fmt.Errorf("%w", err)
strings.Contains(err.Error(), "DRWA_TOKEN_PAUSED")
```

With sentinels in core, any repo can now do:

```go
import coredrwa "github.com/multiversx/mx-chain-core-go/data/drwa"

if errors.Is(err, coredrwa.ErrTokenPolicyNotFound) {
    // works through any number of fmt.Errorf("%w", err) wrapping layers
}
```

`errors.Is()` unwraps the error chain automatically. It never produces false
positives. It never breaks when error messages change.

---

### Change 2 — `data/outport/consts.go` (modified)

**What:** Added 3 DRWA topic constants to the existing file.

```go
TopicDrwaGateDenial   = "DrwaGateDenial"
TopicDrwaPolicyUpdate = "DrwaPolicyUpdate"
TopicDrwaHolderUpdate = "DrwaHolderUpdate"
```

**Why this was needed:**

The outport system is how the Dharitri node streams block data to external
consumers. Topics are named channels. Before this fix there were no DRWA
topics, which meant:
- Gate denials were logged inside the node but never streamed out
- Compliance dashboards had no way to see why transfers were being blocked
- The indexer could only see DRWA events emitted by the Rust contracts —
  not protocol-level gate decisions
- For a regulated asset platform, audit trails for transfer denials are
  legally required — this was a regulatory gap

All 8 existing topics are untouched. No collisions.

---

### Change 3 — `data/outport/drwaEvents.go` (new file)

**What:** 3 typed event structs with JSON tags.

```go
DrwaGateDenialEvent   — TokenID, SenderAddr, ReceiverAddr, DenialCode, TxHash, Timestamp
DrwaPolicyUpdateEvent — TokenID, TxHash, Timestamp
DrwaHolderUpdateEvent — HolderAddr, TokenID (omitempty), TxHash, Timestamp
```

**Why this was needed:**

Topics alone are not enough. Without typed structs, the node would construct
ad-hoc JSON maps — untyped, untested, inconsistent between versions. With
typed structs in core, the node fills a struct and publishes it, the indexer
unmarshals into the same struct — one definition, no drift possible.

`TokenID` is `omitempty` on `DrwaHolderUpdateEvent` because the
`identity-registry` contract writes two kinds of holder updates: global
profile updates (KYC, AML, sanctions — no specific token) and per-token
mirror updates (transfer lock, auditor auth — specific token). One struct
covers both cases cleanly.

---

### Change 4 — `data/drwa/constants.go` (modified) — `ActiveMarkerPrefix` added

**What:** Added a 6th storage key prefix constant.

```go
ActiveMarkerPrefix StorageKeyPrefix = "drwa:active:"
```

Also added to `knownStoragePrefixes` map and `AllStorageKeyPrefixes()` slice.

**Why this was needed:**

This prefix is written to the system account when a token is first registered
as DRWA-regulated. It persists even if the token policy is later deleted or
corrupted. The gate reads it to prevent **compliance escape** — a token that
was once regulated cannot silently become unregulated by losing its policy
entry.

Before this fix, `"drwa:active:"` was a private string literal only in
`mx-chain-vm-common-go/builtInFunctions/drwa.go`:

```go
// private, not importable, not in core
drwaActivePrefix = "drwa:active:"
```

`mx-chain-go` had no canonical reference for this string. If the two repos
ever drifted on this string, compliance escape prevention would silently
break — regulated tokens could be transferred freely after their policy was
deleted. Now both repos import `coredrwa.ActiveMarkerPrefix` from one place.

---

### Change 5 — `data/drwa/flags.go` (new file) — `DRWAEnforcementFlag` added

**What:** One typed epoch flag constant.

```go
const DRWAEnforcementFlag core.EnableEpochFlag = "DRWAEnforcementFlag"
```

**Why this was needed:**

`DRWAEnforcementFlag` is the epoch flag that turns the entire DRWA gate on
or off. When this flag is disabled, all ESDT transfers proceed without any
compliance checks — the gate code is present but dormant.

Before this fix, the flag was defined only in `mx-chain-vm-common-go`:

```go
// only in vm-common — mx-chain-go had no reference to this string
DRWAEnforcementFlag core.EnableEpochFlag = "DRWAEnforcementFlag"
```

`mx-chain-go` needs this exact string to wire the flag into its epoch config
(`enableEpochs.toml`) and the `enableEpochsHandler`. Without that wiring,
`IsFlagEnabled(DRWAEnforcementFlag)` always returns false — the gate is dead
code. This was **launch blocker F-1** from the comprehensive audit:

> `DRWAEnforcementFlag` defined in VM but never wired from chain config.
> Runtime check always returns false → the 1163 lines of drwa.go are dead
> code in production.

`core.EnableEpochFlag` is a type defined in **this repo** (`core/epochFlags.go`).
The flag constant that uses that type belongs here too. Now both
`mx-chain-vm-common-go` (which checks it) and `mx-chain-go` (which wires it)
import from one place. A mismatch between the two is now impossible.

---

### Tests written

**`data/drwa/errors_test.go`** — 4 tests:
- All 11 sentinels are non-nil
- All 11 sentinels are distinct from each other
- `errors.Is()` finds a sentinel through single and double wrapping
- A wrapped sentinel does not match a different sentinel

**`data/drwa/flags_test.go`** — 5 tests:
- `DRWAEnforcementFlag` is non-empty
- `DRWAEnforcementFlag` string value matches `"DRWAEnforcementFlag"` exactly
- `ActiveMarkerPrefix` is in `AllStorageKeyPrefixes()`
- `ActiveMarkerPrefix` passes `IsValid()`
- `ActiveMarkerPrefix` does not overlap with any of the other 5 prefixes

**`data/outport/drwaEvents_test.go`** — 6 tests:
- All 3 DRWA topics are non-empty strings
- All 3 DRWA topics are distinct from each other
- All 3 DRWA topics do not collide with the 8 existing topics
- `DrwaGateDenialEvent` JSON round-trip is lossless
- `DrwaPolicyUpdateEvent` JSON round-trip is lossless
- `DrwaHolderUpdateEvent` `omitempty` behaviour — absent when empty, present when set

---

## Section 4 — Complete File Inventory After All Changes

```
data/drwa/
├── constants.go        ← MODIFIED — now has 6 prefixes (added ActiveMarkerPrefix)
├── constants_test.go   ← pre-existing, unchanged — 6 tests
├── errors.go           ← NEW — 11 typed error sentinels
├── errors_test.go      ← NEW — 4 tests
├── flags.go            ← NEW — DRWAEnforcementFlag
└── flags_test.go       ← NEW — 5 tests

data/outport/
├── consts.go           ← MODIFIED — added 3 DRWA topic constants
├── drwaEvents.go       ← NEW — 3 typed event structs
└── drwaEvents_test.go  ← NEW — 6 tests
```

Everything else in the repo is untouched.

---

## Section 5 — Test Results

```
go test ./...

ok  github.com/multiversx/mx-chain-core-go/data/drwa      0.003s  ← 15 tests
ok  github.com/multiversx/mx-chain-core-go/data/outport   0.005s  ← 10 tests
ok  [all 43 other packages]                                PASS
```

Zero failures. Zero regressions. All pre-existing tests still pass.
Total: 45 packages, all green.

---

## Section 6 — Is the Repo Now Complete for DRWA Integration?

### Yes. Here is the full status table.

| Item | Status | Notes |
|---|---|---|
| 15 denial codes | ✅ Complete | Typed, `IsKnown()`, `NormalizeDenialCode()`, `DenialUnknown` sentinel |
| 6 storage key prefixes | ✅ Complete | Includes `ActiveMarkerPrefix` — compliance escape prevention |
| `AllDenialCodes()` | ✅ Complete | Stable-order slice |
| `AllStorageKeyPrefixes()` | ✅ Complete | Stable-order slice, all 6 prefixes |
| 11 error sentinels | ✅ Complete | All mirror read, expiry, nil, and sync errors |
| 3 outport topic constants | ✅ Complete | Gate denial, policy update, holder update |
| 3 outport event structs | ✅ Complete | Typed, JSON-tagged, tested |
| `DRWAEnforcementFlag` | ✅ Complete | Typed `core.EnableEpochFlag` — unblocks F-1 wiring in mx-chain-go |
| Build | ✅ Clean | `go build ./...` — no errors |
| Tests | ✅ All pass | `go test ./...` — 45 packages, zero failures |

---

### What is NOT in this repo — and correctly so

| Item | Why it does not belong here |
|---|---|
| View structs (`drwaTokenPolicyView` etc.) | Gate-specific internals (`storedVersion`, pre-normalized maps). Live in `mx-chain-vm-common-go` next to the gate. |
| Binary decoders | Enforcement logic — belongs in the gate, not a shared types library |
| Protobuf schemas | Trie uses JSON-wrapped blobs. No schema needed here. |
| `GateVerdict` type | Gate returns errors today. Changing the interface touches every ESDT transfer path. Not a core concern. |
| Sync envelope types | Internal to `mx-chain-go` sync adapter. Not shared across repos. |
| Gas accounting | VM-specific. Belongs in `mx-chain-vm-common-go`. |

---

### Remaining gaps — all in downstream repos, not here

This repo has done everything it needs to do. The remaining work is in
downstream repos that need to consume what is now available here.

**Gap 1 — `mx-sdk-go`: still uses string matching**

`mx-sdk-go/drwa/compliance.go` still has its 30-entry `knownDenialCodes`
string map. The sentinels are now in core and importable. The SDK needs to
replace string matching with `errors.Is()` against `coredrwa.Err*` sentinels.

**Gap 2 — `mx-chain-go`: does not yet emit outport events**

`blockChainHook.go` does not yet call
`outportHandler.Publish(outport.TopicDrwaGateDenial, ...)` when the gate
denies a transfer. The topic constants and event structs are ready in core.
The wiring is the next step in `mx-chain-go`.

**Gap 3 — `mx-chain-go`: F-1 wiring still needs to be done**

`DRWAEnforcementFlag` is now in core. `mx-chain-go` still needs to:
1. Add `DRWAEnforcementEnableEpoch uint32` to `config/epochConfig.go`
2. Add the field to `cmd/node/config/enableEpochs.toml` with value `0`
3. Wire `coredrwa.DRWAEnforcementFlag` into the flag-to-epoch mapping
   in the enableEpochsHandler

This repo has provided the canonical flag constant. The wiring is in
`mx-chain-go`.

**Gap 4 — `mx-chain-vm-common-go`: startup panic still exists**

`drwa_sync_types.go` still has the `init()` panic that validates prefix
parity with `mx-chain-vm-common-go`. This panic exists because
`mx-chain-vm-common-go` re-exports the prefixes as its own constants.
The fix is to remove that re-export so both repos import directly from core.
That change is in `mx-chain-vm-common-go`.

---

## Section 7 — Next Steps (Downstream Repos)

In priority order:

| Step | Repo | What to do | Effort |
|---|---|---|---|
| 1 | `mx-chain-go` | Wire `coredrwa.DRWAEnforcementFlag` into epoch config — fixes launch blocker F-1 | Half a day |
| 2 | `mx-chain-vm-common-go` | Remove re-export of prefix constants. Import `coredrwa.ActiveMarkerPrefix` directly. | 1 hour |
| 3 | `mx-chain-go` | Remove `init()` panic in `drwa_sync_types.go` — no longer needed after step 2 | 15 minutes |
| 4 | `mx-chain-go` | Wire `outportHandler.Publish(outport.TopicDrwaGateDenial, ...)` in `blockChainHook.go` | Half a day |
| 5 | `mx-sdk-go` | Replace 30-entry string map in `compliance.go` with `errors.Is()` against core sentinels | Half a day |

None of these steps require any further changes to this repo.

**This repo is complete. It is the correct starting point for DRWA integration
across the entire Dharitri stack.**
