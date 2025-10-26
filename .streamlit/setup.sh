#!/bin/bash

# Install Playwright browsers
python -m playwright install chromium --with-deps

# Install system dependencies (if needed)
python -m playwright install-deps chromium
