from django.conf import settings
from pylti1p3.tool_config import ToolConfDict

from apps.accounts.models import LtiPlatform


def read_keys() -> tuple[str, str]:
    return (
        settings.LTI_PRIVATE_KEY_PATH.read_text(encoding="utf-8"),
        settings.LTI_PUBLIC_KEY_PATH.read_text(encoding="utf-8"),
    )


def build_tool_conf() -> ToolConfDict:
    platforms = list(LtiPlatform.objects.filter(is_active=True))
    config: dict[str, list[dict]] = {}
    for platform in platforms:
        config.setdefault(platform.issuer, []).append(
            {
                "default": not config.get(platform.issuer),
                "client_id": platform.client_id,
                "auth_login_url": platform.auth_login_url,
                "auth_token_url": platform.auth_token_url,
                "key_set_url": platform.jwks_url,
                "key_set": None,
                "deployment_ids": [platform.deployment_id],
            }
        )
    tool_conf = ToolConfDict(config)
    private_key, public_key = read_keys()
    for platform in platforms:
        tool_conf.set_private_key(platform.issuer, private_key, client_id=platform.client_id)
        tool_conf.set_public_key(platform.issuer, public_key, client_id=platform.client_id)
    return tool_conf
