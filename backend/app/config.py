from functools import lru_cache
from os import getenv

from dotenv import load_dotenv


load_dotenv()


class Settings:
    app_name = "ppshu-ai-search"
    api_prefix = "/api"
    cors_origins = [
        origin.strip()
        for origin in getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]

    tavily_api_key = getenv("TAVILY_API_KEY", "")
    tavily_max_results = int(getenv("TAVILY_MAX_RESULTS", "8"))
    tavily_search_depth = getenv("TAVILY_SEARCH_DEPTH", "advanced")

    deepseek_api_key = getenv("DEEPSEEK_API_KEY", "")
    deepseek_base_url = getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_model = getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    deepseek_temperature = float(getenv("DEEPSEEK_TEMPERATURE", "0.2"))

    demo_mode = getenv("APP_DEMO_MODE", "auto").lower()

    @property
    def should_use_demo(self) -> bool:
        if self.demo_mode in {"1", "true", "yes", "on"}:
            return True
        if self.demo_mode in {"0", "false", "no", "off", "live"}:
            return False
        return not (self.tavily_api_key and self.deepseek_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
