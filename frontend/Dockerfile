# Single-stage Dockerfile: Build React app and serve with serve
FROM node:24-alpine

WORKDIR /app

# Build argument for API base URL
ARG REACT_APP_API_BASE=/api
ENV REACT_APP_API_BASE=${REACT_APP_API_BASE}

# Install serve globally with specific version
RUN npm install -g serve@14.2.5

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm install --omit=dev --no-audit --no-fund

# Copy source code
COPY . .

# Build the React application (optimized for Raspberry Pi 5)
ENV NODE_OPTIONS="--max-old-space-size=2048"
RUN npm run build

# Clean up dev dependencies to reduce image size
RUN rm -rf node_modules src public *.json *.md *.lock

# Expose port 3000
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# Start serve - single page app mode, listening on port 3000
CMD ["serve", "-s", "build", "-l", "3000"]
