# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first (to leverage Docker cache)
COPY frontend/package*.json ./
# Используем npm install, так как package-lock.json может отсутствовать
RUN npm install

# Copy .env file from project root for Vite build-time variables
# Vite will automatically read .env file from the project root
COPY .env ./

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

