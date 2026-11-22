FROM node:22-bookworm-slim AS frontend
WORKDIR /project/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
WORKDIR /project
ENV PYTHONUNBUFFERED=1
COPY backend/requirements.txt /tmp/saral-requirements.txt
RUN pip install --no-cache-dir -r /tmp/saral-requirements.txt
RUN useradd --no-create-home --uid 10001 saral
COPY backend/ ./backend/
COPY --from=frontend /project/frontend/dist/ ./frontend/dist/
USER saral
EXPOSE 10000
CMD ["sh", "-c", "exec uvicorn backend.app.production:app --host 0.0.0.0 --port ${PORT:-10000} --no-access-log"]
