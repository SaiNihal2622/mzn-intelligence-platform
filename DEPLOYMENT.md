# 🌐 Deployment Guide: Reviewer Access

This guide explains how to expose the **Development Intelligence Platform** to an external reviewer.

## Option 1: Quick Demo (Tunneling) - *Fastest*
Use this if you want to give a reviewer access to the application currently running on your machine.

1.  **Install Localtunnel:**
    ```bash
    npm install -g localtunnel
    ```
2.  **Expose Port 8000:**
    ```bash
    lt --port 8000
    ```
3.  **Share the URL:** You will receive a URL like `https://mzn-platform.loca.lt`. Share this with the reviewer.
    > [!IMPORTANT]
    > Keep your terminal open. Closing it will terminate access.

---

## Option 2: Professional Hosting (Render.com) - *Recommended*
Render is the easiest platform for deploying Dockerized full-stack applications.

1.  **Push to GitHub:** Ensure your latest changes (including `Dockerfile` and `static/` build) are pushed to a private or public GitHub repo.
2.  **Create a New "Web Service" on Render:**
    - Connect your GitHub repository.
    - Render will automatically detect the `Dockerfile`.
3.  **Configure Environment Variables:**
    In the Render dashboard, add the following secret keys:
    - `GEMINI_API_KEY`: Your Google Gemini key.
    - `OPENROUTER_API_KEY`: Your OpenRouter key.
    - `LLM_PROVIDER`: `gemini`
    - `FAILPROOF_LLM`: `true`
    - `LOG_LEVEL`: `INFO`
4.  **Deploy:** Click "Create Web Service". Render will build the Docker container and provide a persistent `https://your-app.onrender.com` URL.

---

## Option 3: Local Review (Docker)
If the reviewer is technical and wants to run it themselves:

1.  **Send them the ZIP or Repo.**
2.  **They run:**
    ```bash
    docker-compose up --build
    ```
3.  **Access:** They can view it at `localhost:3000`.

---

## Deployment Checklist
- [ ] **API Keys:** Ensure keys are set in the platform's Environment Settings, not hardcoded.
- [ ] **Static Assets:** Verify `npm run build` was executed and assets are in `backend/static`.
- [ ] **Vector Store:** The system will automatically build the FAISS index on first launch.
