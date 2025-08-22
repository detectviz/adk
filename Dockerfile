
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements-ops.txt
ENV PORT=8000
CMD [ "python", "-m", "sre_assistant.server.app" ]
