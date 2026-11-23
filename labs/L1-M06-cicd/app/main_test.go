package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestRoutesReturnOK(t *testing.T) {
	for _, route := range []string{"/api/orders", "/api/items", "/api/checkout"} {
		h := instrument(route, reply(map[string]string{"ok": "yes"}))
		rec := httptest.NewRecorder()
		h(rec, httptest.NewRequest(http.MethodGet, route, nil))
		if rec.Code != http.StatusOK {
			t.Errorf("%s: got %d, want 200", route, rec.Code)
		}
	}
}
