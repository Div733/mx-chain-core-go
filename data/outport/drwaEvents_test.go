package outport

import (
	"encoding/json"
	"testing"
)

func TestDrwaTopics_AreNonEmpty(t *testing.T) {
	topics := []string{
		TopicDrwaGateDenial,
		TopicDrwaPolicyUpdate,
		TopicDrwaHolderUpdate,
	}
	for _, topic := range topics {
		if topic == "" {
			t.Fatal("DRWA topic must not be empty")
		}
	}
}

func TestDrwaTopics_AreDistinct(t *testing.T) {
	topics := []string{
		TopicDrwaGateDenial,
		TopicDrwaPolicyUpdate,
		TopicDrwaHolderUpdate,
	}
	seen := make(map[string]struct{})
	for _, topic := range topics {
		if _, exists := seen[topic]; exists {
			t.Fatalf("duplicate DRWA topic: %s", topic)
		}
		seen[topic] = struct{}{}
	}
}

func TestDrwaTopics_DoNotCollideWithExistingTopics(t *testing.T) {
	existing := []string{
		TopicSaveBlock,
		TopicRevertIndexedBlock,
		TopicSaveRoundsInfo,
		TopicSaveValidatorsPubKeys,
		TopicSaveValidatorsRating,
		TopicSaveAccounts,
		TopicFinalizedBlock,
		TopicSettings,
	}
	drwa := []string{
		TopicDrwaGateDenial,
		TopicDrwaPolicyUpdate,
		TopicDrwaHolderUpdate,
	}
	for _, d := range drwa {
		for _, e := range existing {
			if d == e {
				t.Fatalf("DRWA topic %q collides with existing topic %q", d, e)
			}
		}
	}
}

func TestDrwaGateDenialEvent_JSONRoundTrip(t *testing.T) {
	original := DrwaGateDenialEvent{
		TokenID:      "CARBON-abc123",
		SenderAddr:   "erd1sender",
		ReceiverAddr: "erd1receiver",
		DenialCode:   "DRWA_KYC_REQUIRED_SENDER",
		TxHash:       "deadbeef",
		Timestamp:    1735689600,
	}
	data, err := json.Marshal(original)
	if err != nil {
		t.Fatalf("marshal failed: %v", err)
	}
	var recovered DrwaGateDenialEvent
	if err = json.Unmarshal(data, &recovered); err != nil {
		t.Fatalf("unmarshal failed: %v", err)
	}
	if original != recovered {
		t.Fatalf("round-trip mismatch: got %+v want %+v", recovered, original)
	}
}

func TestDrwaPolicyUpdateEvent_JSONRoundTrip(t *testing.T) {
	original := DrwaPolicyUpdateEvent{
		TokenID:   "CARBON-abc123",
		TxHash:    "cafebabe",
		Timestamp: 1735689600,
	}
	data, err := json.Marshal(original)
	if err != nil {
		t.Fatalf("marshal failed: %v", err)
	}
	var recovered DrwaPolicyUpdateEvent
	if err = json.Unmarshal(data, &recovered); err != nil {
		t.Fatalf("unmarshal failed: %v", err)
	}
	if original != recovered {
		t.Fatalf("round-trip mismatch: got %+v want %+v", recovered, original)
	}
}

func TestDrwaHolderUpdateEvent_TokenIDOmitempty(t *testing.T) {
	// global profile update — TokenID should be absent from JSON
	global := DrwaHolderUpdateEvent{
		HolderAddr: "erd1holder",
		TxHash:     "aabbccdd",
		Timestamp:  1735689600,
	}
	data, err := json.Marshal(global)
	if err != nil {
		t.Fatalf("marshal failed: %v", err)
	}
	var m map[string]interface{}
	if err = json.Unmarshal(data, &m); err != nil {
		t.Fatalf("unmarshal to map failed: %v", err)
	}
	if _, exists := m["tokenID"]; exists {
		t.Fatal("tokenID must be absent from JSON when empty (omitempty)")
	}

	// per-token mirror update — TokenID must be present
	perToken := DrwaHolderUpdateEvent{
		HolderAddr: "erd1holder",
		TokenID:    "CARBON-abc123",
		TxHash:     "aabbccdd",
		Timestamp:  1735689600,
	}
	data, err = json.Marshal(perToken)
	if err != nil {
		t.Fatalf("marshal failed: %v", err)
	}
	if err = json.Unmarshal(data, &m); err != nil {
		t.Fatalf("unmarshal to map failed: %v", err)
	}
	if _, exists := m["tokenID"]; !exists {
		t.Fatal("tokenID must be present in JSON when set")
	}
}
