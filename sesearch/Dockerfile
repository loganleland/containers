# Use Debian Bookworm base
FROM debian:bookworm

# Install dependencies and setools (contains sesearch)
RUN apt-get update && \
    apt-get install -y setools selinux-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
