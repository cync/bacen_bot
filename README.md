# BACEN Bot - Telegram Bot for Brazilian Central Bank Notifications

A Telegram bot that monitors BACEN (Brazilian Central Bank) RSS feeds and sends notifications to subscribed users.

## Features

- 🤖 Telegram bot interface for user management
- 📡 RSS feed monitoring for BACEN normatives
- 🗄️ PostgreSQL database for user subscriptions and duplicate prevention
- ⚡ Real-time notifications
- 🔄 Automatic deduplication of feed items

## Railway Deployment

### Prerequisites

1. Railway account
2. Telegram Bot Token (from @BotFather)
3. BACEN RSS feed URLs

### Deployment Steps

1. **Connect to Railway:**
   - Go to [Railway](https://railway.app)
   - Create a new project
   - Connect your GitHub repository

2. **Set Environment Variables:**
   In your Railway project settings, add these environment variables:

   ```
   DATABASE_URL=postgresql://postgres:HwzhykJvxaWDwOljZDFDMzVPpIsNcbCM@postgres.railway.internal:5432/railway
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   RSS_FEEDS=https://www.bcb.gov.br/api/feed/v1/noticias,https://www.bcb.gov.br/api/feed/v1/normativos
   MAX_ITEMS_PER_FEED=50
   ```

3. **Deploy Services:**
   Railway will automatically create two services:
   - **bacen-reply-bot**: Handles user messages (`python main.py`)
   - **bacen-cron**: Processes RSS feeds every 20 minutes (`python cron.py`)

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `TELEGRAM_TOKEN` | Telegram bot token from @BotFather | ✅ |
| `RSS_FEEDS` | Comma-separated RSS feed URLs | ✅ |
| `MAX_ITEMS_PER_FEED` | Maximum items to process per feed (default: 50) | ❌ |

### How It Works

**Fluxo Final:**
1. Usuário manda "oi" → entra na lista (opt-in)
2. A cada execução do cron (de 20 em 20 min, 09–19h):
   - Lemos o feed 2025
   - Para cada item inédito: montamos um resumo curto com data/hora de SP e enviamos pra todos os inscritos

**Serviços:**

1. **Reply Bot (`main.py`)**: Handles user interactions
   - `/start` - Welcome message
   - `oi` - Subscribe to notifications
   - `/stop` - Unsubscribe from notifications

2. **Cron Service (`cron.py`)**: Processes RSS feeds
   - Runs every 20 minutes during business hours (09-19h SP)
   - Fetches new items from configured RSS feeds
   - Sends notifications to all subscribers
   - Prevents duplicate notifications

3. **Storage (`storage.py`)**: Database operations
   - Manages user subscriptions
   - Tracks seen RSS items
   - Uses PostgreSQL for persistence

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```env
   DATABASE_URL=postgresql://postgres:HwzhykJvxaWDwOljZDFDMzVPpIsNcbCM@postgres.railway.internal:5432/railway
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   RSS_FEEDS=https://www.bcb.gov.br/api/feed/v1/noticias,https://www.bcb.gov.br/api/feed/v1/normativos
   MAX_ITEMS_PER_FEED=50
   ```

3. **Test database connection:**
   ```bash
   python test_db.py
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```

### Monitoring

- Check Railway logs for bot status
- Monitor database connection
- Verify RSS feed processing
- Check Telegram message delivery

### Troubleshooting

- **Database connection issues**: Verify `DATABASE_URL` is correct
- **Telegram API errors**: Check `TELEGRAM_TOKEN` validity
- **RSS feed errors**: Verify feed URLs are accessible
- **Memory issues**: Adjust `MAX_ITEMS_PER_FEED` if needed

### File Structure

```
bacen_bot/
├── main.py              # Reply bot service entry point
├── cron.py              # Cron service entry point
├── reply_bot.py         # Telegram bot handlers
├── sender.py            # RSS feed processor
├── storage.py           # Database operations
├── test_db.py           # Database connection test
├── requirements.txt     # Python dependencies
├── railway.json         # Railway configuration (Service + Cron)
├── Procfile            # Process definition
└── README.md           # This file
```
