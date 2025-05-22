
# Discord Coinflip Bot v3.0 - Modular Edition

A sophisticated, modular Discord betting bot with advanced risk management, customizable configurations, and comprehensive logging.


As stated in name, (VERIFICATION/CAPTCHA FEATURE IS NOT CURRENTLY WORKING!) <USE AT OWN RISK> (MADE FOR EDUCATIONAL PURPOSES!)



## 🚀 Features

### Core Features
- **Modular Architecture**: Separated into distinct components for maintainability
- **Configuration Management**: Create, load, edit, and manage multiple configurations
- **Advanced Risk Management**: Stop-loss, profit targets, max bet limits, session time limits
- **Progressive Betting Strategy**: Configurable percentage-based betting with loss multipliers
- **Real-time Verification Protection**: Automatic detection and alerting for verification requests
- **Comprehensive Logging**: File and console logging with configurable levels
- **Statistics Tracking**: Real-time performance monitoring and reporting

### Risk Management
- **Stop Loss**: Automatically stop when losses reach a specified percentage
- **Profit Target**: Stop when profit goals are achieved
- **Max Bet Limit**: Never bet more than a specified percentage of balance
- **Consecutive Loss Limit**: Stop after a specified number of consecutive losses
- **Session Time Limit**: Automatically stop after a specified time period

### Automation Features
- **Anti-CAPTCHA Timing**: Randomized delays to avoid detection
- **Random Commands**: Periodically send random commands to appear human
- **Verification Monitoring**: Continuous background monitoring for verification requests
- **Graceful Error Handling**: Robust error handling and recovery mechanisms

## 📁 Project Structure

```
discord-coinflip-bot/
├── main.py                 # Main application entry point
├── config_manager.py       # Configuration management system
├── discord_client.py       # Discord interaction handling
├── betting_engine.py       # Betting logic and strategy
├── verification_monitor.py # Verification detection and alerts
├── logger_manager.py       # Logging system management
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── configs/               # Configuration files directory
├── logs/                  # Log files directory
└── chrome_data/           # Chrome browser profile data
```

## 🛠️ Installation

1. **Clone or download** all the Python files to a directory
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Ensure Chrome browser** is installed on your system

## ⚙️ Configuration

### First Run Setup
Run the bot and follow the interactive setup:
```bash
python main.py
```

The setup will guide you through:
1. **General Settings**: Discord channel URL
2. **Betting Strategy**: Initial bet percentage, loss multiplier, max consecutive losses
3. **Risk Management**: Stop loss, profit targets, max bet limits
4. **Automation**: Random commands, timing delays

### Configuration Options

#### Betting Settings
- `initial_bet_percentage`: Starting bet as percentage of balance (default: 1.0%)
- `loss_multiplier`: Multiply bet by this amount after loss (default: 2.5x)
- `max_consecutive_losses`: Stop after this many consecutive losses (default: 10)
- `min_bet_amount`: Minimum bet amount (default: 1)

#### Risk Management
- `enable_stop_loss`: Enable automatic stop loss (default: true)
- `stop_loss_percentage`: Stop when balance drops by this % (default: 50%)
- `enable_profit_target`: Enable profit target stopping (default: false)
- `profit_target_percentage`: Stop when profit reaches this % (default: 100%)
- `max_bet_percentage`: Maximum bet as % of balance (default: 10%)
- `enable_session_time_limit`: Enable time-based stopping (default: false)
- `session_time_limit_hours`: Maximum session length (default: 24)

#### Automation Settings
- `enable_random_commands`: Send random w b/w h commands (default: true)
- `random_command_chance`: Probability of sending random command (default: 0.3)
- `bet_delay_min/max`: Delay range between bets in seconds (default: 8-15)
- `command_delay_min/max`: Delay range for commands in seconds (default: 1-4)

## 🎮 Usage

### Starting the Bot
```bash
python main.py
```

### Configuration Management
1. **Create New Config**: Set up a new configuration with custom settings
2. **Load Existing Config**: Use a previously saved configuration
3. **Edit Config**: Modify an existing configuration
4. **List Configs**: View all available configurations

### Example Workflow
1. Run `python main.py`
2. Choose option 1 to create a new configuration
3. Enter your Discord channel URL
4. Set your betting parameters (e.g., 2% initial bet, 2.0x multiplier)
5. Configure risk management (e.g., 30% stop loss)
6. Start the bot and monitor the logs

## 📊 Strategy Explanation

### Progressive Betting Strategy
1. **Initial Bet**: Start with a percentage of your current balance
2. **Win**: Continue with the same bet amount
3. **Loss**: Multiply the bet by the configured multiplier (e.g., 2.5x)
4. **Recovery**: When you win after losses, return to initial percentage betting
5. **Risk Limits**: Never exceed maximum bet percentage or consecutive loss limits

### Example Betting Sequence
- Balance: 100,000 cowoncy, 1% initial bet, 2.5x multiplier
- Bet 1: 1,000 (1%) → Loss → Balance: 99,000
- Bet 2: 2,500 (2.5x) → Loss → Balance: 96,500  
- Bet 3: 6,250 (2.5x) → Win (+12,500) → Balance: 108,750
- Bet 4: 1,088 (1% of new balance) → Start new cycle

## 🛡️ Safety Features

### Verification Protection
- Continuous monitoring for verification requests
- Automatic detection of verification messages
- Alert system to notify user immediately
- Automatic betting pause during verification

### Risk Management
- Multiple stop-loss mechanisms
- Bet size limitations
- Time-based controls
- Consecutive loss protection

### Error Handling
- Graceful recovery from connection issues
- Multiple fallback methods for sending commands
- Comprehensive error logging
- Automatic retry mechanisms

## 📝 Logging

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational information
- **WARNING**: Warning messages and important events
- **ERROR**: Error conditions
- **CRITICAL**: Critical errors requiring immediate attention

### Log Files
- Stored in `logs/` directory
- Named with timestamp and configuration name
- Include full session statistics and performance data

## ⚠️ Important Notes

### Disclaimer
- This bot is for educational purposes
- Use at your own risk
- Always gamble responsibly
- Be aware of Discord's Terms of Service

### Browser Requirements
- Chrome browser must be installed
- Bot maintains a separate Chrome profile in `chrome_data/`
- Manual login to Discord required on first run

### Performance Tips
- Use reasonable delay settings to avoid detection
- Monitor logs for any issues
- Keep betting percentages conservative
- Set appropriate risk limits

## 🔧 Troubleshooting

### Common Issues
1. **Chrome Driver Issues**: The bot automatically downloads the correct ChromeDriver
2. **Login Problems**: Manually log in when prompted on first run
3. **Command Sending Failures**: Bot has multiple fallback methods
4. **Verification Detection**: Monitor logs for verification alerts

### Getting Help
- Check the log files for detailed error information
- Ensure your configuration settings are reasonable
- Verify Discord channel URL is correct
- Make sure you have sufficient balance to start betting

## 📈 Future Enhancements

- Web-based dashboard for monitoring
- Multiple betting strategies
- Advanced analytics and reporting
- Integration with other Discord bots
- Mobile notifications for verification alerts

---

**Version**: 3.0.0  
**Last Updated**: 2025   
**Author**: IllNoobis
