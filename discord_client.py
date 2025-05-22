import time
import random
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains

class DiscordClient:
    def __init__(self, config):
        """
        Initialize the Discord client with configuration settings.
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.channel_url = config["general"]["channel_url"]
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
        # Command cooldown tracking
        self.last_command_time = {
            'w b': 0,
            'w h': 0
        }
        
        # Set up chrome profile directory
        self.script_dir = Path(__file__).parent
        self.chrome_data_dir = self.script_dir / "chrome_data"
        
    def random_delay(self, min_seconds=None, max_seconds=None):
        """Add a random delay based on configuration or provided values"""
        if min_seconds is None:
            min_seconds = self.config["automation"]["command_delay_min"]
        if max_seconds is None:
            max_seconds = self.config["automation"]["command_delay_max"]
            
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    def setup_driver(self):
        """Set up the Selenium WebDriver with appropriate options"""
        self.logger.info("🔧 Setting up Chrome WebDriver...")
        
        options = webdriver.ChromeOptions()
        # Prevent Discord from detecting automation
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Create chrome_data directory if it doesn't exist
        if not self.chrome_data_dir.exists():
            self.chrome_data_dir.mkdir(exist_ok=True)
            self.logger.info(f"📁 Created new Chrome profile directory: {self.chrome_data_dir}")
        else:
            self.logger.info(f"📁 Using existing Chrome profile: {self.chrome_data_dir}")
        
        # Use the local profile directory to maintain sessions
        options.add_argument(f"user-data-dir={self.chrome_data_dir}")
        
        # Use WebDriver Manager to automatically get the correct driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        
        self.logger.info("✅ Chrome WebDriver setup complete")
    
    def login_to_discord(self):
        """Navigate to Discord and handle login if needed"""
        self.logger.info("🌐 Navigating to Discord...")
        self.driver.get(self.channel_url)
        
        # First check if login is needed
        try:
            # Wait to see if we need to log in
            login_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_any_elements_located((
                    (By.CSS_SELECTOR, "input[name='email']"),
                    (By.CSS_SELECTOR, "button[type='submit']")
                ))
            )
            
            if login_elements:
                self.logger.info("🔐 Login screen detected - waiting for manual login...")
                # Wait for manual login to complete
                WebDriverWait(self.driver, 120).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
                )
                self.logger.info("✅ Successfully logged in to Discord")
        except:
            # If we didn't find login elements, we might already be logged in
            try:
                # Wait for the chat to load
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
                )
                self.logger.info("✅ Already logged in to Discord")
                
                # Wait for messages to fully load
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='messageContent']"))
                )
                self.logger.info("📨 Chat messages loaded successfully")
            except TimeoutException:
                self.logger.warning("⚠️  Could not detect login status - manual intervention may be needed")
                input("Press Enter after Discord is fully loaded and you're ready to continue...")
        
        # Wait additional time for everything to load properly
        self.random_delay(8, 12)
        self.logger.info("🚀 Discord setup complete - ready to start!")
    
    def send_command(self, command, command_type="general"):
        """
        Send a command to the Discord chat with appropriate timing.
        
        Args:
            command (str): The command to send
            command_type (str): Type of command for appropriate delay timing
        """
        # Set delay ranges based on command type and configuration
        if command_type == "cash_check":
            min_delay, max_delay = 2, 5
        elif command_type == "bet":
            min_delay = self.config["automation"]["bet_delay_min"]
            max_delay = self.config["automation"]["bet_delay_max"]
        elif command_type == "random":
            min_delay, max_delay = 1, 3
        else:
            min_delay = self.config["automation"]["command_delay_min"]
            max_delay = self.config["automation"]["command_delay_max"]
        
        # Add random delay before sending command
        delay = self.random_delay(min_delay, max_delay)
        
        try:
            # Find the textbox using the role attribute
            textbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='textbox'][aria-label*='Message']"))
            )
            
            # Click to focus the textbox
            textbox.click()
            time.sleep(0.5)
            
            # Clear any existing text
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time.sleep(0.5)
            
            # Delete selected text
            textbox.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # Type the command
            textbox.send_keys(command)
            time.sleep(0.5)
            
            # Send the command
            textbox.send_keys(Keys.RETURN)
            
            self.logger.info(f"📤 Sent command: {command} (delay: {delay:.1f}s)")
            
            # Wait for the bot to respond
            self.random_delay(3, 6)
            
        except Exception as e:
            self.logger.error(f"❌ Error with primary send method: {e}")
            self._try_alternative_send_methods(command)
    
    def _try_alternative_send_methods(self, command):
        """Try alternative methods to send commands if primary method fails"""
        try:
            # Alternative method using JavaScript execution
            js_script = """
            const textbox = document.querySelector('div[role="textbox"][aria-label*="Message"]');
            if (textbox) {
                textbox.focus();
                
                const selection = window.getSelection();
                const range = document.createRange();
                range.selectNodeContents(textbox);
                selection.removeAllRanges();
                selection.addRange(range);
                document.execCommand('delete', false, null);
                
                document.execCommand('insertText', false, arguments[0]);
                return true;
            }
            return false;
            """
            
            success = self.driver.execute_script(js_script, command)
            if success:
                ActionChains(self.driver).send_keys(Keys.RETURN).perform()
                self.logger.info(f"📤 Sent command with JavaScript method: {command}")
                self.random_delay(3, 6)
            else:
                raise Exception("Could not find textbox with JavaScript")
                
        except Exception as e2:
            self.logger.error(f"❌ JavaScript method failed: {e2}")
            try:
                # Final fallback - try using active element
                self.driver.switch_to.active_element.send_keys(command)
                time.sleep(0.5)
                self.driver.switch_to.active_element.send_keys(Keys.RETURN)
                self.logger.info(f"📤 Sent command with active element method: {command}")
                self.random_delay(3, 6)
            except Exception as e3:
                self.logger.error(f"❌ All send methods failed: {e3}")
    
    def send_random_command(self):
        """Send random commands (w b or w h) with cooldown enforcement"""
        if not self.config["automation"]["enable_random_commands"]:
            return False
            
        current_time = time.time()
        cooldown = self.config["automation"]["random_command_cooldown"]
        available_commands = []
        
        # Check which commands are available (not on cooldown)
        for cmd in ['w b', 'w h']:
            if current_time - self.last_command_time[cmd] >= cooldown:
                available_commands.append(cmd)
        
        if available_commands:
            # Randomly choose from available commands
            chosen_command = random.choice(available_commands)
            self.last_command_time[chosen_command] = current_time
            
            self.logger.info(f"🎲 Sending random command: {chosen_command}")
            self.send_command(chosen_command, "random")
            return True
        else:
            # Calculate when next command will be available
            next_available = min(cooldown - (current_time - self.last_command_time[cmd]) for cmd in ['w b', 'w h'])
            self.logger.debug(f"⏰ Random commands on cooldown - next available in {next_available:.1f}s")
            return False
    
    def get_recent_messages(self, limit=10):
        """
        Get recent messages from the chat.
        
        Args:
            limit (int): Number of recent messages to retrieve
            
        Returns:
            list: List of message text strings
        """
        try:
            messages = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='messageContent']"))
            )
            
            # Get the most recent messages
            recent_messages = []
            for message in reversed(messages[-limit:]):
                recent_messages.append(message.text)
            
            return recent_messages
        except Exception as e:
            self.logger.error(f"❌ Error getting recent messages: {e}")
            return []
    
    def close(self):
        """Close the Discord client and browser"""
        if self.driver:
            self.logger.info("🔧 Closing browser...")
            self.driver.quit()
            self.driver = None
