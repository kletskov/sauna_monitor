from dataclasses import dataclass
import os

def _get_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}

@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "5000"))
    refresh_interval_s: int = int(os.getenv("REFRESH_INTERVAL_S", "10"))
    tuya_device_name: str = os.getenv("TUYA_DEVICE_NAME", "Breaker")
    tuya_version: str = os.getenv("TUYA_VERSION", "3.3")

    # Temperature settings
    temp_display_in_fahrenheit: bool = _get_bool("TEMP_DISPLAY_IN_FAHRENHEIT", False)

    # YoLink
    yolink_uaid: str = os.getenv("YOLINK_UAID", "")
    yolink_secret_key: str = os.getenv("YOLINK_SECRET_KEY", "")
    yolink_device_id: str = os.getenv("YOLINK_DEVICE_ID", "")

    # Telegram
    telegram_token: str = os.getenv("TELEGRAM_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    telegram_ready_temp_c: float = float(os.getenv("TELEGRAM_READY_TEMP_C", "75"))

    # Tuya
    tuya_device_id: str = os.getenv("TUYA_DEVICE_ID", "")
    tuya_local_key: str = os.getenv("TUYA_LOCAL_KEY", "")
    tuya_ip: str = os.getenv("TUYA_IP", "")
