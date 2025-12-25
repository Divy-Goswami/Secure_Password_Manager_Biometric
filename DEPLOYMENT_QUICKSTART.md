# 🎯 Deployment Quick Start

## Your Production Secret Key
```
o92dsjee&h)a2+8pr1%4188&^rx_1xrts6374*k(z(@&w5q(_z
```

## Backend (Railway) - Environment Variables
```bash
DJANGO_SECRET_KEY=o92dsjee&h)a2+8pr1%4188&^rx_1xrts6374*k(z(@&w5q(_z
DEBUG=False
ALLOWED_HOSTS=.railway.app,.vercel.app,localhost
DJANGO_SETTINGS_MODULE=password_manager.settings_production
CORS_ALLOWED_ORIGINS=https://[YOUR-VERCEL-URL].vercel.app,http://localhost:3000
EMAIL_HOST_USER=bbramadhikari@gmail.com
EMAIL_HOST_PASSWORD=sjbu texf yxtp fuve
```

## Frontend (Vercel) - Environment Variables
```bash
NEXT_PUBLIC_API_URL=https://[YOUR-RAILWAY-URL].railway.app
```

## Deployment Order
1. ✅ Deploy Backend to Railway FIRST
2. ✅ Get Railway URL
3. ✅ Deploy Frontend to Vercel (use Railway URL in env var)
4. ✅ Get Vercel URL
5. ✅ Update Railway CORS_ALLOWED_ORIGINS with Vercel URL
6. ✅ Test!

## Railway Settings
- **Root Directory**: `password-manager-backend/password_manager`
- **Database**: Add PostgreSQL from Railway dashboard

## Vercel Settings
- **Root Directory**: `password-manager-frontend`
- **Framework**: Next.js (auto-detected)

## After Deployment
```bash
# Create admin user (run in Railway console)
python manage.py createsuperuser

# Collect static files (if needed)
python manage.py collectstatic --noinput
```

## URLs to Update
- [ ] Railway backend URL → Update in Vercel env vars
- [ ] Vercel frontend URL → Update in Railway CORS settings
