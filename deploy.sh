#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DOMAIN=${1:-"moltable.ai"}
PROJECT_DIR="/opt/moltable"
DB_PASSWORD=$(openssl rand -base64 32)

echo -e "${GREEN}🚀 Deploying Moltable to ${DOMAIN}...${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Please run as root (use sudo)${NC}"
    exit 1
fi

# Update system
echo -e "${YELLOW}📦 Updating system...${NC}"
apt-get update -qq
apt-get install -y -qq curl git docker.io docker-compose nginx certbot python3-certbot-nginx openssl

# Enable Docker
systemctl enable docker
systemctl start docker
usermod -aG docker $SUDO_USER || true

# Create project directory
echo -e "${YELLOW}📁 Creating project directory...${NC}"
rm -rf $PROJECT_DIR
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Clone repository
echo -e "${YELLOW}📥 Cloning repository...${NC}"
read -p "Enter GitLab repository URL (e.g., git@gitlab.com:username/moltable.git or https://gitlab.com/username/moltable.git): " REPO_URL
git clone "$REPO_URL" .

# Generate environment file
echo -e "${YELLOW}⚙️  Generating configuration...${NC}"
cat > .env << EOF
# Database
DB_PASSWORD=${DB_PASSWORD}

# Telegram
TELEGRAM_BOT_TOKEN=8367425047:AAEiHFHLjGZACipWr85OlOY-ul7Jnrv61nw

# App
APP_DOMAIN=https://${DOMAIN}
EOF

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  moltable:
    build: .
    container_name: moltable
    restart: unless-stopped
    environment:
      - DATABASE_HOST=postgres
      - DATABASE_USER=moltable
      - DATABASE_PASSWORD=${DB_PASSWORD}
      - DATABASE_NAME=moltable
      - APP_DOMAIN=${APP_DOMAIN:-https://moltable.ai}
    ports:
      - "8080:8080"
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    container_name: moltable-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=moltable
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=moltable
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  nginx:
    image: nginx:alpine
    container_name: moltable-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - moltable

volumes:
  postgres_data:
EOF

# Create nginx.conf
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream moltable {
        server moltable:8080;
    }

    server {
        listen 80;
        server_name _;

        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://moltable;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/v1/telegram/webhook {
            proxy_pass http://moltable;
            proxy_set_header Content-Type application/json;
            proxy_set_header X-Telegram-Bot-Api-Secret-Token "";
        }
    }
}
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ./cmd/server/

FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /app

COPY --from=builder /app/main .
COPY migrations ./migrations

EXPOSE 8080

CMD ["./main"]
EOF

# Create nginx ssl directory
mkdir -p ssl

# Build and start
echo -e "${YELLOW}🐳 Building Docker images...${NC}"
docker-compose build

echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose up -d

# Wait for database
echo -e "${YELLOW}⏳ Waiting for database...${NC}"
sleep 10

# Run migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
docker-compose exec -T moltable go run cmd/migrate/main.go 2>/dev/null || true

# Setup SSL
echo -e "${YELLOW}🔒 Setting up SSL certificate...${NC}"
mkdir -p /var/www/letsencrypt/$DOMAIN

# Get SSL certificate
if [ -f /etc/letsencrypt/live/$DOMAIN/cert.pem ]; then
    echo "SSL certificate already exists"
else
    certbot certonly --webroot -w /var/www/letsencrypt/$DOMAIN \
        -d $DOMAIN -d www.$DOMAIN --register-unsafely-without-email --agree-tos || true
fi

# Copy SSL certificates
if [ -f /etc/letsencrypt/live/$DOMAIN/cert.pem ]; then
    cp /etc/letsencrypt/live/$DOMAIN/cert.pem ssl/
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/key.pem
    echo -e "${GREEN}✅ SSL certificates copied${NC}"
else
    echo -e "${YELLOW}⚠️  SSL not configured. Please run certbot manually.${NC}"
fi

# Setup auto-renewal
echo "0 0,12 * * * root certbot renew --quiet --deploy-hook 'cp /etc/letsencrypt/live/$DOMAIN/cert.pem /opt/moltable/ssl/ && cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/moltable/ssl/ && docker-compose restart nginx'" > /etc/cron.d/certbot-renew
chmod 644 /etc/cron.d/certbot-renew

# Restart nginx
docker-compose restart nginx

# Setup Telegram Webhook
echo -e "${YELLOW}📱 Setting up Telegram Webhook...${NC}"
TELEGRAM_TOKEN="8367425047:AAEiHFHLjGZACipWr85OlOY-ul7Jnrv61nw"
WEBHOOK_URL="https://${DOMAIN}/api/v1/telegram/webhook"

curl -s "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook?url=${WEBHOOK_URL}" || echo "Webhook setup skipped"

# Final
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "=========================================="
echo -e "${GREEN}🌐 Website: https://${DOMAIN}${NC}"
echo -e "${GREEN}📱 Telegram Bot: @moltable_bot${NC}"
echo -e "${GREEN}🔧 API: https://${DOMAIN}/api/v1/${NC}"
echo ""
echo "=========================================="
echo ""
echo "Useful commands:"
echo "  View logs:     cd ${PROJECT_DIR} && docker-compose logs -f"
echo "  Restart:       cd ${PROJECT_DIR} && docker-compose restart"
echo "  Update:        cd ${PROJECT_DIR} && git pull && docker-compose up -d --build"
echo ""
echo "📝 Don't forget to:"
echo "  1. Point your domain DNS to this server's IP"
echo "  2. Open ports 80, 443 in firewall"
echo "  3. Configure Telegram webhook URL in BotFather"
echo ""
