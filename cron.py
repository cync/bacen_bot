#!/usr/bin/env python3
"""
Cron service for BACEN Bot RSS processing
Runs every 20 minutes during business hours (09-19h SP)
"""
import asyncio
import os
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv
from aiohttp import web
import pytz

# Load environment variables
load_dotenv()

# Import sender module
from sender import run_cron

# Configuração do fuso horário brasileiro
BR_TZ = pytz.timezone('America/Sao_Paulo')

class BACENCronService:
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
            "service": "bacen-cron",
            "timestamp": datetime.now(BR_TZ).isoformat()
        })
    
    async def start_web_server(self):
        """Start a simple web server for health checks"""
        app = web.Application()
        app.router.add_get('/health', self.health_check_handler)
        app.router.add_get('/', self.health_check_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Use PORT environment variable or default to 8001
        port = int(os.getenv('PORT', 8001))
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        print(f"🌐 Health check server running on port {port}")
        
    async def start(self):
        """Start the cron service"""
        print("🚀 Starting BACEN Cron Service on Railway...")
        print(f"📅 Started at: {datetime.now(BR_TZ)}")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start health check server
            await self.start_web_server()
            
            print("🕒 Starting RSS cron (10 em 10 min, 08:00-19:25h SP)...")
            await run_cron()
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        finally:
            print("🏁 BACEN Cron Service shutdown complete")
            
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
    
    # Start the cron service
    cron_service = BACENCronService()
    success = await cron_service.start()
    
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
