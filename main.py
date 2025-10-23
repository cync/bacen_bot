#!/usr/bin/env python3
"""
Main entry point for the BACEN Bot reply service on Railway
Runs only the reply bot for handling user messages
"""
import asyncio
import os
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv
from aiohttp import web
import threading

# Load environment variables
load_dotenv()

# Import bot modules
from reply_bot import main as reply_bot_main

class BACENReplyBot:
    def __init__(self):
        self.running = True
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    async def health_check_handler(self, request):
        """Health check endpoint for Railway"""
        return web.json_response({
            "status": "healthy",
            "service": "bacen-reply-bot",
            "timestamp": datetime.now().isoformat()
        })
    
    async def start_web_server(self):
        """Start a simple web server for health checks"""
        app = web.Application()
        app.router.add_get('/health', self.health_check_handler)
        app.router.add_get('/', self.health_check_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Use PORT environment variable or default to 8000
        port = int(os.getenv('PORT', 8000))
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        print(f"🌐 Health check server running on port {port}")
        
    async def start(self):
        """Start the reply bot service"""
        print("🚀 Starting BACEN Reply Bot on Railway...")
        print(f"📅 Started at: {datetime.now()}")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start health check server
            await self.start_web_server()
            
            print("🤖 Starting reply bot...")
            await reply_bot_main()
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        finally:
            print("🏁 BACEN Reply Bot shutdown complete")
            
        return True

async def main():
    """Main entry point"""
    # Validate required environment variables
    required_vars = ["DATABASE_URL", "TELEGRAM_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your Railway project settings")
        sys.exit(1)
    
    # Start the reply bot
    reply_bot = BACENReplyBot()
    success = await reply_bot.start()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)
