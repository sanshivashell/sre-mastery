package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

// The commit stage's unit test covers the orders route only. That gap is deliberate: the break-me branch breaks
// routes these tests don't exercise, so the bug passes the commit gate and only the canary's SLI analysis catches it
// (L1·M06 lab step 6).
func TestOrdersReturnsOK(t *testing.T) {
	h := instrument("/api/orders", reply(map[string]string{"ok": "yes"}))
	rec := httptest.NewRecorder()
	h(rec, httptest.NewRequest(http.MethodGet, "/api/orders", nil))
	if rec.Code != http.StatusOK {
		t.Errorf("/api/orders: got %d, want 200", rec.Code)
	}
}
