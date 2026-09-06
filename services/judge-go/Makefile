BIN := bin/judge-go

.PHONY: build run test vet clean docker

build:
	go build -o $(BIN) .

vet:
	go vet ./...

test:
	go test ./...

run: build
	REDIS_URL=$${REDIS_URL:-redis://localhost:6379/0} ./$(BIN)

docker:
	docker build -t rankwant/judge-go .

clean:
	rm -rf bin
