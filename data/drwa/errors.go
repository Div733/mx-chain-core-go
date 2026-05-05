package drwa

import "errors"

// Mirror read errors — returned when a compliance record is absent from the native mirror trie.
// Use errors.Is() to distinguish these from unexpected system errors.
var ErrTokenPolicyNotFound = errors.New("token policy not found in native mirror")

// ErrHolderProfileNotFound is returned when no holder profile exists at drwa:profile:<address>.
var ErrHolderProfileNotFound = errors.New("holder profile not found in native mirror")

// ErrHolderMirrorNotFound is returned when no holder mirror exists at drwa:holder:<tokenID>:<address>.
var ErrHolderMirrorNotFound = errors.New("holder mirror not found in native mirror")

// ErrAuditorAuthNotFound is returned when no auditor authorization exists at drwa:auditor:<tokenID>:<address>.
var ErrAuditorAuthNotFound = errors.New("auditor authorization not found in native mirror")

// ErrAssetRecordNotFound is returned when no asset record exists at drwa:asset:<tokenID>:record.
var ErrAssetRecordNotFound = errors.New("asset record not found in native mirror")

// Expiry errors — returned when a compliance record exists but has expired.
var ErrAuditorAuthExpired = errors.New("auditor authorization has expired")

// ErrKYCExpired is returned when a holder's KYC record has passed its expiry round.
var ErrKYCExpired = errors.New("KYC record has expired")

// Nil argument errors — returned when a required struct pointer is nil.
var ErrNilTokenPolicy = errors.New("nil token policy")

// ErrNilHolderProfile is returned when a nil *HolderProfile is passed to a function that requires it.
var ErrNilHolderProfile = errors.New("nil holder profile")

// Sync envelope errors — returned during sync hook processing.
var ErrInvalidSyncEnvelope = errors.New("invalid DRWA sync envelope")

// ErrSyncHashMismatch is returned when the keccak256 hash in the sync envelope
// does not match the computed hash of the payload. Indicates tampering or corruption.
var ErrSyncHashMismatch = errors.New("DRWA sync envelope hash mismatch")
