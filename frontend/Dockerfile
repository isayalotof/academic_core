# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first (to leverage Docker cache)
COPY frontend/package*.json ./
# Используем npm install, так как package-lock.json может отсутствовать
RUN npm install

# Copy project root to temp location to access .env file FIRST
COPY . /tmp/project-root/

# Create default .env file first (in the project root where Vite expects it)
RUN echo "VITE_API_URL=https://max.isayalot.ru" > .env

# Copy .env from project root if it exists (will overwrite default)
RUN if [ -f /tmp/project-root/.env ]; then \
      echo "📋 Found .env file in project root, copying..."; \
      cp /tmp/project-root/.env .env; \
      echo "✅ .env file copied. Contents:"; \
      cat .env; \
    else \
      echo "⚠️  No .env file found in project root, using default"; \
      echo "📋 Default .env contents:"; \
      cat .env; \
    fi && \
    echo "🔍 Final .env file before build:" && \
    cat .env && \
    rm -rf /tmp/project-root

# Copy source code (this will invalidate cache if package.json changed)
COPY frontend/ .

# Fix permissions for node_modules/.bin after copying all files
RUN chmod -R +x node_modules/.bin 2>/dev/null || true


# Build the app using node to bypass permission issues
RUN node node_modules/vite/bin/vite.js build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

