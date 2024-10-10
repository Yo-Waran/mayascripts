import logging

# Set up the logger
logger = logging.getLogger("My Custom Program")

# Manually check if there are handlers, and remove them if necessary
if len(logger.handlers) > 0:
    del logger.handlers[:]  # Clear the handlers list by deleting all its elements

# Create a StreamHandler to output logs to Maya's Script Editor
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(stream_handler)

#setting the logger level
logger.setLevel(logging.INFO)

###########################################################################
#ADDING A CUSTOM LEVEL 

# Step 1: Define the new custom logging level
NOTICE_LEVEL = 25  # Numeric value between INFO (20) and WARNING (30)

# Step 2: Add the custom level to the logging module
logging.addLevelName(NOTICE_LEVEL, "NOTICE")

# Step 3: Define a method in the Logger class for the new level
def notice(self, message, *args, **kwargs):
    if self.isEnabledFor(NOTICE_LEVEL):
        self._log(NOTICE_LEVEL, message, args, **kwargs)

# Add the method to the logger instance
logging.Logger.notice = notice

###########################################################################
#order of levels by numeric values
""" 
Numeric Level Summary

DEBUG: 10
INFO: 20
WARNING: 30
ERROR: 40
CRITICAL: 50 

"""

logger.debug("This is a DEBUG message")

logger.info("This is an INFO message")

logger.notice("This is a NOTICE message ")

logger.warning("This is a WARNING message")

logger.error("This is an ERROR message")

logger.critical("This is a CRITICAL message")