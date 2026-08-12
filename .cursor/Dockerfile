# Base image for the roommate-finance Telegram bot (aiogram + PostgreSQL + Alembic).
# System-level, slow-changing dependencies live here; Python packages are installed
# from requirements.txt by ./.cursor/install.sh against the checked-out source.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-venv \
        python3-dev \
        postgresql \
        postgresql-contrib \
        libpq-dev \
        build-essential \
        git \
        curl \
        ca-certificates \
        sudo \
    && rm -rf /var/lib/apt/lists/*

# The ubuntu:24.04 image ships a non-root "ubuntu" user (uid 1000). Ensure it
# exists and grant passwordless sudo so install/start can manage the local
# PostgreSQL cluster.
RUN if ! id ubuntu >/dev/null 2>&1; then useradd -m -s /bin/bash -u 1000 ubuntu; fi \
    && usermod -aG sudo ubuntu \
    && echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/90-ubuntu \
    && chmod 0440 /etc/sudoers.d/90-ubuntu

USER ubuntu
