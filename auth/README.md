---
title: 'Injecting Unsupported OAuth Providers into Chainlit for Callback Support'
tags: ['Auth', 'OAuth']
---

# Injecting Unsupported OAuth Providers into Chainlit for Callback Support

This repository provides a step-by-step guide to injecting unsupported OAuth providers into Chainlit for use in existing callback, authentication and logging functionality.

## Simple Function Explanation

The `app.py` in this repository only defines the `@cl.oauth_callback decorator` and the prerequisite `add_custom_oauth_provider` method. The rest of the app logic is intentionally left blank

## Quickstart

I used [Azure AD B2C](https://learn.microsoft.com/en-us/azure/active-directory-b2c/) for my custom provider, so my setup might look different than yours.

See the provided .py files for a direct reference

To get started with integrating your alternative OAuth provider with your Chainlit app, (loosely) follow these steps:

### Prerequisites

- Python ≥ 3.10
- A provisioned auth resource of your choosing

### Step 1: Set up your custom provider override

1. Create your `foobar_provider.py` file
2. In that file, import the following:
```python
import os
import httpx
from fastapi import HTTPException
from chainlit.user import User
from chainlit.oauth_providers import OAuthProvider
import json
```
3. Set up your class and make sure it inherits from the Chainlit base class:
```python
class FooBarProvider(OAuthProvider):
    id="your-id"
    env=["YOUR_ENV_VAR_NAMES"]

    authorize_url=f"https://get.your/auth_url"
    token_url=f"https://get.your/token_url"
    
    def __init__(self):
        self.client_id = os.environ.get("YOUR_ENV_VAR_NAMES")
    
    async def get_token(self, code: str, url: str) -> str:
        payload = { "foo": self.client_id }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=payload
            )
            # do stuff, return a token

    async def get_user_info(self, token: str):
        async with httpx.AsyncClient() as client:
            # do stuff with the token and return a user, User tuple
```


### Step 2: Set up the required environment variables

Keeping in line with how Chainlit supports OAuth providers like Github, Google, and Azure AD, we'll need to set up a few environment variables. For AADB2C, I used the following, but they may change based on need:
```
OAUTH_AZURE_AD_B2C_CLIENT_ID=your b2c application/client ID
OAUTH_AZURE_AD_B2C_CLIENT_SECRET=your b2c client secret
OAUTH_AZURE_AD_B2C_TENANT_ID=your b2c tenant id
OAUTH_AZURE_AD_B2C_TENANT_NAME=your b2c tenant name
OAUTH_AZURE_AD_B2C_REDIRECT_URL=your specified redirect url
OAUTH_AZURE_AD_B2C_POLICY=your policy
```
* Add each of the environment variables you create to the `env` property of your new provider class


### Step 3: Optionally set up JWT validation (recommended)

For security reasons, I recommend validating the JWT returned from get_token. Modify the logic in `validate_jwt.py` as needed. This should work out of the box for AADB2C.


### Step 4: Set up injection logic

Add another file called `inject_custom_auth.py` and add the following, adjusting the env vars as needed:
```python
import os
import secrets
import string
from chainlit.oauth_providers import providers

chars = string.ascii_letters + string.digits + "$%*,-./:=>?@^_~"


# This is the same as the Chainlit `random_secret` method
def random_secret(length: int = 64):
    return "".join((secrets.choice(chars) for i in range(length)))


def custom_oauth_enabled():
    if (os.environ.get('YOUR_ENV_VARS') is not None):
        print("Custom OAuth configured.")
        return True
    else:
        print("Custom OAuth not configured. Skipping...")
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


# This ensures that the provider doesn't get added every time the application reloads.
def add_custom_oauth_provider(provider_id: str, custom_provider_instance):
    if custom_oauth_enabled() and not provider_id_in_instance_list(provider_id):
        providers.append(custom_provider_instance)
        print(f"Added provider: {provider_id}")
    else:
        print(f"Custom OAuth is not enabled or provider {provider_id} already exists")
```

### Step 5: Add the injection step to your `app.py` file

Add the necessary dependencies to your `app.py` file and add a call to the `add_custom_oauth_provider` method. The parameters for the method should be the `id` specified in the provider class and an instance of the class.

i.e.
```python
from cookbook.auth.foobar_oauthprovider import FooBarProvider
from cookbook.auth.inject_custom_auth import add_custom_oauth_provider

add_custom_oauth_provider("foobar", FooBarProvider())

@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  return default_user  
```

The `@cl.oauth_callback` should now work as normal with your new provider.

As of 03/13/2024, the injected provider is also fully supported in Literal.

### Step 6: Set up custom JS and CSS to handle the login page (recommended)

The injected oauth provider doesn't look great on the login page, so I'd recommend overriding the styling on them and adding some JS handling. In your `../public` folder, add a `stylesheet.css` and `script.js` and provide them to your config.toml file as [custom css](https://docs.chainlit.io/customisation/custom-css) and [custom js](https://docs.chainlit.io/customisation/custom-js) files.

Start with the js and styles in the provided documentation, but feel free to customize as needed.
