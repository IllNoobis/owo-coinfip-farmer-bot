import re
import time
import threading
import logging

class VerificationMonitor:
    def __init__(self, config, discord_client):
        """
        Initialize the verification monitor.
        
        Args:
            config (dict): Configuration dictionary
            discord_client: DiscordClient instance
        """
        self.config = config
        self.client = discord_client
        self.logger = logging.getLogger(__name__)
        
        # Verification state
        self.verification_detected = False
        self.should_stop_monitoring = False
        self.monitor_thread = None
        self.alert_thread = None
        
        # Verification patterns to look for
        self.verification_patterns = [
            r"@\w+,\s*are you a real human\?.*verify",
            r"please use the link below so i can check",
            r"please complete this within \d+ minutes",
            r"verify.*within.*minutes.*ban"
        ]
    
    def check_for_verification(self):
        """
        Check for verification message in recent chat messages.
        
        Returns:
            bool: True if verification message is detected
        """
        if not self.config["verification"]["enable_verification_protection"]:
            return False
            
        try:
            # Get recent messages
            messages = self.client.get_recent_messages(15)
            
            # Check each message for verification patterns
            for message_text in messages:
                message_lower = message_text.lower()
                
                # Check for any verification pattern
                for pattern in self.verification_patterns:
                    if re.search(pattern, message_lower, re.IGNORECASE):
                        self.logger.critical("🚨 VERIFICATION REQUEST DETECTED!")
                        self.logger.critical(f"📄 Message: {message_text}")
                        return True
                
                # Also check for simple keyword combinations
                if ("human" in message_lower and "verify" in message_lower) or \
                   ("@" in message_text and "verify" in message_lower and "minutes" in message_lower):
                    self.logger.critical("🚨 VERIFICATION REQUEST DETECTED!")
                    self.logger.critical(f"📄 Message: {message_text}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error checking for verification: {e}")
            return False
    
    def start_monitoring(self):
        """Start the verification monitoring thread"""
        if not self.config["verification"]["enable_verification_protection"]:
            self.logger.info("🛡️  Verification monitoring disabled in config")
            return
            
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.logger.warning("⚠️  Verification monitoring already running")
            return
        
        self.should_stop_monitoring = False
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("🛡️  Verification monitoring started")
    
    def stop_monitoring(self):
        """Stop the verification monitoring"""
        self.should_stop_monitoring = True
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("🛡️  Verification monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread"""
        check_interval = self.config["verification"]["verification_check_interval"]
        
        while not self.should_stop_monitoring:
            try:
                # Check for verification message
                if self.check_for_verification():
                    if not self.verification_detected:
                        self.verification_detected = True
                        self.logger.warning("🚨 VERIFICATION DETECTED - Starting alert system")
                        
                        # Start alert system if enabled
                        if self.config["verification"]["enable_verification_alerts"]:
                            self._start_alert_system()
                else:
                    # If verification was detected but no longer present
                    if self.verification_detected:
                        self.verification_detected = False
                        self.logger.info("✅ Verification resolved - monitoring continues")
                
                # Wait before next check
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Error in verification monitoring loop: {e}")
                time.sleep(check_interval)
    
    def _start_alert_system(self):
        """Start the alert system in a separate thread"""
        if self.alert_thread and self.alert_thread.is_alive():
            return  # Alert system already running
            
        self.alert_thread = threading.Thread(target=self._alert_loop, daemon=True)
        self.alert_thread.start()
    
    def _alert_loop(self):
        """Alert loop that continuously pings until verification is resolved"""
        self.logger.critical("🚨 VERIFICATION ALERT SYSTEM ACTIVATED")
        self.logger.info("🔔 Continuously checking and alerting for verification...")
        
        ping_count = 0
        max_pings = 50  # Prevent infinite pinging
        
        while not self.should_stop_monitoring and ping_count < max_pings:
            if self.check_for_verification():
                ping_count += 1
                self.logger.warning(f"🚨 VERIFICATION PING #{ping_count}")
                
                # Send alert message
                try:
                    alert_message = f"🚨 VERIFICATION NEEDED! CHECK DISCORD NOW! (Alert #{ping_count})"
                    self.client.send_command(alert_message, "alert")
                except Exception as e:
                    self.logger.error(f"❌ Error sending verification alert: {e}")
                
                # Wait between pings
                time.sleep(2)
            else:
                # Verification resolved
                if self.verification_detected:
                    self.logger.info(f"✅ Verification resolved after {ping_count} alerts")
                    self.verification_detected = False
                    return
                break
        
        if ping_count >= max_pings:
            self.logger.critical(f"🚨 MAX VERIFICATION ALERTS REACHED ({max_pings})")
    
    def is_verification_active(self):
        """
        Check if verification is currently detected.
        
        Returns:
            bool: True if verification is currently active
        """
        return self.verification_detected
    
    def wait_for_verification_resolution(self, timeout=300):
        """
        Wait for verification to be resolved.
        
        Args:
            timeout (int): Maximum time to wait in seconds
            
        Returns:
            bool: True if verification was resolved, False if timeout
        """
        start_time = time.time()
        
        while self.verification_detected and (time.time() - start_time) < timeout:
            self.logger.info("⏸️  Waiting for verification to be resolved...")
            time.sleep(5)
        
        if self.verification_detected:
            self.logger.warning(f"⏰ Verification wait timeout after {timeout} seconds")
            return False
        else:
            self.logger.info("✅ Verification resolved - continuing")
            return True