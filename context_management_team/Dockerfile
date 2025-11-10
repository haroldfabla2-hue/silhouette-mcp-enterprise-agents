# Context Management Team Dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install dependencies
RUN npm install --production

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S contextmgr && \
    adduser -S contextmgr -u 1001

# Change ownership of app directory
RUN chown -R contextmgr:contextmgr /app

# Switch to non-root user
USER contextmgr

# Expose port
EXPOSE 8070

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8070/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Start the service
CMD ["node", "main.js"]
