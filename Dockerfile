# ============================================================
# Dockerfile — OpenClaw AI Learning Assistant
# ============================================================
# Multi-stage build for a production-ready OpenClaw gateway
# ============================================================

# ── Stage 1: Builder ──────────────────────────────────────────
FROM node:22-alpine AS builder

RUN apk add --no-cache python3 make g++ git
RUN npm install -g openclaw@latest
RUN openclaw --version

# ── Stage 2: Production ──────────────────────────────────────
FROM node:22-alpine AS production

LABEL maintainer="Shamya Lohitha Damisetti"
LABEL description="Personalized AI Learning Assistant on Telegram with OpenClaw"
LABEL version="1.0"

RUN apk add --no-cache curl tini tzdata && rm -rf /var/cache/apk/*

# Create non-root user for security
RUN addgroup -S openclaw && adduser -S openclaw -G openclaw

# Copy OpenClaw from builder stage
COPY --from=builder /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=builder /usr/local/bin/openclaw /usr/local/bin/openclaw
RUN ln -sf /usr/local/lib/node_modules/openclaw/dist/cli.js /usr/local/bin/openclaw 2>/dev/null || true

# Set up workspace directories
ENV OPENCLAW_HOME=/home/openclaw/.openclaw
ENV OPENCLAW_WORKSPACE=/home/openclaw/workspace

RUN mkdir -p \
    ${OPENCLAW_HOME} \
    ${OPENCLAW_WORKSPACE} \
    /home/openclaw/.openclaw/skills/user-onboarding \
    /home/openclaw/.openclaw/skills/daily-quiz \
    /home/openclaw/.openclaw/data/memory

# Copy project files
COPY config/openclaw.json ${OPENCLAW_HOME}/openclaw.json
COPY skills/user-onboarding/SKILL.md ${OPENCLAW_HOME}/skills/user-onboarding/SKILL.md
COPY skills/daily-quiz/SKILL.md ${OPENCLAW_HOME}/skills/daily-quiz/SKILL.md

# Set correct ownership
RUN chown -R openclaw:openclaw /home/openclaw

USER openclaw
WORKDIR /home/openclaw

EXPOSE 18789

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:18789/health || exit 1

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["openclaw", "gateway", "start"]
