#!/bin/bash
# Moltable Startup and Test Script

echo "🧪 Moltable AI Agent Integration Test"
echo "======================================="
echo ""

# Check if server is running
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Server is running at http://localhost:8080"
else
    echo "⚠️  Server is not running. Starting..."
    cd /Users/lee/Desktop/project/moltable
    if [ -f "./moltable" ]; then
        ./moltable &
        sleep 2
        echo "✅ Server started"
    else
        echo "❌ Server binary not found. Building..."
        go build -o moltable ./cmd/server
        if [ $? -eq 0 ]; then
            ./moltable &
            sleep 2
            echo "✅ Server built and started"
        else
            echo "❌ Build failed"
            exit 1
        fi
    fi
fi

echo ""
echo "🧪 Running integration tests..."
echo ""

python3 test_integration.py
