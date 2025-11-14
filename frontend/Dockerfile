# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first (to leverage Docker cache)
COPY frontend/package*.json ./
# Используем npm install, так как package-lock.json может отсутствовать
RUN npm install

# Create default .env file first
RUN echo "VITE_API_URL=https://max.isayalot.ru" > .env

# Copy project root to temp location to access .env file
COPY . /tmp/project-root/

# Copy .env from project root if it exists (will overwrite default)
RUN if [ -f /tmp/project-root/.env ]; then \
      cp /tmp/project-root/.env .env; \
    fi && \
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

