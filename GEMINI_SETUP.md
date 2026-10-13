# 🎯 Google Gemini API Setup (FREE)

## Get Your Free Gemini API Key

### 1. Go to Google AI Studio
- Visit: https://makersuite.google.com/app/apikey
- Sign in with your Google account (create one if needed)

### 2. Create API Key
- Click **"Create API Key"**
- Click **"Create API key in new project"**
- Your key appears instantly (copy it!)

### 3. Add to .env File
```bash
# Edit your .env file
GEMINI_API_KEY=your_key_here
```

Example:
```bash
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Free Tier Limits

| Limit | Value |
|-------|-------|
| Requests/minute | 60 |
| Requests/day | Unlimited |
| Cost | **FREE** ✅ |

✅ **Plenty for paper trading and learning!**

---

## Setup Your System

### Quick Setup
```bash
# 1. Update dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env

# 3. Add your Gemini key
# Edit .env and paste your key

# 4. Test system
python test_setup.py

# 5. Run!
python app.py
```

### Verify Setup
```bash
# Check if everything works
python test_setup.py

# Should show: ✓ google-generativeai
# Should show: ✓ GEMINI_API_KEY configured
```

---

## System Now Uses Gemini

✅ **Updated to use Google Gemini API (100% FREE)**

- ✅ Technical Analysis Bot
- ✅ Sentiment Analysis Bot
- ✅ ML Prediction Bot
- ✅ Fundamental Analysis Bot
- ✅ **Claude replaced with Gemini for AI Synthesis** ← AI now free!
- ✅ Paper Trading Engine
- ✅ Web Dashboard
- ✅ TradingView Integration

---

## Example .env File

```env
# FREE API Key from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: for sentiment analysis
NEWS_API_KEY=your_newsapi_key_here

# Webhook security
WEBHOOK_SECRET=your_webhook_secret_here

# Flask config
FLASK_DEBUG=True
FLASK_PORT=5000
```

---

## Troubleshooting

### "Invalid API key error"
- Make sure key is copied completely
- Check for leading/trailing spaces
- Verify at https://makersuite.google.com/app/apikey

### "API quota exceeded"
- Free tier: 60 requests/minute
- Wait a minute or upgrade to paid

### "google-generativeai not found"
```bash
pip install --upgrade google-generativeai
```

---

## Ready? Run It!

```bash
python app.py
```

Then open: http://localhost:5000

That's it! 🚀 Your AI analyst system is now running with **100% free Gemini AI!**
