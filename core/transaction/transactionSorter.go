package transaction

import (
	"bytes"
	"errors"
	"sort"

	"github.com/multiversx/mx-chain-core-go/data"
	"github.com/multiversx/mx-chain-core-go/hashing"
)

// ErrInvalidAddressLength signals that the address length is invalid for XOR operation
var ErrInvalidAddressLength = errors.New("invalid address length for XOR operation")

// SortTransactionsBySenderAndNonceWithFrontRunningProtection - sorts the transactions by address and randomness source to protect from front running
func SortTransactionsBySenderAndNonceWithFrontRunningProtection(transactions []data.TransactionHandler, hasher hashing.Hasher, randomness []byte) {
	// make sure randomness is 32bytes and uniform
	randSeed := hasher.Compute(string(randomness))
	xoredAddresses := make(map[string][]byte)

	for _, tx := range transactions {
		xoredBytes, err := xorBytes(tx.GetSndAddr(), randSeed)
		if err != nil {
			continue
		}
		xoredAddresses[string(tx.GetSndAddr())] = hasher.Compute(string(xoredBytes))
	}

	sorter := func(i, j int) bool {
		txI := transactions[i]
		txJ := transactions[j]

		delta := bytes.Compare(xoredAddresses[string(txI.GetSndAddr())], xoredAddresses[string(txJ.GetSndAddr())])
		if delta == 0 {
			delta = int(txI.GetNonce()) - int(txJ.GetNonce())
		}

		return delta < 0
	}

	sort.Slice(transactions, sorter)
}

// TODO remove duplicated function when will use the version of mx-chain-go which exports transaction order during processing

// SortTransactionsBySenderAndNonceWithFrontRunningProtectionExtendedTransactions - sorts the transactions by address and randomness source to protect from front running
func SortTransactionsBySenderAndNonceWithFrontRunningProtectionExtendedTransactions(transactions []data.TxWithExecutionOrderHandler, hasher hashing.Hasher, randomness []byte) {
	// make sure randomness is 32bytes and uniform
	randSeed := hasher.Compute(string(randomness))
	xoredAddresses := make(map[string][]byte)

	for _, tx := range transactions {
		txHandler := tx.GetTxHandler()

		xoredBytes, err := xorBytes(txHandler.GetSndAddr(), randSeed)
		if err != nil {
			continue
		}
		xoredAddresses[string(txHandler.GetSndAddr())] = hasher.Compute(string(xoredBytes))
	}

	sorter := func(i, j int) bool {
		txI := transactions[i]
		txJ := transactions[j]
		txIHandler := txI.GetTxHandler()
		txJHandler := txJ.GetTxHandler()

		delta := bytes.Compare(xoredAddresses[string(txIHandler.GetSndAddr())], xoredAddresses[string(txJHandler.GetSndAddr())])
		if delta == 0 {
			delta = int(txIHandler.GetNonce()) - int(txJHandler.GetNonce())
		}

		return delta < 0
	}

	sort.Slice(transactions, sorter)
}

// SortTransactionsBySenderAndNonce - sorts the transactions by address without the front running protection
func SortTransactionsBySenderAndNonce(transactions []data.TransactionHandler) {
	sorter := func(i, j int) bool {
		txI := transactions[i]
		txJ := transactions[j]

		delta := bytes.Compare(txI.GetSndAddr(), txJ.GetSndAddr())
		if delta == 0 {
			delta = int(txI.GetNonce()) - int(txJ.GetNonce())
		}

		return delta < 0
	}

	sort.Slice(transactions, sorter)
}

// SortTransactionsBySenderAndNonceExtendedTransactions - sorts the transactions by address without the front running protection
func SortTransactionsBySenderAndNonceExtendedTransactions(transactions []data.TxWithExecutionOrderHandler) {
	sorter := func(i, j int) bool {
		txI := transactions[i]
		txJ := transactions[j]
		txIHandler := txI.GetTxHandler()
		txJHandler := txJ.GetTxHandler()

		delta := bytes.Compare(txIHandler.GetSndAddr(), txJHandler.GetSndAddr())
		if delta == 0 {
			delta = int(txIHandler.GetNonce()) - int(txJHandler.GetNonce())
		}

		return delta < 0
	}

	sort.Slice(transactions, sorter)
}

// xorBytes returns the XOR of two byte slices. Returns an error if b is shorter than a.
func xorBytes(a, b []byte) ([]byte, error) {
	if len(b) < len(a) {
		return nil, ErrInvalidAddressLength
	}
	res := make([]byte, len(a))
	for i := range a {
		res[i] = a[i] ^ b[i]
	}
	return res, nil
}
