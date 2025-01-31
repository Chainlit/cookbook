import os
import httpx
from fastapi import HTTPException
from chainlit.user import User
from chainlit.oauth_providers import OAuthProvider
import json
from cookbook.auth.validate_jwt import validate_jwt, decode_jwt

class AzureADB2COAuthProvider(OAuthProvider):
    id = "azure-ad-b2c"
    env = [
        "OAUTH_AZURE_AD_B2C_CLIENT_ID",
        "OAUTH_AZURE_AD_B2C_CLIENT_SECRET",
        "OAUTH_AZURE_AD_B2C_TENANT_ID",
        "OAUTH_AZURE_AD_B2C_POLICY",
    ]
    url_base = f"https://{os.environ.get('OAUTH_AZURE_AD_B2C_TENANT_NAME', '')}.b2clogin.com/{os.environ.get('OAUTH_AZURE_AD_B2C_TENANT_NAME', '')}.onmicrosoft.com/{os.environ.get('OAUTH_AZURE_AD_B2C_POLICY', '')}/"

    authorize_url = f"{url_base}oauth2/v2.0/authorize"
    token_url = f"{url_base}oauth2/v2.0/token"
    well_known_url = f"{url_base}v2.0/.well-known/openid-configuration"
    iss_url = f"https://{os.environ.get('OAUTH_AZURE_AD_B2C_TENANT_NAME', '')}.b2clogin.com/{os.environ.get('OAUTH_AZURE_AD_B2C_TENANT_ID', '')}/v2.0/"

    def __init__(self):
        self.client_id = os.environ.get("OAUTH_AZURE_AD_B2C_CLIENT_ID")
        self.client_secret = os.environ.get("OAUTH_AZURE_AD_B2C_CLIENT_SECRET")
        self.authorize_params = {
            "p": os.environ.get("OAUTH_AZURE_AD_B2C_POLICY"),
            "response_type": "code",
            "scope": "openid offline_access https://graph.microsoft.com/User.Read",
            "response_mode": "query",
        }

    async def get_token(self, code: str, url: str) -> str:
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": url,
            "scope": "openid offline_access https://graph.microsoft.com/User.Read",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=payload
            )
            response.raise_for_status()
            response_json = response.json()

            token = response_json["id_token"]

            if not token:
                raise HTTPException(
                    status_code=400, detail="Failed to get the access token"
                )

            return token

    async def get_user_info(self, token: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(self.well_known_url)
            response.raise_for_status()
            well_known = response.json()

            print("Printing token: \n\t", token)
            print("Printing well_known: \n", json.dumps(well_known, indent=2))
            key = validate_jwt(token,
                               jwks_uri=well_known["jwks_uri"])
            print("Printing key: \n", key)
            b2c_user = decode_jwt(token,
                                  key,
                                  audience=os.environ.get('OAUTH_AZURE_AD_B2C_CLIENT_ID'),
                                  issuer=self.iss_url)
            print("Printing user object: \n", json.dumps(b2c_user, indent=2))

            try:
                user = User(
                    identifier=b2c_user["emails"][0] if "emails" in b2c_user else b2c_user["email"],
                    metadata={"image": None, "provider": "azure-ad"},
                )
                return b2c_user, user
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail="Failed to get the user info"
                )