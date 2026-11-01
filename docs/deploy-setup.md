# Configurar el deploy (una sola vez)

**Hecho el 1 nov por Cabrera.** Queda documentado acá para referencia (p. ej.
si hay que recrearlo o entender el scope de permisos).

El workflow `.github/workflows/cd.yml` despliega a Azure App Service usando OIDC
(sin publish profile, porque la autenticación básica/SCM está deshabilitada en
`cvexpert-ms-cvs`). Esto requiere un Azure AD App Registration
(`gh-actions-cvexpert-ms-cvs`) con federated credentials que confíen en
GitHub Actions para este repo.

```bash
# 1. Crear el App Registration
az ad app create --display-name "gh-actions-cvexpert-ms-cvs"
# Copiar el "appId" de la salida, es el AZURE_CLIENT_ID

APP_ID="<appId de arriba>"
SUBSCRIPTION_ID="<subscription id de rg-cvexpert>"

# 2. Crear el Service Principal asociado
az ad sp create --id "$APP_ID"

# 3. Darle rol de Website Contributor solo sobre cvexpert-ms-cvs (no sobre todo
# el resource group), para que el pipeline no pueda tocar los otros App Services
az role assignment create \
  --assignee "$APP_ID" \
  --role "Website Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-cvexpert/providers/Microsoft.Web/sites/cvexpert-ms-cvs"

# 4. Federated credentials: cd.yml usa `environment: production`, así que el
# subject del token de GitHub es el del environment, no el de push a main —
# hacen falta las dos.
az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-main-deploy",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:SoftwareDesignTEC/cvexpert-ms-cvs:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'
az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-production-environment",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:SoftwareDesignTEC/cvexpert-ms-cvs:environment:production",
  "audiences": ["api://AzureADTokenExchange"]
}'

# 5. Datos para los secrets de GitHub (Settings > Secrets and variables > Actions):
echo "AZURE_CLIENT_ID=$APP_ID"
az account show --query "{AZURE_TENANT_ID:tenantId, AZURE_SUBSCRIPTION_ID:id}" -o json
```

En GitHub (`Settings > Secrets and variables > Actions`) ya están cargados:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

Ninguno de los tres es secreto en el sentido tradicional (son IDs, no
contraseñas) — la seguridad real está en los federated credentials, que solo
confían en tokens de GitHub Actions para este repo exacto (push a `main`, o
el environment `production`).

## Qué hace el pipeline

- `.github/workflows/ci.yml`: lint + pytest en cada PR y push a `main` (ya existía).
- `.github/workflows/cd.yml`: en cada push a `main` que toque `app/`,
  `requirements*.txt` o el propio workflow, corre pruebas de nuevo y si pasan
  despliega a `cvexpert-ms-cvs` vía `az webapp deploy` (zip deploy, Oryx
  instala `requirements.txt` del lado del servidor porque
  `SCM_DO_BUILD_DURING_DEPLOYMENT=true` ya está configurado en el App Service).
- `concurrency` evita que dos deploys corran pisándose si hay pushes seguidos.
