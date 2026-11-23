# Multi-stage build: the Go toolchain stays in the build stage; only the binary ships.
# Base images are pinned by digest (a tag can be republished; a digest cannot).
FROM golang:1.27-alpine@sha256:70bd7ddea8b6cbe5d6943cde279d6b67feb10cc924fb9100d1d8757c1575b280 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY *.go ./
ARG VERSION=dev
RUN CGO_ENABLED=0 go build -trimpath -ldflags "-s -w -X main.version=${VERSION}" -o /out/sample-app .

# Minimal runtime image, non-root user.
FROM gcr.io/distroless/static-debian12:nonroot@sha256:afa5c872c891853ca7fcf1f12c3edb23f7eeef36189728842dd51042ff57f7ab
COPY --from=build /out/sample-app /sample-app
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/sample-app"]
