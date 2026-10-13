# ⚡ Quick Alert Setup (5 Minutes)

## TradingView Indicator & Alert - Quick Start

---

## 🚀 The Fastest Path

### **3 Simple Steps:**

```
STEP 1: Add Indicator to Chart
STEP 2: Right-click → Create Alert  
STEP 3: Configure Webhook + Message
        ↓
    Done! Alerts now send to AI Analyst
```

---

## Step 1️⃣: Add Indicator (60 seconds)

```
1. Open TradingView: https://www.tradingview.com

2. Search for stock: Type "AAPL"

3. Add indicator:
   Click: "Indicators & Strategies" (top menu)
   
4. Choose one:
   • Moving Average (easiest)
   • RSI
   • MACD
   • Bollinger Bands
   
5. Click: Add to Chart
```

---

## Step 2️⃣: Create Alert (60 seconds)

```
1. Find the indicator on your chart
   (It's a line or histogram)

2. Right-click on it

3. Select: "Create Alert"

4. Alert window opens!
```

---

## Step 3️⃣: Configure Alert (3 minutes)

### **Tab 1: Set Condition**

```
Alert name: "AI Analyst AAPL BUY"

Condition examples:
  • Moving Average 20 > Moving Average 50
  • RSI(14) < 30
  • Price > 150
  • Volume > Average

Frequency: Once per bar
Expiration: None
```

### **Tab 2: Add Webhook (IMPORTANT!)**

```
1. Click: "Notifications" tab

2. Check box: ✅ Webhook URL

3. Enter URL:
   http://localhost:5000/api/webhook/tradingview

4. Scroll down → Add Headers:
   
   Header 1:
   Name:  X-Webhook-Secret
   Value: MyTradingViewSecret123
   
   (Must match your .env file!)

5. Enter Message:

   {
       "symbol": "{{ticker}}",
       "signal": "BUY",
       "confidence": 0.85
   }

6. Click: "Create Alert"
```

---

## ✅ That's It!

Your alert is now **ACTIVE** and will:

```
1. Monitor the condition
2. When it triggers → sends webhook
3. AI Analyst receives it
4. Executes paper trade automatically
5. Updates dashboard
```

---

## 📋 Copy-Paste Values

### Your Webhook URL:
```
http://localhost:5000/api/webhook/tradingview
```

### Your Header (must match .env):
```
Name: X-Webhook-Secret
Value: MyTradingViewSecret123
```

### Your BUY Message:
```json
{
    "symbol": "{{ticker}}",
    "signal": "BUY",
    "confidence": 0.85
}
```

### Your SELL Message:
```json
{
    "symbol": "{{ticker}}",
    "signal": "SELL",
    "confidence": 0.75
}
```

---

## 🔄 Create SELL Alert

Repeat the same steps but:

```
Alert name: "AI Analyst AAPL SELL"
Condition: Moving Average 20 < Moving Average 50
Message: Change "signal": "BUY" to "signal": "SELL"
```

---

## ✅ Test Your Alert

```bash
# 1. Wait for condition to trigger (or manually force it)

# 2. Check if trade executed:
curl http://localhost:5000/api/portfolio

# 3. View in dashboard:
http://localhost:5000

# 4. Check CLI:
python cli.py trades
```

---

## 🎯 Most Popular Setup

**Simple Moving Average Crossover:**

```
Indicator: Moving Average (SMA)
  • Period 1: 20
  • Period 2: 50

BUY Alert:
  Condition: SMA20 > SMA50
  Confidence: 0.85
  
SELL Alert:
  Condition: SMA20 < SMA50
  Confidence: 0.75
```

Why? Works on any timeframe, reliable, simple.

---

## 🆘 If It Doesn't Work

### Alert won't fire?
```
→ Check condition is actually true on chart
→ Is price really above/below indicator?
→ Try simpler condition first
```

### Webhook not received?
```
→ Make sure Flask is running: python app.py
→ Check URL is exactly correct (no typos)
→ Check secret matches .env
```

### Trade didn't execute?
```
→ Portfolio has cash available?
→ Signal is exactly "BUY" or "SELL"?
→ Confidence is 0-1 (not 0-100)?
```

---

## 📱 Variables You Can Use

In your message, use these:
```
{{ticker}}    → Stock symbol (AAPL)
{{close}}     → Current price
{{open}}      → Opening price
{{high}}      → Day high
{{low}}       → Day low
{{volume}}    → Trading volume
{{time}}      → Current time
```

Example:
```json
{
    "symbol": "{{ticker}}",
    "signal": "BUY",
    "price": {{close}},
    "time": "{{time}}",
    "confidence": 0.85
}
```

---

## 🎉 Done!

Your indicator and alert are set up and running!

**What happens next:**
1. ✅ You trade on TradingView chart
2. ✅ Indicator condition triggers
3. ✅ Alert fires
4. ✅ Webhook sends to AI Analyst
5. ✅ Paper trade executes
6. ✅ Dashboard updates in real-time

---

## 📚 Need More Details?

See full guide: **TRADINGVIEW_INDICATOR_ALERT_SETUP.md**

- ✅ Screenshots guide
- ✅ Real-world examples
- ✅ Troubleshooting
- ✅ Best practices
- ✅ Advanced tips

---

**You're all set! Start creating alerts now! 🚀**
