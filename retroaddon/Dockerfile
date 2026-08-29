# Build stage: compile better-sqlite3's native binding.
FROM node:22-bookworm-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends python3 make g++ && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Runtime stage.
FROM node:22-bookworm-slim
ENV NODE_ENV=production PORT=7000 DB_PATH=/data/games.db
WORKDIR /app
COPY --from=build /app/node_modules ./node_modules
COPY package.json ./
COPY src ./src
RUN mkdir -p /data && chown node:node /data
USER node
VOLUME /data
EXPOSE 7000
CMD ["node", "src/server.js"]
