# Deployment Instructions: Funda House Scraper Web App

This project consists of a FastAPI backend (Python) and a modern HTML/Tailwind frontend. To deploy the full application, you need to host both the backend and the frontend. GitHub Pages can only host the static frontend, not the backend. For a working app, follow the steps below.

---

## 1. Deploy the FastAPI Backend

You can deploy the backend to any cloud provider that supports Python web apps, such as:
- **Render.com** (free tier available)
- **Fly.io**
- **Railway.app**
- **Heroku** (may require a credit card)
- **VPS/VM** (e.g., DigitalOcean, AWS EC2, etc.)

### Example: Deploy to Render.com

1. **Push your code to GitHub.**
2. Go to [https://render.com](https://render.com) and sign up/log in.
3. Click **"New Web Service"** and connect your GitHub repo.
4. Set the following settings:
    - **Environment:** Python 3.x
    - **Build Command:** `pip install -r backend/requirements.txt`
    - **Start Command:** `uvicorn backend.api:app --host 0.0.0.0 --port 10000`
    - **(Optional) Working Directory:** Set to your repo root or `backend/` if needed.
5. Click **"Create Web Service"** and wait for deployment.
6. Note the public URL (e.g., `https://your-app.onrender.com`).

### Example: Deploy to Fly.io

1. Install the [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/).
2. Run `fly launch` in your project directory and follow prompts.
3. Set the Dockerfile or use a `fly.toml` for Python/uvicorn.
4. Deploy with `fly deploy`.
5. Note your public URL.

---

## 2. Deploy the Frontend (Static HTML)

### Option A: GitHub Pages (Frontend Only)

1. Copy `backend/listings.html` (and any static assets) to a new folder, e.g., `frontend/`.
2. Commit and push to your GitHub repo.
3. In your repo settings, enable GitHub Pages for the `frontend/` folder (or `main` branch, `/root` if you put it there).
4. **Edit the API URLs in your HTML:**
    - Change all `http://localhost:8000/...` to your deployed backend URL (e.g., `https://your-app.onrender.com/...`).
    - Example:
      ```js
      fetch('https://your-app.onrender.com/listings', ...)
      fetch('https://your-app.onrender.com/scrape_listings?...', ...)
      ```
5. Visit your GitHub Pages URL to use the frontend.

### Option B: Serve Frontend from Backend

- You can also serve `listings.html` directly from FastAPI (already supported in your code). This way, users only need to visit your backend URL.
- To do this, deploy only the backend as above. The HTML will be available at `/listings.html` or `/`.

---

## 3. Final Notes

- **CORS:** Make sure CORS is enabled in your FastAPI backend (already done in your code).
- **Environment Variables:** If you use secrets or API keys, set them in your cloud provider's dashboard.
- **HTTPS:** All public deployments should use HTTPS (automatic on most platforms).
- **Backend Only:** GitHub Pages cannot run Python or FastAPI. It is for static files only.

---

## 4. Example Directory Structure

```
House_scraper/
├── backend/
│   ├── api.py
│   ├── scrape_api.py
│   ├── ...
│   └── listings.html
├── frontend/   # (optional, for GitHub Pages)
│   └── listings.html
├── requirements.txt
└── DEPLOYMENT.md
```

---

## 5. Useful Links

- [Render Python Quickstart](https://render.com/docs/deploy-python)
- [Fly.io Python Guide](https://fly.io/docs/languages-and-frameworks/python/)
- [GitHub Pages Docs](https://pages.github.com/)
- [FastAPI Deployment Docs](https://fastapi.tiangolo.com/deployment/)

---

If you need a production-ready setup (Docker, CI/CD, custom domains), ask for more details!
