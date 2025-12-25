---
description: How to deploy the Password Manager application
---

# Password Manager Deployment Guide

This guide covers deploying the Password Manager application using **Vercel** (frontend) and **Railway/Render** (backend).

## Prerequisites

Before deploying, ensure you have:
- [ ] Git repository pushed to GitHub
- [ ] Vercel account (free at https://vercel.com)
- [ ] Railway account (free at https://railway.app) OR Render account (free at https://render.com)
- [ ] PostgreSQL database (provided by Railway/Render or separate service)

---

## Part 1: Backend Deployment (Django API)

### Option A: Deploy to Railway

1. **Create a new Railway project**
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `Secure_Password_Manager_Biometric` repository
   - Choose the `password-manager-backend/password_manager` directory as the root

2. **Add PostgreSQL database**
   - In your Railway project, click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically provision a PostgreSQL database

3. **Configure environment variables**
   - In Railway, go to your Django service → "Variables"
   - Add these environment variables:
     ```
     DJANGO_SECRET_KEY=<generate-a-secure-random-key>
     DEBUG=False
     ALLOWED_HOSTS=.railway.app,.vercel.app,localhost
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
     ```

4. **Create Procfile for Railway**
   - Create `password-manager-backend/password_manager/Procfile`:
     ```
     web: python manage.py migrate && gunicorn password_manager.wsgi
     ```

5. **Update requirements.txt**
   - Add `gunicorn` and `whitenoise` for production:
     ```
     gunicorn>=20.1.0
     whitenoise>=6.4.0
     dj-database-url>=2.0.0
     ```

6. **Deploy**
   - Railway will automatically detect changes and deploy
   - Note your backend URL (e.g., `https://your-app.railway.app`)

### Option B: Deploy to Render

1. **Create a new Web Service**
   - Go to https://render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the `password-manager-backend/password_manager` directory

2. **Configure build settings**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python manage.py migrate && gunicorn password_manager.wsgi:application`

3. **Add PostgreSQL database**
   - In Render dashboard, click "New" → "PostgreSQL"
   - Copy the Internal Database URL

4. **Set environment variables** (same as Railway above)

---

## Part 2: Frontend Deployment (Next.js)

### Deploy to Vercel

1. **Install Vercel CLI** (optional but recommended)
   // turbo
   ```bash
   npm install -g vercel
   ```

2. **Configure environment variables**
   - Create `password-manager-frontend/.env.production`:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
     ```

3. **Deploy to Vercel**
   - Option 1: Using Vercel CLI
     ```bash
     cd password-manager-frontend
     vercel --prod
     ```
   
   - Option 2: Using Vercel Dashboard
     - Go to https://vercel.com
     - Click "New Project"
     - Import your GitHub repository
     - Select `password-manager-frontend` as the root directory
     - Add environment variable `NEXT_PUBLIC_API_URL`
     - Click "Deploy"

4. **Configure project settings**
   - Vercel will auto-detect Next.js settings
   - Build Command: `npm run build` (auto-configured)
   - Output Directory: `.next` (auto-configured)
   - Install Command: `npm install` (auto-configured)

---

## Part 3: Post-Deployment Configuration

### 1. Update Backend CORS Settings

Update your Django CORS settings to allow your Vercel frontend:

```python
# password-manager-backend/password_manager/password_manager/settings.py
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.vercel.app",
    "http://localhost:3000",  # for local development
]
```

### 2. Update Frontend API URL

Ensure your frontend is pointing to the correct backend URL:

```typescript
// password-manager-frontend/src/config.ts or similar
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### 3. Run Database Migrations

SSH into your backend service or use the platform's console:

```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

### 4. Verify Deployment

- ✅ Visit your frontend URL and test registration
- ✅ Test login functionality
- ✅ Test password creation and retrieval
- ✅ Test biometric authentication (if browser supports it)
- ✅ Check browser console for errors
- ✅ Test API endpoints directly

---

## Part 4: Optional Optimizations

### 1. Custom Domain (Optional)

**For Vercel:**
- Go to Project Settings → Domains
- Add your custom domain
- Update DNS records as instructed

**For Railway/Render:**
- Go to Settings → Custom Domains
- Add your domain and update DNS

### 2. Enable HTTPS (Automatic)

Both Vercel and Railway/Render provide automatic HTTPS certificates.

### 3. Set up CI/CD

- Both platforms support automatic deployments from GitHub
- Every push to `main` branch will trigger a new deployment

### 4. Monitor Your Application

- **Vercel**: Built-in analytics and monitoring
- **Railway**: View logs in the dashboard
- **Render**: View logs and metrics in the dashboard

---

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure `CORS_ALLOWED_ORIGINS` includes your frontend domain
   - Check that `django-cors-headers` is installed and configured

2. **Database Connection Errors**
   - Verify `DATABASE_URL` environment variable is set
   - Ensure migrations have been run

3. **Static Files Not Loading**
   - Configure `whitenoise` for serving static files
   - Run `python manage.py collectstatic`

4. **Build Failures**
   - Check build logs in platform dashboard
   - Verify all dependencies are in `requirements.txt` or `package.json`

---

## Environment Variables Checklist

### Backend (Django)
- [ ] `DJANGO_SECRET_KEY`
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS`
- [ ] `DATABASE_URL`
- [ ] `CORS_ALLOWED_ORIGINS`

### Frontend (Next.js)
- [ ] `NEXT_PUBLIC_API_URL`

---

## Cost Estimate

- **Vercel Free Tier**: Unlimited hobby projects
- **Railway Free Tier**: $5 credit/month (sufficient for small apps)
- **Render Free Tier**: Free web services with some limitations

**Total Cost**: $0 - $5/month for hobby/personal use

---

## Next Steps After Deployment

1. Test all functionality in production
2. Set up monitoring and error tracking (Sentry, LogRocket)
3. Configure backups for your database
4. Set up staging environment for testing
5. Document your deployment process
6. Share your deployed app!

---

**Need Help?**
- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Django Deployment Checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
