# Extract secrets from Azure Key Vault and insert into a .env file to be consumed by Docker

from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

key_vault_name = "kv-deploy-02" # Create this in Azure and create the following secrets
kv_uri = f"https://{key_vault_name}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=kv_uri, credential=credential)

GROCERY_SECRET_KEY = client.get_secret("SHOPPING-SECRET-KEY").value
ADMIN_USERNAME = client.get_secret("ADMIN-USERNAME").value
ADMIN_PASSWORD = client.get_secret("ADMIN-PASSWORD").value
ADMIN_EMAIL = client.get_secret("ADMIN-EMAIL").value
# database_uri = client.get_secret("DATABASE-URI").value

# Open/create .env and dump secrets

with open(".env", "w") as f:
    f.write(f"GROCERY_SECRET_KEY={GROCERY_SECRET_KEY}\n")
    f.write(f"ADMIN_USERNAME={ADMIN_USERNAME}\n")
    f.write(f"ADMIN_PASSWORD={ADMIN_PASSWORD}\n")
    f.write(f"ADMIN_EMAIL={ADMIN_EMAIL}\n")
    # f.write(f"DATABASE_URI={database_uri}\n")