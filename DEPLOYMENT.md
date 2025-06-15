# Railway Deployment Guide

## 🚀 Deploy Bitcoin Trading Signal System to Railway

### Prerequisites
- Railway account (sign up at [railway.app](https://railway.app))
- Git repository with your code
- Telegram bot token and chat ID configured

### Step 1: Prepare for Deployment
Your project is already configured with:
- ✅ `Procfile` - Tells Railway how to run the app
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version specification
- ✅ `.gitignore` - Excludes sensitive files
- ✅ `config/telegram_config.json` - Bot configuration (test_mode: false)

### Step 2: Deploy to Railway

1. **Connect Repository**:
   ```bash
   # Initialize git if not already done
   git init
   git add .
   git commit -m "Initial commit - Bitcoin Trading Signal System"
   
   # Push to GitHub/GitLab (optional but recommended)
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo" (or upload directly)
   - Select your repository
   - Railway will automatically detect Python and deploy

3. **Monitor Deployment**:
   - Check the deployment logs in Railway dashboard
   - Look for "Bitcoin Signal System initialized" message
   - Verify scheduled signal checks are set up

### Step 3: Verify Live System

1. **Check Logs**:
   - In Railway dashboard, go to your project
   - Click on "Deployments" tab
   - View real-time logs

2. **Test Signal Generation**:
   - The system runs automatically on schedule
   - Next signal check times are logged
   - You'll receive Telegram notifications when signals are generated

### Step 4: Monitor and Maintain

- **Logs**: Monitor Railway logs for any errors
- **Telegram**: You'll receive notifications at scheduled times
- **Uptime**: Railway keeps the service running 24/7

### Scheduled Signal Times (Dutch Timezone):
**Signals sent 3 minutes before optimal entry times for 5-minute expiry options:**

**Morning Session (08:00-11:00 Amsterdam time):**
- 09:27 → Enter at 09:30
- 09:57 → Enter at 10:00
- 10:27 → Enter at 10:30

**Evening Session (17:00-19:00 Amsterdam time):**
- 18:27 → Enter at 18:30
- 18:57 → Enter at 19:00
- 19:27 → Enter at 19:30

**Total:** Up to 6 signals per day during your preferred trading hours

### Troubleshooting:
- **No signals**: Check logs for data fetching errors
- **Telegram not working**: Verify bot token and chat ID
- **Deployment fails**: Check requirements.txt and Python version

Your Bitcoin trading signal system is now live and will send you high-conviction trading signals via Telegram! 🎯 