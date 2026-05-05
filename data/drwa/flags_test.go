package drwa

import (
	"strings"
	"testing"
)

func TestDRWAEnforcementFlag_NonEmpty(t *testing.T) {
	if DRWAEnforcementFlag == "" {
		t.Fatal("DRWAEnforcementFlag must not be empty")
	}
}

func TestDRWAEnforcementFlag_MatchesExpectedString(t *testing.T) {
	if string(DRWAEnforcementFlag) != "DRWAEnforcementFlag" {
		t.Fatalf("DRWAEnforcementFlag string value changed: got %q", DRWAEnforcementFlag)
	}
}

func TestActiveMarkerPrefix_IsInAllPrefixes(t *testing.T) {
	found := false
	for _, p := range AllStorageKeyPrefixes() {
		if p == ActiveMarkerPrefix {
			found = true
			break
		}
	}
	if !found {
		t.Fatal("ActiveMarkerPrefix must be in AllStorageKeyPrefixes()")
	}
}

func TestActiveMarkerPrefix_IsValid(t *testing.T) {
	if !ActiveMarkerPrefix.IsValid() {
		t.Fatal("ActiveMarkerPrefix must be valid")
	}
}

func TestActiveMarkerPrefix_DoesNotOverlapOtherPrefixes(t *testing.T) {
	active := ActiveMarkerPrefix.String()
	others := []StorageKeyPrefix{
		TokenPolicyPrefix,
		HolderMirrorPrefix,
		HolderProfilePrefix,
		HolderAuditorAuthPrefix,
		AssetRecordPrefix,
	}
	for _, other := range others {
		otherRaw := other.String()
		if strings.HasPrefix(active, otherRaw) || strings.HasPrefix(otherRaw, active) {
			t.Fatalf("ActiveMarkerPrefix %q overlaps with %q", active, otherRaw)
		}
	}
}
