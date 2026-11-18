# A seeded finding for Trivy: CI proves the scanner still detects (D-013).
# Synthetic. Never built. Trivy's check DS-0002 (high) must report the root user below.
FROM python:3.11-slim
USER root
CMD ["python", "-c", "print('seeded')"]
