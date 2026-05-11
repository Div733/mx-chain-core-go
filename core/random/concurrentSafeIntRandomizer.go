package random

import (
	"crypto/rand"
	"math/big"
)

// ConcurrentSafeIntRandomizer implements dataRetriever.IntRandomizer and can be accessed in a concurrent manner
type ConcurrentSafeIntRandomizer struct {
}

// Intn returns an int in [0, n) interval
func (csir *ConcurrentSafeIntRandomizer) Intn(n int) int {
	if n <= 0 {
		return 0
	}

	val, err := rand.Int(rand.Reader, big.NewInt(int64(n)))
	if err != nil {
		return 0
	}

	return int(val.Int64())
}

// IsInterfaceNil returns true if there is no value under the interface
func (csir *ConcurrentSafeIntRandomizer) IsInterfaceNil() bool {
	return csir == nil
}
