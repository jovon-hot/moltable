# Dockerfile - 单镜像部署
FROM golang:1.21-alpine AS builder

WORKDIR /app

# 复制依赖
COPY go.mod go.sum ./
RUN go mod download

# 复制源码
COPY . .

# 编译
RUN CGO_ENABLED=0 GOOS=linux go build -a -ldflags="-s -w" -o server ./cmd/server

# 运行阶段
FROM alpine:latest

RUN apk --no-cache add ca-certificates tzdata wget postgresql-client

WORKDIR /app

# 复制编译产物和模板
COPY --from=builder /app/server .
COPY --from=builder /app/config.yaml .
COPY --from=builder /app/migrations ./migrations
COPY --from=builder /app/templates ./templates
COPY --from=builder /app/static ./static

EXPOSE 8080

ENV TZ=UTC
ENV CONFIG_PATH=/app/config.yaml

CMD ["./server"]
