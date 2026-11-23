// sample-app: the service the L1·M06 lab builds, signs and ships through a canary.
// Three API routes, a health check and Prometheus metrics. The break-me branch changes failRoutes.
package main

import (
	"context"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// version is set at build time: -ldflags "-X main.version=<commit sha>".
var version = "dev"

// failRoutes return HTTP 500. Empty on main; the break-me branch fills it.
var failRoutes = map[string]bool{}

var (
	requests = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "http_requests_total",
		Help: "HTTP requests by route and status code.",
	}, []string{"route", "status"})
	duration = promauto.NewHistogramVec(prometheus.HistogramOpts{
		Name:    "http_request_duration_seconds",
		Help:    "HTTP request latency by route.",
		Buckets: []float64{.005, .01, .025, .05, .1, .25, .5, 1, 2.5},
	}, []string{"route"})
)

type recorder struct {
	http.ResponseWriter
	status int
}

func (r *recorder) WriteHeader(code int) { r.status = code; r.ResponseWriter.WriteHeader(code) }

// instrument counts and times every request to an API route.
func instrument(route string, h http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, req *http.Request) {
		start := time.Now()
		rec := &recorder{ResponseWriter: w, status: http.StatusOK}
		if failRoutes[route] {
			http.Error(rec, `{"error":"internal error"}`, http.StatusInternalServerError)
		} else {
			h(rec, req)
		}
		requests.WithLabelValues(route, strconv.Itoa(rec.status)).Inc()
		duration.WithLabelValues(route).Observe(time.Since(start).Seconds())
	}
}

func reply(v any) http.HandlerFunc {
	return func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(v)
	}
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/api/orders", instrument("/api/orders", reply(map[string]any{"orders": []string{"o-1001", "o-1002"}, "version": version})))
	mux.HandleFunc("/api/items", instrument("/api/items", reply(map[string]any{"items": []string{"keyboard", "monitor"}, "version": version})))
	mux.HandleFunc("/api/checkout", instrument("/api/checkout", reply(map[string]any{"status": "accepted", "version": version})))
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) { _, _ = w.Write([]byte("ok\n")) })
	mux.Handle("/metrics", promhttp.Handler())

	addr := ":8080"
	if p := os.Getenv("PORT"); p != "" {
		addr = ":" + p
	}
	srv := &http.Server{Addr: addr, Handler: mux, ReadHeaderTimeout: 5 * time.Second}
	go func() {
		log.Printf("sample-app %s listening on %s", version, addr)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatal(err)
		}
	}()

	// On SIGTERM (a pod being stopped), finish in-flight requests before exiting.
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM, os.Interrupt)
	<-stop
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	_ = srv.Shutdown(ctx)
	log.Printf("sample-app %s stopped", version)
}
