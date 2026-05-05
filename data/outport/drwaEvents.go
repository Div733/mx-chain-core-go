package outport

// DrwaGateDenialEvent is emitted on TopicDrwaGateDenial whenever the DRWA
// enforcement gate blocks a regulated ESDT transfer. It provides the full
// audit trail required for compliance dashboards and regulatory reporting.
type DrwaGateDenialEvent struct {
	// TokenID is the ESDT token identifier of the regulated token.
	TokenID string `json:"tokenID"`
	// SenderAddr is the bech32-encoded address of the transfer sender.
	SenderAddr string `json:"senderAddr"`
	// ReceiverAddr is the bech32-encoded address of the transfer receiver.
	ReceiverAddr string `json:"receiverAddr"`
	// DenialCode is the canonical DRWA denial code string (e.g. "DRWA_KYC_REQUIRED_SENDER").
	// Always matches one of the DenialCode constants in data/drwa/constants.go.
	DenialCode string `json:"denialCode"`
	// TxHash is the hex-encoded hash of the transaction that was denied.
	TxHash string `json:"txHash"`
	// Timestamp is the block timestamp (Unix seconds) when the denial occurred.
	Timestamp uint64 `json:"timestamp"`
}

// DrwaPolicyUpdateEvent is emitted on TopicDrwaPolicyUpdate whenever a token
// policy is written to the native mirror via the sync hook. Consumers use this
// to invalidate cached policy state and record policy change history.
type DrwaPolicyUpdateEvent struct {
	// TokenID is the ESDT token identifier whose policy was updated.
	TokenID string `json:"tokenID"`
	// TxHash is the hex-encoded hash of the transaction that triggered the sync.
	TxHash string `json:"txHash"`
	// Timestamp is the block timestamp (Unix seconds) when the update occurred.
	Timestamp uint64 `json:"timestamp"`
}

// DrwaHolderUpdateEvent is emitted on TopicDrwaHolderUpdate whenever a holder
// mirror or holder profile is written to the native mirror via the sync hook.
// TokenID is omitempty — it is empty when a global profile update applies to
// all tokens, and set when a per-token mirror entry is updated.
type DrwaHolderUpdateEvent struct {
	// HolderAddr is the bech32-encoded address of the holder whose record changed.
	HolderAddr string `json:"holderAddr"`
	// TokenID is the ESDT token identifier for per-token mirror updates.
	// Empty for global profile updates (identity-registry writes).
	TokenID string `json:"tokenID,omitempty"`
	// TxHash is the hex-encoded hash of the transaction that triggered the sync.
	TxHash string `json:"txHash"`
	// Timestamp is the block timestamp (Unix seconds) when the update occurred.
	Timestamp uint64 `json:"timestamp"`
}
