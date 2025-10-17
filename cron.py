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

# Load environment variables
load_dotenv()

# Import sender module
from sender import run_cron

class BACENCronService:
    def __init__(self):
        self.running = True
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    async def start(self):
        """Start the cron service"""
        print("🚀 Starting BACEN Cron Service on Railway...")
        print(f"📅 Started at: {datetime.now()}")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            print("🕒 Starting RSS cron (20 em 20 min, 09-19h SP)...")
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
    required_vars = ["DATABASE_URL", "TELEGRAM_TOKEN", "RSS_FEEDS"]
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
