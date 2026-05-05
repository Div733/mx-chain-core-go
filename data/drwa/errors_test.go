package drwa

import (
	"errors"
	"fmt"
	"testing"
)

func TestErrorSentinels_AreNonNil(t *testing.T) {
	sentinels := []error{
		ErrTokenPolicyNotFound,
		ErrHolderProfileNotFound,
		ErrHolderMirrorNotFound,
		ErrAuditorAuthNotFound,
		ErrAssetRecordNotFound,
		ErrAuditorAuthExpired,
		ErrKYCExpired,
		ErrNilTokenPolicy,
		ErrNilHolderProfile,
		ErrInvalidSyncEnvelope,
		ErrSyncHashMismatch,
	}
	for _, sentinel := range sentinels {
		if sentinel == nil {
			t.Fatalf("sentinel must not be nil")
		}
	}
}

func TestErrorSentinels_AreDistinct(t *testing.T) {
	sentinels := []error{
		ErrTokenPolicyNotFound,
		ErrHolderProfileNotFound,
		ErrHolderMirrorNotFound,
		ErrAuditorAuthNotFound,
		ErrAssetRecordNotFound,
		ErrAuditorAuthExpired,
		ErrKYCExpired,
		ErrNilTokenPolicy,
		ErrNilHolderProfile,
		ErrInvalidSyncEnvelope,
		ErrSyncHashMismatch,
	}
	for i := 0; i < len(sentinels); i++ {
		for j := i + 1; j < len(sentinels); j++ {
			if errors.Is(sentinels[i], sentinels[j]) {
				t.Fatalf("sentinels[%d] and sentinels[%d] must be distinct", i, j)
			}
		}
	}
}

func TestErrorSentinels_ErrorsIsWorksAcrossWrapping(t *testing.T) {
	wrapped := fmt.Errorf("mirror read failed: %w", ErrTokenPolicyNotFound)
	if !errors.Is(wrapped, ErrTokenPolicyNotFound) {
		t.Fatal("errors.Is must find ErrTokenPolicyNotFound through wrapping")
	}

	doubleWrapped := fmt.Errorf("outer: %w", fmt.Errorf("inner: %w", ErrSyncHashMismatch))
	if !errors.Is(doubleWrapped, ErrSyncHashMismatch) {
		t.Fatal("errors.Is must find ErrSyncHashMismatch through double wrapping")
	}
}

func TestErrorSentinels_DoNotMatchEachOtherWhenWrapped(t *testing.T) {
	wrapped := fmt.Errorf("mirror read failed: %w", ErrTokenPolicyNotFound)
	if errors.Is(wrapped, ErrHolderProfileNotFound) {
		t.Fatal("wrapped ErrTokenPolicyNotFound must not match ErrHolderProfileNotFound")
	}
}
