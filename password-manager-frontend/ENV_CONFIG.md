# Frontend Production Environment Configuration

To deploy the frontend to Vercel, you'll need to set up environment variables in the Vercel dashboard.

## Required Environment Variables

Add this in your Vercel project settings under "Environment Variables":

```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

**Steps:**
1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add the variable name: `NEXT_PUBLIC_API_URL`
4. Add the value: Your deployed backend URL (e.g., `https://password-manager-backend.railway.app`)
5. Select "Production" environment
6. Click "Save"

## Important Notes

- The `NEXT_PUBLIC_` prefix is required for environment variables that need to be accessible in the browser
- Update the URL after deploying your backend to Railway/Render
- Do NOT include a trailing slash in the URL
