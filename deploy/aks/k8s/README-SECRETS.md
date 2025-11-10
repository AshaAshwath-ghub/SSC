# Kubernetes Secrets Setup Guide

## ⚠️ IMPORTANT: Never Commit Secrets to Git!

The `02-secrets.yaml` file contains sensitive API keys and credentials and is **excluded from Git** via `.gitignore`.

---

## Setup Instructions

### 1. Create Your Secrets File

```bash
# Copy the template
cd deploy/aks/k8s
cp 02-secrets.yaml.template 02-secrets.yaml
```

### 2. Fill in Real Values

Edit `02-secrets.yaml` and replace all placeholder values:

#### Required (Must Change):
- `DB_PASSWORD` - Strong PostgreSQL password
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `JWT_SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

#### OAuth Providers (If using social login):
- **Google**: Get from https://console.cloud.google.com/
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`

- **Microsoft**: Get from https://portal.azure.com/
  - `MICROSOFT_CLIENT_ID`
  - `MICROSOFT_CLIENT_SECRET`
  - `MICROSOFT_TENANT`

- **Apple**: Get from https://developer.apple.com/
  - `APPLE_CLIENT_ID`
  - `APPLE_TEAM_ID`
  - `APPLE_KEY_ID`
  - `APPLE_PRIVATE_KEY`

#### MFA Providers (If using):
- **Duo Security**: Get from https://admin.duosecurity.com/
- **SendGrid**: Get from https://app.sendgrid.com/settings/api_keys
- **Twilio**: Get from https://console.twilio.com/

### 3. Update Domain Names

Replace all instances of `yourdomain.com` with your actual domain:

```yaml
GOOGLE_REDIRECT_URI: "https://YOUR_DOMAIN.com/api/v1/oauth/google/callback"
MICROSOFT_REDIRECT_URI: "https://YOUR_DOMAIN.com/api/v1/oauth/microsoft/callback"
```

---

## Deployment Options

### Option 1: Deploy from YAML file (Development)

```bash
kubectl apply -f 02-secrets.yaml
```

### Option 2: Create from Command Line (Production)

```bash
kubectl create secret generic app-secrets \
  --from-literal=DB_PASSWORD='your-strong-password' \
  --from-literal=SECRET_KEY='your-secret-key' \
  --from-literal=JWT_SECRET_KEY='your-jwt-secret' \
  --from-literal=GOOGLE_CLIENT_ID='your-id' \
  --from-literal=GOOGLE_CLIENT_SECRET='your-secret' \
  --namespace=ssc-app
```

### Option 3: Use Azure Key Vault (Recommended for Production)

See Azure Key Vault CSI driver documentation:
https://learn.microsoft.com/en-us/azure/aks/csi-secrets-store-driver

---

## Security Best Practices

1. ✅ **Never commit `02-secrets.yaml` to Git** (already in .gitignore)
2. ✅ **Use strong, randomly generated passwords**
3. ✅ **Rotate secrets regularly** (every 90 days)
4. ✅ **Use different secrets for dev/staging/production**
5. ✅ **Enable Azure Key Vault for production deployments**
6. ✅ **Use RBAC to restrict access to secrets**
7. ✅ **Enable audit logging for secret access**

---

## Verify Secrets Deployment

```bash
# Check if secret exists
kubectl get secret app-secrets -n ssc-app

# View secret keys (not values)
kubectl describe secret app-secrets -n ssc-app

# Decode a specific value (use carefully)
kubectl get secret app-secrets -n ssc-app -o jsonpath='{.data.DB_USER}' | base64 --decode
```

---

## Troubleshooting

### Secret not found
```bash
# List all secrets
kubectl get secrets -n ssc-app

# Create secret if missing
kubectl apply -f 02-secrets.yaml
```

### Update existing secret
```bash
# Delete old secret
kubectl delete secret app-secrets -n ssc-app

# Create new one
kubectl apply -f 02-secrets.yaml
```

### Pods not picking up new secret values
```bash
# Restart deployments
kubectl rollout restart deployment/backend -n ssc-app
kubectl rollout restart deployment/frontend -n ssc-app
```

---

## Emergency: Leaked Secrets

If secrets are accidentally committed to Git:

1. **Immediately rotate ALL compromised credentials**
2. **Remove from Git history** (use BFG Repo-Cleaner or git-filter-repo)
3. **Force push to overwrite history**
4. **Notify security team**
5. **Check for unauthorized access**

---

## Questions?

- Check the main deployment guide: `../PRE-DEPLOYMENT-CHECKLIST.md`
- Review Kubernetes secrets documentation: https://kubernetes.io/docs/concepts/configuration/secret/
- Contact DevOps team for production deployment assistance
