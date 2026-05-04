package sync

import (
	"sync"
	"sync/atomic"
)

// rwMutex is a mutex that can be used to lock/unlock a resource
// this component is not concurrent safe, concurrent accesses need to be managed by the caller
type rwMutex struct {
	cntLocks  atomic.Int32
	cntRLocks atomic.Int32

	controlMut sync.RWMutex
}

// newRWMutex returns a new instance of rwMutex
func newRWMutex() *rwMutex {
	return &rwMutex{}
}

func (rm *rwMutex) updateCounterLock() {
	rm.cntLocks.Add(1)
}

func (rm *rwMutex) updateCounterRLock() {
	rm.cntRLocks.Add(1)
}

func (rm *rwMutex) updateCounterUnlock() {
	rm.cntLocks.Add(-1)
}

func (rm *rwMutex) updateCounterRUnlock() {
	rm.cntRLocks.Add(-1)
}

// lock locks the rwMutex
func (rm *rwMutex) lock() {
	rm.controlMut.Lock()
}

// unlock unlocks the rwMutex
func (rm *rwMutex) unlock() {
	rm.controlMut.Unlock()
}

// rLock locks for read the rwMutex
func (rm *rwMutex) rLock() {
	rm.controlMut.RLock()
}

// rUnlock unlocks for read the rwMutex
func (rm *rwMutex) rUnlock() {
	rm.controlMut.RUnlock()
}

// numLocks returns the number of locks on the rwMutex
func (rm *rwMutex) numLocks() int32 {
	return rm.cntLocks.Load() + rm.cntRLocks.Load()
}
