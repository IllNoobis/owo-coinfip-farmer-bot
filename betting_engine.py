import re
import time
import logging
from datetime import datetime

class BettingEngine:
    def __init__(self, config, discord_client):
        """
        Initialize the betting engine with configuration and Discord client.
        
        Args:
            config (dict): Configuration dictionary
            discord_client: DiscordClient instance
        """
        self.config = config
        self.client = discord_client
        self.logger = logging.getLogger(__name__)
        
        # Betting state
        self.current_cash = 0
        self.starting_balance = 0
        self.current_bet = 0
        self.consecutive_losses = 0
        self.total_bets = 0
        self.total_wins = 0
        self.total_losses = 0
        self.total_profit = 0
        self.session_start_time = datetime.now()
        
        # Risk management flags
        self.stop_loss_triggered = False
        self.profit_target_reached = False
        self.max_losses_reached = False
        
    def check_cash(self):
        """
        Send 'w cash' command and parse the response to get current cash amount.
        
        Returns:
            float: The current cash amount
        """
        self.logger.info("💰 Checking current balance...")
        self.client.send_command("w cash", "cash_check")
        
        try:
            # Get recent messages to find cash information
            messages = self.client.get_recent_messages(10)
            
            # Find the latest message that contains cash information
            for message_text in messages:
                if "cowoncy" in message_text.lower():
                    # Extract the cash amount using regex
                    match = re.search(r'(\d+(?:,\d+)*)\s*cowoncy', message_text, re.IGNORECASE)
                    if match:
                        cash_str = match.group(1).replace(',', '')
                        previous_cash = self.current_cash
                        self.current_cash = float(cash_str)
                        
                        # Set starting balance if this is the first check
                        if self.starting_balance == 0:
                            self.starting_balance = self.current_cash
                            self.logger.info(f"🏦 Starting balance set: {self.starting_balance:,.0f} cowoncy")
                        
                        # Calculate profit/loss
                        self.total_profit = self.current_cash - self.starting_balance
                        
                        # Log balance change if significant
                        if previous_cash > 0:
                            change = self.current_cash - previous_cash
                            if change != 0:
                                change_symbol = "📈" if change > 0 else "📉"
                                self.logger.info(f"{change_symbol} Balance: {self.current_cash:,.0f} cowoncy ({change:+,.0f})")
                            else:
                                self.logger.info(f"💰 Balance: {self.current_cash:,.0f} cowoncy")
                        else:
                            self.logger.info(f"💰 Balance: {self.current_cash:,.0f} cowoncy")
                        
                        # Check risk management conditions
                        self._check_risk_conditions()
                        
                        return self.current_cash
            
            self.logger.warning("⚠️  Could not find cash information in recent messages")
            return 0
        except Exception as e:
            self.logger.error(f"❌ Error checking cash: {e}")
            return 0
    
    def _check_risk_conditions(self):
        """Check if any risk management conditions are triggered"""
        # Check stop loss
        if self.config["risk_management"]["enable_stop_loss"] and self.starting_balance > 0:
            loss_percentage = ((self.starting_balance - self.current_cash) / self.starting_balance) * 100
            if loss_percentage >= self.config["risk_management"]["stop_loss_percentage"]:
                self.stop_loss_triggered = True
                self.logger.critical(f"🛑 STOP LOSS TRIGGERED! Lost {loss_percentage:.1f}% of starting balance")
        
        # Check profit target
        if self.config["risk_management"]["enable_profit_target"] and self.starting_balance > 0:
            profit_percentage = (self.total_profit / self.starting_balance) * 100
            if profit_percentage >= self.config["risk_management"]["profit_target_percentage"]:
                self.profit_target_reached = True
                self.logger.info(f"🎯 PROFIT TARGET REACHED! Gained {profit_percentage:.1f}%")
        
        # Check consecutive losses
        if self.consecutive_losses >= self.config["betting"]["max_consecutive_losses"]:
            self.max_losses_reached = True
            self.logger.critical(f"🔥 MAX CONSECUTIVE LOSSES REACHED! ({self.consecutive_losses})")
    
    def calculate_bet_amount(self):
        """
        Calculate the appropriate bet amount based on strategy and risk management.
        
        Returns:
            float: The bet amount
        """
        if self.consecutive_losses == 0:
            # New betting cycle - bet percentage of current balance
            bet_amount = self.current_cash * (self.config["betting"]["initial_bet_percentage"] / 100)
        else:
            # Apply loss multiplier
            bet_amount = self.current_bet * self.config["betting"]["loss_multiplier"]
        
        # Apply minimum bet
        bet_amount = max(bet_amount, self.config["betting"]["min_bet_amount"])
        
        # Apply maximum bet limit
        if self.config["risk_management"]["enable_max_bet_limit"]:
            max_bet = self.current_cash * (self.config["risk_management"]["max_bet_percentage"] / 100)
            bet_amount = min(bet_amount, max_bet)
        
        # Round to nearest whole number
        return round(bet_amount)
    
    def place_coinflip_bet(self, amount):
        """
        Place a coin flip bet with the specified amount.
        
        Args:
            amount (float): The amount to bet
            
        Returns:
            bool: True if won, False if lost, None if error
        """
        amount = round(amount)
        self.current_bet = amount
        self.total_bets += 1
        
        self.logger.info(f"🎲 Placing bet #{self.total_bets}: {amount:,.0f} cowoncy")
        
        # Send the coin flip command
        self.client.send_command(f"w cf {amount}", "bet")
        
        try:
            # Wait a moment for the command to process
            time.sleep(3)
            
            # Get recent messages to find the result
            messages = self.client.get_recent_messages(5)
            
            # Find the latest message that contains coin flip result
            for message_text in messages:
                message_lower = message_text.lower()
                
                # Check if this is a message about our coin flip
                if "spent" in message_lower and "coin spins" in message_lower:
                    # Wait a moment for the message to be updated with results
                    time.sleep(2)
                    
                    # Get updated messages
                    updated_messages = self.client.get_recent_messages(5)
                    for updated_text in updated_messages:
                        updated_lower = updated_text.lower()
                        
                        # Check for win or loss
                        if "you won" in updated_lower:
                            # Extract the win amount for better reporting
                            match = re.search(r'you won (?:\*\*)?(\d+(?:,\d+)*)(?:\*\*)?!!', updated_lower)
                            win_amount = match.group(1).replace(',', '') if match else amount * 2
                            
                            self.total_wins += 1
                            self.logger.info(f"🎉 WIN! Bet #{self.total_bets}: +{win_amount} cowoncy")
                            
                            if self.consecutive_losses > 0:
                                self.logger.info(f"🔥 Broke loss streak of {self.consecutive_losses}!")
                                self.consecutive_losses = 0
                            
                            return True
                        elif "lost it all" in updated_lower:
                            self.total_losses += 1
                            self.consecutive_losses += 1
                            self.logger.info(f"💸 LOSS: Bet #{self.total_bets}: -{amount:,.0f} cowoncy")
                            return False
            
            # If we couldn't determine the result, wait longer and try again
            self.logger.warning("⚠️  Could not determine coin flip result immediately, waiting...")
            time.sleep(5)
            
            final_messages = self.client.get_recent_messages(10)
            for message_text in final_messages:
                message_lower = message_text.lower()
                if "you won" in message_lower and str(amount) in message_text:
                    self.total_wins += 1
                    self.logger.info(f"🎉 WIN! Bet #{self.total_bets}: +{amount*2:,.0f} cowoncy")
                    if self.consecutive_losses > 0:
                        self.consecutive_losses = 0
                    return True
                elif "lost it all" in message_lower and str(amount) in message_text:
                    self.total_losses += 1
                    self.consecutive_losses += 1
                    self.logger.info(f"💸 LOSS: Bet #{self.total_bets}: -{amount:,.0f} cowoncy")
                    return False
            
            self.logger.warning("⚠️  Could not determine coin flip result")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error checking coin flip result: {e}")
            return None
    
    def should_stop_betting(self):
        """
        Check if betting should stop based on risk management conditions.
        
        Returns:
            tuple: (should_stop, reason)
        """
        if self.stop_loss_triggered:
            return True, "Stop loss triggered"
        
        if self.profit_target_reached:
            return True, "Profit target reached"
        
        if self.max_losses_reached:
            return True, "Maximum consecutive losses reached"
        
        if self.current_cash <= 0:
            return True, "Insufficient funds"
        
        # Check session time limit
        if self.config["risk_management"]["enable_session_time_limit"]:
            session_hours = (datetime.now() - self.session_start_time).total_seconds() / 3600
            if session_hours >= self.config["risk_management"]["session_time_limit_hours"]:
                return True, "Session time limit reached"
        
        return False, ""
    
    def get_statistics(self):
        """
        Get current session statistics.
        
        Returns:
            dict: Statistics dictionary
        """
        runtime = datetime.now() - self.session_start_time
        hours, remainder = divmod(runtime.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        win_rate = (self.total_wins / self.total_bets * 100) if self.total_bets > 0 else 0
        
        return {
            "runtime": f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}",
            "starting_balance": self.starting_balance,
            "current_balance": self.current_cash,
            "total_profit": self.total_profit,
            "total_bets": self.total_bets,
            "total_wins": self.total_wins,
            "total_losses": self.total_losses,
            "win_rate": win_rate,
            "consecutive_losses": self.consecutive_losses,
            "current_bet": self.current_bet
        }
    
    def log_statistics(self):
        """Log current session statistics"""
        stats = self.get_statistics()
        
        self.logger.info("📊 SESSION STATISTICS")
        self.logger.info("-" * 50)
        self.logger.info(f"⏱️  Runtime: {stats['runtime']}")
        self.logger.info(f"💰 Starting Balance: {stats['starting_balance']:,.0f} cowoncy")
        self.logger.info(f"💵 Current Balance: {stats['current_balance']:,.0f} cowoncy")
        self.logger.info(f"📈 Total Profit/Loss: {stats['total_profit']:+,.0f} cowoncy")
        self.logger.info(f"🎲 Total Bets: {stats['total_bets']}")
        self.logger.info(f"✅ Wins: {stats['total_wins']}")
        self.logger.info(f"❌ Losses: {stats['total_losses']}")
        self.logger.info(f"📊 Win Rate: {stats['win_rate']:.1f}%")
        self.logger.info(f"🔥 Current Loss Streak: {stats['consecutive_losses']}")
        self.logger.info("-" * 50)