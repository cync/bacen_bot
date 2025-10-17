#!/usr/bin/env python3
"""
Main entry point for the BACEN Bot deployed on Railway
Runs both the reply bot (for handling user messages) and the sender (for RSS processing)
"""
import asyncio
import os
import signal
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import bot modules
from reply_bot import main as reply_bot_main
from sender import run_once as sender_run_once

class BACENBotManager:
    def __init__(self):
        self.running = True
        self.reply_bot_task = None
        self.sender_task = None
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    async def run_sender_periodically(self):
        """Run the sender every 30 minutes"""
        while self.running:
            try:
                print(f"📡 Running RSS sender at {datetime.now()}")
                await sender_run_once()
                print("✅ RSS sender completed successfully")
            except Exception as e:
                print(f"❌ RSS sender failed: {e}")
            
            # Wait 30 minutes before next run
            if self.running:
                print("⏰ Waiting 30 minutes until next RSS check...")
                await asyncio.sleep(30 * 60)  # 30 minutes
    
    async def run_reply_bot(self):
        """Run the reply bot continuously"""
        try:
            print("🤖 Starting reply bot...")
            await reply_bot_main()
        except Exception as e:
            print(f"❌ Reply bot failed: {e}")
            raise
    
    async def start(self):
        """Start both bot services"""
        print("🚀 Starting BACEN Bot on Railway...")
        print(f"📅 Started at: {datetime.now()}")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start both tasks concurrently
            self.reply_bot_task = asyncio.create_task(self.run_reply_bot())
            self.sender_task = asyncio.create_task(self.run_sender_periodically())
            
            # Wait for either task to complete or fail
            done, pending = await asyncio.wait(
                [self.reply_bot_task, self.sender_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Check if any task failed
            for task in done:
                if task.exception():
                    print(f"❌ Task failed: {task.exception()}")
                    return False
                    
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        finally:
            print("🏁 BACEN Bot shutdown complete")
            
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
    
    # Start the bot manager
    bot_manager = BACENBotManager()
    success = await bot_manager.start()
    
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
