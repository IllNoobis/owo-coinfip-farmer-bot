#!/usr/bin/env python3
"""
Discord Coinflip Bot - Main Application
A modular, configurable Discord betting bot with advanced risk management.
"""

import time
import random
import signal
import sys
from pathlib import Path

# Import our modules
from config_manager import ConfigManager
from discord_client import DiscordClient
from betting_engine import BettingEngine
from verification_monitor import VerificationMonitor
from logger_manager import LoggerManager

class DiscordCoinflipBot:
    def __init__(self):
        """Initialize the main bot application"""
        self.config_manager = ConfigManager()
        self.config = None
        self.logger_manager = None
        self.logger = None
        self.discord_client = None
        self.betting_engine = None
        self.verification_monitor = None
        self.should_exit = False
        
        # Set up signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print("\n🛑 Shutdown signal received. Cleaning up...")
        self.should_exit = True
        self.shutdown()
        sys.exit(0)
    
    def display_welcome(self):
        """Display welcome message and options"""
        print("🤖 Discord Coinflip Bot v3.0 - Modular Edition")
        print("=" * 60)
        print("✅ Modular architecture with separated components")
        print("✅ Customizable configuration management") 
        print("✅ Advanced risk management & stop-loss features")
        print("✅ Real-time verification protection")
        print("✅ Comprehensive logging & statistics")
        print("✅ Progressive betting strategy")
        print("=" * 60)
        print()
    
    def setup(self):
        """Set up the bot with user configuration choices"""
        print("🔧 BOT SETUP")
        print("-" * 30)
        print("1. Create new configuration")
        print("2. Load existing configuration") 
        print("3. Edit existing configuration")
        print("4. List all configurations")
        print()
        
        while True:
            choice = input("Select option (1-4) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                return False
            elif choice == '1':
                self.config = self.config_manager.create_config()
                break
            elif choice == '2':
                self.config = self.config_manager.load_config()
                break
            elif choice == '3':
                self.config = self.config_manager.edit_config()
                break
            elif choice == '4':
                configs = self.config_manager.list_configs()
                if configs:
                    print("\nAvailable configurations:")
                    for i, cfg in enumerate(configs, 1):
                        print(f"  {i}. {cfg}")
                else:
                    print("\nNo configurations found.")
                print()
                continue
            else:
                print("Invalid choice. Please try again.")
                continue
        
        if not self.config:
            print("❌ Failed to load configuration. Exiting.")
            return False
        
        # Display loaded configuration
        self.config_manager.display_config(self.config)
        
        # Confirm before starting
        confirm = input("\nStart bot with this configuration? [Y/n]: ").strip().lower()
        if confirm in ['n', 'no']:
            return False
        
        return True
    
    def initialize_components(self):
        """Initialize all bot components"""
        try:
            config_name = self.config["general"]["config_name"]
            
            # Initialize logger first
            self.logger_manager = LoggerManager(self.config, config_name)
            self.logger = self.logger_manager.get_logger("MainBot")
            
            # Initialize Discord client
            self.discord_client = DiscordClient(self.config)
            
            # Initialize betting engine
            self.betting_engine = BettingEngine(self.config, self.discord_client)
            
            # Initialize verification monitor
            self.verification_monitor = VerificationMonitor(self.config, self.discord_client)
            
            self.logger.info("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            return False
    
    def start_bot_services(self):
        """Start all bot services"""
        try:
            # Set up Discord client
            self.discord_client.setup_driver()
            self.discord_client.login_to_discord()
            
            # Start verification monitoring
            self.verification_monitor.start_monitoring()
            
            self.logger.info("🚀 All services started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error starting services: {e}")
            return False
    
    def run_betting_strategy(self):
        """Main betting strategy loop"""
        try:
            self.logger.info("🎯 BETTING STRATEGY STARTED")
            
            # Initial cash check
            initial_cash = self.betting_engine.check_cash()
            if initial_cash <= 0:
                self.logger.error("❌ No cowoncy detected - cannot start betting")
                return
            
            # Log strategy information
            self.logger.info(f"💰 Starting balance: {initial_cash:,.0f} cowoncy")
            self.logger.info(f"📋 Strategy: {self.config['betting']['initial_bet_percentage']}% initial bet")
            self.logger.info(f"📈 Loss multiplier: {self.config['betting']['loss_multiplier']}x")
            
            bet_count = 0
            
            while not self.should_exit:
                # Check if we should stop betting
                should_stop, reason = self.betting_engine.should_stop_betting()
                if should_stop:
                    self.logger.info(f"🛑 Stopping betting: {reason}")
                    break
                
                # Wait for verification to be resolved if detected
                if self.verification_monitor.is_verification_active():
                    self.logger.warning("⏸️  Betting paused - verification detected")
                    if not self.verification_monitor.wait_for_verification_resolution(300):
                        self.logger.critical("⏰ Verification timeout - stopping bot")
                        break
                    self.logger.info("▶️  Verification resolved - resuming betting")
                
                # Check current balance
                current_cash = self.betting_engine.check_cash()
                if current_cash <= 0:
                    self.logger.error("💸 Insufficient funds to continue")
                    break
                
                # Calculate bet amount
                bet_amount = self.betting_engine.calculate_bet_amount()
                
                # Ensure we have enough cash for the bet
                if bet_amount > current_cash:
                    self.logger.warning(f"⚠️  Bet amount ({bet_amount:,.0f}) exceeds balance ({current_cash:,.0f})")
                    bet_amount = current_cash
                
                # Log betting cycle info
                if self.betting_engine.consecutive_losses == 0:
                    self.logger.info(f"🆕 New betting cycle: {bet_amount:,.0f} cowoncy")
                else:
                    self.logger.info(f"🔄 Recovery attempt #{self.betting_engine.consecutive_losses + 1}: {bet_amount:,.0f} cowoncy")
                
                # Add pre-bet delay
                delay = self.discord_client.random_delay(
                    self.config["automation"]["bet_delay_min"],
                    self.config["automation"]["bet_delay_max"]
                )
                
                # Place the bet
                result = self.betting_engine.place_coinflip_bet(bet_amount)
                
                if result is None:
                    self.logger.warning("⚠️  Could not determine bet result, continuing...")
                    continue
                
                # Handle bet result
                if result:  # Win
                    if self.betting_engine.consecutive_losses > 0:
                        self.logger.info(f"🎊 Recovery successful after {self.betting_engine.consecutive_losses} losses!")
                        # Add extra delay after recovery
                        self.discord_client.random_delay(6, 12)
                    else:
                        self.logger.info("✅ Continuing winning streak")
                        self.discord_client.random_delay(4, 8)
                else:  # Loss
                    self.logger.warning(f"📊 Loss streak: {self.betting_engine.consecutive_losses}")
                    # Shorter delay after loss to attempt recovery
                    self.discord_client.random_delay(3, 7)
                
                bet_count += 1
                
                # Log statistics at regular intervals
                if bet_count % self.config["logging"]["log_statistics_interval"] == 0:
                    self.betting_engine.log_statistics()
                
                # Randomly send commands if enabled
                if self.config["automation"]["enable_random_commands"]:
                    if random.random() < self.config["automation"]["random_command_chance"]:
                        self.discord_client.send_random_command()
                
                # Add delay between betting cycles
                self.discord_client.random_delay(
                    self.config["automation"]["bet_delay_min"],
                    self.config["automation"]["bet_delay_max"]
                )
        
        except KeyboardInterrupt:
            self.logger.info("⏹️  Bot stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Error in betting strategy: {e}")
        finally:
            # Log final statistics
            self.betting_engine.log_statistics()
    
    def run(self):
        """Main bot execution method"""
        try:
            # Display welcome and setup
            self.display_welcome()
            
            if not self.setup():
                print("👋 Setup cancelled. Goodbye!")
                return
            
            # Initialize components
            if not self.initialize_components():
                print("❌ Failed to initialize components. Exiting.")
                return
            
            # Start services
            if not self.start_bot_services():
                self.logger.error("❌ Failed to start services. Exiting.")
                return
            
            # Run the betting strategy
            self.run_betting_strategy()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Critical error in main execution: {e}")
            else:
                print(f"❌ Critical error: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown all components"""
        try:
            if self.logger:
                self.logger.info("🔄 Shutting down bot components...")
            
            # Stop verification monitoring
            if self.verification_monitor:
                self.verification_monitor.stop_monitoring()
            
            # Close Discord client
            if self.discord_client:
                self.discord_client.close()
            
            # Log final statistics and session end
            if self.betting_engine and self.logger_manager:
                final_stats = self.betting_engine.get_statistics()
                self.logger_manager.log_session_end(final_stats)
            
            if self.logger:
                self.logger.info("✅ Shutdown complete")
            
        except Exception as e:
            print(f"⚠️  Error during shutdown: {e}")


def main():
    """Main entry point"""
    try:
        # Create bot instance
        bot = DiscordCoinflipBot()
        
        # Run the bot
        bot.run()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user. Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()