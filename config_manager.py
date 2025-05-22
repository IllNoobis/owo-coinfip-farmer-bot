import json
import os
from pathlib import Path
from datetime import datetime

class ConfigManager:
    def __init__(self):
        self.script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = self.script_dir / "configs"
        self.config_dir.mkdir(exist_ok=True)
        
    def get_default_config(self):
        """Return default configuration settings"""
        return {
            "general": {
                "channel_url": "https://discord.com/channels/1374324722510069812/1374572927596630076",
                "config_name": "default",
                "created_at": datetime.now().isoformat()
            },
            "betting": {
                "initial_bet_percentage": 1.0,  # 1% of balance
                "loss_multiplier": 2.5,  # Multiply bet by 2.5x on loss
                "min_bet_amount": 1,
                "max_consecutive_losses": 10,  # Stop after X consecutive losses
                "enable_progressive_betting": True
            },
            "risk_management": {
                "enable_stop_loss": True,
                "stop_loss_percentage": 50.0,  # Stop if balance drops by 50%
                "enable_profit_target": False,
                "profit_target_percentage": 100.0,  # Stop if profit reaches 100%
                "enable_max_bet_limit": True,
                "max_bet_percentage": 10.0,  # Never bet more than 10% of balance
                "enable_session_time_limit": False,
                "session_time_limit_hours": 24
            },
            "automation": {
                "enable_random_commands": True,
                "random_command_chance": 0.3,  # 30% chance
                "random_command_cooldown": 15,  # seconds
                "bet_delay_min": 8,
                "bet_delay_max": 15,
                "command_delay_min": 1,
                "command_delay_max": 4
            },
            "logging": {
                "log_level": "INFO",
                "log_statistics_interval": 10,  # Every X bets
                "enable_file_logging": True,
                "enable_console_logging": True
            },
            "verification": {
                "enable_verification_protection": True,
                "verification_check_interval": 5,  # seconds
                "enable_verification_alerts": True
            }
        }
    
    def create_config(self, config_name=None):
        """Create a new configuration file"""
        if not config_name:
            config_name = input("Enter config name (or press Enter for 'default'): ").strip()
            if not config_name:
                config_name = "default"
        
        config = self.get_default_config()
        config["general"]["config_name"] = config_name
        
        print(f"\n🔧 Creating configuration: {config_name}")
        print("=" * 50)
        
        # Get user input for key settings
        print("📋 GENERAL SETTINGS")
        url = input(f"Discord Channel URL [{config['general']['channel_url']}]: ").strip()
        if url:
            config["general"]["channel_url"] = url
        
        print("\n💰 BETTING SETTINGS")
        bet_pct = input(f"Initial bet percentage [{config['betting']['initial_bet_percentage']}%]: ").strip()
        if bet_pct:
            try:
                config["betting"]["initial_bet_percentage"] = float(bet_pct)
            except ValueError:
                print("Invalid percentage, using default")
        
        multiplier = input(f"Loss multiplier [{config['betting']['loss_multiplier']}x]: ").strip()
        if multiplier:
            try:
                config["betting"]["loss_multiplier"] = float(multiplier)
            except ValueError:
                print("Invalid multiplier, using default")
        
        max_losses = input(f"Max consecutive losses [{config['betting']['max_consecutive_losses']}]: ").strip()
        if max_losses:
            try:
                config["betting"]["max_consecutive_losses"] = int(max_losses)
            except ValueError:
                print("Invalid number, using default")
        
        print("\n🛡️ RISK MANAGEMENT")
        enable_stop_loss = input(f"Enable stop loss? [y/N]: ").strip().lower()
        config["risk_management"]["enable_stop_loss"] = enable_stop_loss in ['y', 'yes']
        
        if config["risk_management"]["enable_stop_loss"]:
            stop_loss = input(f"Stop loss percentage [{config['risk_management']['stop_loss_percentage']}%]: ").strip()
            if stop_loss:
                try:
                    config["risk_management"]["stop_loss_percentage"] = float(stop_loss)
                except ValueError:
                    print("Invalid percentage, using default")
        
        enable_profit_target = input(f"Enable profit target? [y/N]: ").strip().lower()
        config["risk_management"]["enable_profit_target"] = enable_profit_target in ['y', 'yes']
        
        if config["risk_management"]["enable_profit_target"]:
            profit_target = input(f"Profit target percentage [{config['risk_management']['profit_target_percentage']}%]: ").strip()
            if profit_target:
                try:
                    config["risk_management"]["profit_target_percentage"] = float(profit_target)
                except ValueError:
                    print("Invalid percentage, using default")
        
        max_bet = input(f"Max bet percentage [{config['risk_management']['max_bet_percentage']}%]: ").strip()
        if max_bet:
            try:
                config["risk_management"]["max_bet_percentage"] = float(max_bet)
            except ValueError:
                print("Invalid percentage, using default")
        
        # Save configuration
        config_file = self.config_dir / f"{config_name}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"\n✅ Configuration saved: {config_file}")
        return config
    
    def load_config(self, config_name=None):
        """Load a configuration file"""
        if not config_name:
            configs = self.list_configs()
            if not configs:
                print("No configurations found. Creating default...")
                return self.create_config("default")
            
            print("Available configurations:")
            for i, cfg in enumerate(configs, 1):
                print(f"{i}. {cfg}")
            
            choice = input("Select config number (or press Enter for first): ").strip()
            try:
                idx = int(choice) - 1 if choice else 0
                config_name = configs[idx]
            except (ValueError, IndexError):
                config_name = configs[0]
        
        config_file = self.config_dir / f"{config_name}.json"
        
        if not config_file.exists():
            print(f"Configuration '{config_name}' not found. Creating new...")
            return self.create_config(config_name)
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print(f"✅ Loaded configuration: {config_name}")
        return config
    
    def list_configs(self):
        """List all available configurations"""
        configs = []
        for file in self.config_dir.glob("*.json"):
            configs.append(file.stem)
        return sorted(configs)
    
    def edit_config(self, config_name=None):
        """Edit an existing configuration"""
        if not config_name:
            configs = self.list_configs()
            if not configs:
                print("No configurations found.")
                return None
            
            print("Available configurations:")
            for i, cfg in enumerate(configs, 1):
                print(f"{i}. {cfg}")
            
            choice = input("Select config to edit: ").strip()
            try:
                idx = int(choice) - 1
                config_name = configs[idx]
            except (ValueError, IndexError):
                print("Invalid selection")
                return None
        
        config = self.load_config(config_name)
        
        print(f"\n🔧 Editing configuration: {config_name}")
        print("=" * 50)
        print("Leave blank to keep current value")
        
        # Edit key settings
        print("\n📋 GENERAL SETTINGS")
        print(f"Current URL: {config['general']['channel_url']}")
        new_url = input("New URL: ").strip()
        if new_url:
            config["general"]["channel_url"] = new_url
        
        print(f"\n💰 BETTING SETTINGS")
        print(f"Current initial bet: {config['betting']['initial_bet_percentage']}%")
        new_bet = input("New initial bet percentage: ").strip()
        if new_bet:
            try:
                config["betting"]["initial_bet_percentage"] = float(new_bet)
            except ValueError:
                print("Invalid value, keeping current")
        
        print(f"Current loss multiplier: {config['betting']['loss_multiplier']}x")
        new_mult = input("New loss multiplier: ").strip()
        if new_mult:
            try:
                config["betting"]["loss_multiplier"] = float(new_mult)
            except ValueError:
                print("Invalid value, keeping current")
        
        # Save updated configuration
        config_file = self.config_dir / f"{config_name}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"\n✅ Configuration updated: {config_file}")
        return config
    
    def display_config(self, config):
        """Display configuration settings in a readable format"""
        print("\n📋 CURRENT CONFIGURATION")
        print("=" * 50)
        
        print(f"📌 Name: {config['general']['config_name']}")
        print(f"🌐 Channel: {config['general']['channel_url']}")
        
        print(f"\n💰 BETTING:")
        print(f"   Initial bet: {config['betting']['initial_bet_percentage']}% of balance")
        print(f"   Loss multiplier: {config['betting']['loss_multiplier']}x")
        print(f"   Max consecutive losses: {config['betting']['max_consecutive_losses']}")
        
        print(f"\n🛡️ RISK MANAGEMENT:")
        if config['risk_management']['enable_stop_loss']:
            print(f"   Stop loss: {config['risk_management']['stop_loss_percentage']}%")
        else:
            print("   Stop loss: Disabled")
        
        if config['risk_management']['enable_profit_target']:
            print(f"   Profit target: {config['risk_management']['profit_target_percentage']}%")
        else:
            print("   Profit target: Disabled")
        
        print(f"   Max bet limit: {config['risk_management']['max_bet_percentage']}%")
        
        print(f"\n🤖 AUTOMATION:")
        print(f"   Random commands: {'Enabled' if config['automation']['enable_random_commands'] else 'Disabled'}")
        print(f"   Bet delay: {config['automation']['bet_delay_min']}-{config['automation']['bet_delay_max']}s")
        
        print("=" * 50)