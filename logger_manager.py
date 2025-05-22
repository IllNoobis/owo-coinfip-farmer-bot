import logging
import sys
from pathlib import Path
from datetime import datetime

class LoggerManager:
    def __init__(self, config, config_name="default"):
        """
        Initialize the logging manager with configuration settings.
        
        Args:
            config (dict): Configuration dictionary
            config_name (str): Name of the configuration for log file naming
        """
        self.config = config
        self.config_name = config_name
        self.script_dir = Path(__file__).parent
        self.log_dir = self.script_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.setup_logging()
        
    def setup_logging(self):
        """Set up comprehensive logging system with file and console output"""
        # Create log filename with timestamp and config name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"discord_bot_{self.config_name}_{timestamp}.log"
        
        # Configure logging level
        log_level = getattr(logging, self.config["logging"]["log_level"].upper(), logging.INFO)
        
        # Clear any existing handlers
        logging.getLogger().handlers.clear()
        
        # Set up handlers
        handlers = []
        
        # File logging handler
        if self.config["logging"]["enable_file_logging"]:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            handlers.append(file_handler)
        
        # Console logging handler
        if self.config["logging"]["enable_console_logging"]:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            handlers.append(console_handler)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s | %(levelname)8s | %(name)15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=handlers
        )
        
        # Get logger for main application
        self.logger = logging.getLogger("DiscordBot")
        
        # Log session start
        self.logger.info("=" * 80)
        self.logger.info("🤖 DISCORD COINFLIP BOT SESSION STARTED")
        self.logger.info("=" * 80)
        if self.config["logging"]["enable_file_logging"]:
            self.logger.info(f"📁 Log file: {log_file}")
        self.logger.info(f"📋 Configuration: {self.config_name}")
        self.logger.info(f"🌐 Channel: {self.config['general']['channel_url']}")
        
        # Log configuration summary
        self._log_config_summary()
    
    def _log_config_summary(self):
        """Log a summary of the current configuration"""
        self.logger.info("⚙️  CONFIGURATION SUMMARY")
        self.logger.info("-" * 50)
        
        # Betting settings
        self.logger.info(f"💰 Initial bet: {self.config['betting']['initial_bet_percentage']:.1f}% of balance")
        self.logger.info(f"📈 Loss multiplier: {self.config['betting']['loss_multiplier']:.1f}x")
        self.logger.info(f"🔥 Max consecutive losses: {self.config['betting']['max_consecutive_losses']}")
        
        # Risk management
        if self.config['risk_management']['enable_stop_loss']:
            self.logger.info(f"🛑 Stop loss: {self.config['risk_management']['stop_loss_percentage']:.1f}%")
        
        if self.config['risk_management']['enable_profit_target']:
            self.logger.info(f"🎯 Profit target: {self.config['risk_management']['profit_target_percentage']:.1f}%")
        
        self.logger.info(f"🚫 Max bet limit: {self.config['risk_management']['max_bet_percentage']:.1f}%")
        
        # Automation
        if self.config['automation']['enable_random_commands']:
            self.logger.info(f"🎲 Random commands: {self.config['automation']['random_command_chance']*100:.0f}% chance")
        
        self.logger.info(f"⏱️  Bet delays: {self.config['automation']['bet_delay_min']}-{self.config['automation']['bet_delay_max']}s")
        
        # Verification
        if self.config['verification']['enable_verification_protection']:
            self.logger.info("🛡️  Verification protection: Enabled")
        
        self.logger.info("-" * 50)
    
    def get_logger(self, name=None):
        """
        Get a logger instance.
        
        Args:
            name (str): Logger name (optional)
            
        Returns:
            logging.Logger: Logger instance
        """
        if name:
            return logging.getLogger(name)
        return self.logger
    
    def log_session_end(self, statistics=None):
        """
        Log session end information.
        
        Args:
            statistics (dict): Session statistics dictionary (optional)
        """
        self.logger.info("🏁 SESSION ENDING")
        self.logger.info("=" * 50)
        
        if statistics:
            self.logger.info("📊 FINAL STATISTICS")
            self.logger.info(f"⏱️  Total Runtime: {statistics.get('runtime', 'Unknown')}")
            self.logger.info(f"💰 Starting Balance: {statistics.get('starting_balance', 0):,.0f} cowoncy")
            self.logger.info(f"💵 Final Balance: {statistics.get('current_balance', 0):,.0f} cowoncy")
            self.logger.info(f"📈 Total Profit/Loss: {statistics.get('total_profit', 0):+,.0f} cowoncy")
            self.logger.info(f"🎲 Total Bets: {statistics.get('total_bets', 0)}")
            self.logger.info(f"✅ Total Wins: {statistics.get('total_wins', 0)}")
            self.logger.info(f"❌ Total Losses: {statistics.get('total_losses', 0)}")
            self.logger.info(f"📊 Final Win Rate: {statistics.get('win_rate', 0):.1f}%")
        
        self.logger.info("=" * 80)
        self.logger.info("🤖 DISCORD COINFLIP BOT SESSION ENDED")
        self.logger.info("=" * 80)
    
    def set_log_level(self, level):
        """
        Change the logging level during runtime.
        
        Args:
            level (str): New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # Update all handlers
        for handler in logging.getLogger().handlers:
            handler.setLevel(log_level)
        
        # Update root logger
        logging.getLogger().setLevel(log_level)
        
        self.logger.info(f"📝 Logging level changed to: {level.upper()}")
    
    def log_error_with_context(self, error, context=""):
        """
        Log an error with additional context information.
        
        Args:
            error (Exception): The exception that occurred
            context (str): Additional context information
        """
        self.logger.error(f"❌ ERROR: {error}")
        if context:
            self.logger.error(f"📍 Context: {context}")
        self.logger.error(f"🔍 Error type: {type(error).__name__}")
    
    def log_configuration_change(self, setting, old_value, new_value):
        """
        Log configuration changes during runtime.
        
        Args:
            setting (str): The setting that was changed
            old_value: The previous value
            new_value: The new value
        """
        self.logger.info(f"⚙️  Configuration changed: {setting}")
        self.logger.info(f"   Old: {old_value}")
        self.logger.info(f"   New: {new_value}")
    
    def create_performance_log(self, operation, duration, success=True):
        """
        Log performance information for operations.
        
        Args:
            operation (str): Name of the operation
            duration (float): Duration in seconds
            success (bool): Whether the operation was successful
        """
        status = "✅" if success else "❌"
        self.logger.debug(f"{status} {operation}: {duration:.2f}s")