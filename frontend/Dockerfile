# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
# Используем npm install, так как package-lock.json может отсутствовать
RUN npm install

# Fix permissions for node_modules/.bin
RUN chmod -R +x node_modules/.bin 2>/dev/null || true

# Copy source code
COPY . .

# Build arguments for environment variables
ARG VITE_API_URL=http://localhost:8000
ARG VITE_MAX_BOT_TOKEN=

# Set environment variables for build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_MAX_BOT_TOKEN=$VITE_MAX_BOT_TOKEN

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

