import logging
import sys
from datetime import datetime

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  # Auto-reset colors
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    if COLORAMA_AVAILABLE:
        COLORS = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
            'RESET': Style.RESET_ALL,
            'BOLD': Style.BRIGHT,
        }
    else:
        # Fallback ANSI codes
        COLORS = {
            'DEBUG': '\033[36m',
            'INFO': '\033[32m',
            'WARNING': '\033[33m',
            'ERROR': '\033[31m',
            'CRITICAL': '\033[35m',
            'RESET': '\033[0m',
            'BOLD': '\033[1m',
        }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        bold = self.COLORS['BOLD']
        
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        log_message = (
            f"{color}{bold}[{record.levelname}]{reset} "
            f"{timestamp} - {color}{record.name}{reset} - "
            f"{record.getMessage()}"
        )
        
        return log_message

def setup_logger(name: str = "story_forge", level: str = "INFO", colored: bool = True):
    """
    Setup basic logger for the application with optional colors
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Choose formatter based on color preference and terminal support
    if colored and sys.stdout.isatty():  # Only use colors in terminal
        formatter = ColoredFormatter()
    else:
        # Fallback to standard formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Create default logger instance
logger = setup_logger()