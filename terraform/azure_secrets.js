// Modified Microsoft code example

const { SecretClient } = require("@azure/keyvault-secrets");
const { DefaultAzureCredential } = require("@azure/identity");

async function main() {
  // DefaultAzureCredential automatically uses managed identity in Azure environments.
  // For local development, it uses credentials from Azure CLI, Azure PowerShell, or environment variables.
  // See: https://learn.microsoft.com/javascript/api/@azure/identity/defaultazurecredential
  const credential = new DefaultAzureCredential();

  const keyVaultUrl = "https://kv-deploy-02.vault.azure.net";
  if(!keyVaultUrl) throw new Error("KEY_VAULT_URL is empty");

  const client = new SecretClient(keyVaultUrl, credential);

  // Read the secret we created
  const GROCERY_SECRET_KEY = await client.getSecret("SHOPPING-SECRET-KEY");
  const ADMIN_USERNAME = await client.getSecret("ADMIN-USERNAME");
  const ADMIN_PASSWORD = await client.getSecret("ADMIN-PASSWORD");
  const ADMIN_EMAIL = await client.getSecret("ADMIN-EMAIL");
  console.log(`GROCERY_SECRET_KEY=${GROCERY_SECRET_KEY.value}
ADMIN_USERNAME=${ADMIN_USERNAME.value}
ADMIN_PASSWORD=${ADMIN_PASSWORD.value}
ADMIN_EMAIL=${ADMIN_EMAIL.value}`);
}

main().catch((error) => {
  console.error("An error occurred:", error);
  process.exit(1);
});