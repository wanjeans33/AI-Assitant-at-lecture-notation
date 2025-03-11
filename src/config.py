import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SILICON_FLOW_API_KEY = os.getenv('SILICON_FLOW_API_KEY')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set."""
        missing_vars = []
        
        if not cls.OPENAI_API_KEY:
            missing_vars.append('OPENAI_API_KEY')
        if not cls.SILICON_FLOW_API_KEY:
            missing_vars.append('SILICON_FLOW_API_KEY')
        if not cls.DEEPSEEK_API_KEY:
            missing_vars.append('DEEPSEEK_API_KEY')
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                "Please check your .env file."
            )

# Validate configuration on import
Config.validate() 