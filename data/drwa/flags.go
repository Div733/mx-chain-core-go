package drwa

import "github.com/multiversx/mx-chain-core-go/core"

// DRWAEnforcementFlag is the enable-epoch flag that activates the DRWA compliance
// gate on every regulated ESDT transfer. When this flag is disabled (epoch not yet
// reached), all ESDT transfers proceed without DRWA compliance checks — the gate
// code is present but dormant.
//
// This constant must be used by:
//   - mx-chain-vm-common-go: to check IsFlagEnabled(DRWAEnforcementFlag) in the gate
//   - mx-chain-go: to wire the flag into the epoch config (enableEpochs.toml) and
//     the enableEpochsHandler so the gate activates at the correct epoch
//
// Defining it here ensures both repos use the exact same string. A mismatch
// between the flag name in the gate and the flag name in the epoch config means
// the gate never activates — all regulated transfers pass unchecked.
const DRWAEnforcementFlag core.EnableEpochFlag = "DRWAEnforcementFlag"
