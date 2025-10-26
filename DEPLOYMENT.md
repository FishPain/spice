# Streamlit Cloud Deployment Guide

## Issue: ImportError on Streamlit Cloud

If you see `ImportError: cannot import name 'build_graph' from 'agent.agent'`, try these solutions:

### Solution 1: Clear Cache and Reboot (Recommended)
1. Go to your Streamlit Cloud dashboard
2. Click on your app
3. Click the three dots menu (⋮) in the top right
4. Select **"Reboot app"**
5. If that doesn't work, also try **"Clear cache"** then reboot

### Solution 2: Force Redeploy
1. Make a small change to any file (add a comment)
2. Commit and push to GitHub
3. Streamlit Cloud will auto-redeploy

### Solution 3: Playwright Installation
For Playwright to work on Streamlit Cloud:

1. **System dependencies** - Already configured in `packages.txt`
2. **Browser installation** - The app now auto-installs browsers on startup using `@st.cache_resource`
3. **If browsers still fail to install**:
   - Check Streamlit Cloud logs for Playwright installation messages
   - Verify `packages.txt` system dependencies were installed
   - The app uses Chromium by default (most reliable on Linux)
   - Try changing browser in the sidebar: chromium → firefox → webkit

**Note**: First deployment may take 2-3 minutes while Playwright downloads browsers (~200MB).

### Solution 4: Check Python Version
Ensure your Streamlit Cloud uses Python 3.9+ (preferably 3.11 or 3.12):
- Add a `.python-version` file with content: `3.11`

### Solution 4: Playwright Installation
For Playwright to work on Streamlit Cloud, you need:

1. **packages.txt** (already created) - System dependencies for Chromium
2. **Post-install script**: Add to requirements.txt:
   ```
   playwright
   ```
   Then in your app, add before any scraping:
   ```python
   import subprocess
   subprocess.run(["playwright", "install", "chromium"])
   ```

## Files Created for Deployment

- ✅ `packages.txt` - System dependencies for Playwright
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `agent/__init__.py` - Makes agent a proper Python package
- ✅ All subdirectory `__init__.py` files

## Environment Variables on Streamlit Cloud

Make sure to set in Streamlit Cloud dashboard → App settings → Secrets:

```toml
OPENAI_API_KEY = "your-key-here"
APP_PASSWORD = "your-password"
LANGSMITH_API_KEY = "your-key-here"
LANGSMITH_PROJECT = "your-project"
```

## Testing Locally

Before deploying, test locally:
```bash
# Activate venv
source .venv/bin/activate

# Test import
python -c "from agent.agent import build_graph; print('Success')"

# Run app
streamlit run app.py
```

## Common Issues

### Issue: Module not found
- **Cause**: Missing `__init__.py` files
- **Fix**: Already created in this repo

### Issue: Playwright not working
- **Cause**: Missing system dependencies
- **Fix**: `packages.txt` file already created

### Issue: Import works locally but not on cloud
- **Cause**: Cached bytecode on Streamlit Cloud
- **Fix**: Reboot app + clear cache
