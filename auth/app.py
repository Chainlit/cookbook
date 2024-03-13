from cookbook.auth.azure_ad_b2c_oauthprovider import AzureADB2COAuthProvider
from cookbook.auth.inject_custom_auth import add_custom_oauth_provider

add_custom_oauth_provider("azure-ad-b2c", AzureADB2COAuthProvider())

@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  return default_user  

# The rest of your logic
