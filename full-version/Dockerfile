# Dockerfile for full-version React app (Vite)
FROM node:20-slim AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build the app with environment variables
ARG VITE_APP_API_URL=http://localhost:3010/
ARG VITE_APP_BASE_URL=http://localhost:3000
ENV VITE_APP_API_URL=$VITE_APP_API_URL
ENV VITE_APP_BASE_URL=$VITE_APP_BASE_URL
RUN npm run build

# Production image: serve static files
FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Remove default nginx static assets
RUN rm -rf ./*

# Copy built assets from builder
COPY --from=builder /app/dist .

# Copy custom nginx site config for SPA routing
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
