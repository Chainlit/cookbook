import os
import secrets
import string
from chainlit.oauth_providers import providers

chars = string.ascii_letters + string.digits + "$%*,-./:=>?@^_~"


def random_secret(length: int = 64):
    return "".join((secrets.choice(chars) for i in range(length)))


def custom_oauth_enabled():
    if (os.environ.get('OAUTH_AZURE_AD_B2C_CLIENT_ID') is not None
            and os.environ.get('OAUTH_AZURE_AD_B2C_CLIENT_SECRET') is not None
            and os.environ.get('OAUTH_AZURE_AD_B2C_TENANT_ID') is not None
            and os.environ.get('OAUTH_AZURE_AD_B2C_TENANT_NAME') is not None
            and os.environ.get('OAUTH_AZURE_AD_B2C_REDIRECT_URL') is not None
            and os.environ.get('OAUTH_AZURE_AD_B2C_POLICY') is not None):
        print("B2C OAuth configured.")
        return True
    else:
        print("B2C OAuth not configured. Skipping...")
        return False


def provider_id_in_instance_list(provider_id: str):
    if providers is None:
        print("No providers found")
        return False
    if not any(provider.id == provider_id for provider in providers):
        print(f"Provider {provider_id} not found")
        return False
    else:
        print(f"Provider {provider_id} found")
        return True


def add_custom_oauth_provider(provider_id: str, custom_provider_instance):
    if custom_oauth_enabled() and not provider_id_in_instance_list(provider_id):
        providers.append(custom_provider_instance)
        print(f"Added provider: {provider_id}")
    else:
        print(f"Custom OAuth is not enabled or provider {provider_id} already exists")
