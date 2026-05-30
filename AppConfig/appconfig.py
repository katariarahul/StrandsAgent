import boto3
import time
import json
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()
# ---------------------------------------------------
# AppConfig Details
# ---------------------------------------------------

APPLICATION_ID = os.getenv("APPCONFIG_APPLICATION_ID")
logger.info(f"***************Application ID ********** = {APPLICATION_ID}")
ENVIRONMENT_ID = os.getenv("APPCONFIG_ENVIRONMENT_ID")
CONFIG_PROFILE_ID = os.getenv("APPCONFIG_CONFIGURATION_PROFILE_ID")
# ---------------------------------------------------
# AppConfig Client
# ---------------------------------------------------

appconfig = boto3.client(
    "appconfigdata",
    region_name="us-east-1"
)

# ---------------------------------------------------
# Simple Config Cache
# ---------------------------------------------------

config_cache = None
last_refresh = 0
CACHE_TTL = float(os.getenv("CACHE_TTL", "60"))
config_token = None

def initialize_appconfig():
    print("inside initialize_appconfig")
    global config_token
    logger.info("inside initialize_appconfig")
    if config_token is None:
        try:
            # Start configuration session once
            session = appconfig.start_configuration_session(
                ApplicationIdentifier=APPLICATION_ID,
                EnvironmentIdentifier=ENVIRONMENT_ID,
                ConfigurationProfileIdentifier=CONFIG_PROFILE_ID,
            )
            logger.info(f"start session response = {session}")
            config_token = session["InitialConfigurationToken"]
            logger.info(f"token = {config_token}")
        except Exception as e:
            print("Error in session object",e)
    return config_token



def get_runtime_config():
    global config_cache
    global last_refresh
    global config_token

    now = time.time()
    try:
        # initialize only once
        if config_token is None:
            config_token = initialize_appconfig()

        # Use cache if still valid
        if config_cache and (now - last_refresh < CACHE_TTL):
            logger.info(f"Returning cached config = {config_cache}")
            return config_cache
        logger.info(f"config_token before latest call = {config_token}")

        response = appconfig.get_latest_configuration(
            ConfigurationToken=config_token
        )

        config_token = response["NextPollConfigurationToken"]

        config_data = response["Configuration"].read()
        logger.info(f"Raw config_data = {config_data}")

        if config_data:
            config_cache = json.loads(config_data.decode("utf-8"))
            last_refresh = now
            logger.info(f"Updated config cache = {config_cache}")
        else:
            logger.info("Empty config payload received from AppConfig")
    except Exception as e:
        logger.exception("Error in get_runtime_config")
    
     # Always return dict
    if config_cache is None:
        return {}
    
    return config_cache