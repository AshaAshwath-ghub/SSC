# Pre-Deployment Checklist for AKS

## ⚠️ CRITICAL - Update Before Production Deployment

This checklist contains items that MUST be updated before deploying to production.

---

## 1. Security Keys (CRITICAL - Change These!)

### File: `k8s/02-secrets.yaml`

Currently using development values. **MUST CHANGE** for production:

```yaml
# Generate strong keys using:
# python -c "import secrets; print(secrets.token_urlsafe(32))"

SECRET_KEY: "your-secret-key-change-in-production-min-32-chars"
# ⚠️ CHANGE TO: Generate new 32+ character random string

JWT_SECRET_KEY: "your-jwt-secret-key-change-in-production-min-32-chars"
# ⚠️ CHANGE TO: Generate new 32+ character random string
```

**Generate new keys:**
```bash
# For SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# For JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 2. Database Password (CRITICAL - Change This!)

### File: `k8s/02-secrets.yaml`

```yaml
DB_PASSWORD: "postgres"
# ⚠️ CHANGE TO: Strong password with uppercase, lowercase, numbers, symbols
```

**Generate strong password:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

---

## 3. Domain Configuration (Required)

### Files to Update:
- `k8s/01-configmap.yaml`
- `k8s/02-secrets.yaml`
- `k8s/09-ingress.yaml`

**Replace all instances of `yourdomain.com` with your actual domain:**

```bash
# Find all occurrences
grep -r "yourdomain.com" k8s/

# Update in:
# - 01-configmap.yaml: VITE_APP_API_URL, CORS_ORIGINS
# - 02-secrets.yaml: OAuth redirect URIs
# - 09-ingress.yaml: host, tls host
```

**Search and replace:**
```bash
# Example: Replace with your domain
find k8s/ -type f -name "*.yaml" -exec sed -i 's/yourdomain.com/your-actual-domain.com/g' {} +
```

---

## 4. OAuth Redirect URIs (Required for OAuth)

### File: `k8s/02-secrets.yaml`

Update OAuth redirect URIs from localhost to production domain:

```yaml
# Google OAuth
GOOGLE_REDIRECT_URI: "https://yourdomain.com/api/v1/oauth/google/callback"
# ⚠️ Update 'yourdomain.com' to your domain

# Microsoft OAuth
MICROSOFT_REDIRECT_URI: "https://yourdomain.com/api/v1/oauth/microsoft/callback"
# ⚠️ Update 'yourdomain.com' to your domain

# Apple OAuth
APPLE_REDIRECT_URI: "https://yourdomain.com/api/v1/oauth/apple/callback"
# ⚠️ Update 'yourdomain.com' to your domain
```

**Also update in OAuth provider consoles:**
- Google Cloud Console: https://console.cloud.google.com/
- Microsoft Azure Portal: https://portal.azure.com/
- Apple Developer: https://developer.apple.com/

---

## 5. Container Registry Name (Required)

### Files to Update:
- `k8s/07-backend.yaml`
- `k8s/08-frontend.yaml`
- `deploy.sh`

**Replace `sscappregistry` with your ACR name:**

```yaml
# In 07-backend.yaml
image: sscappregistry.azurecr.io/ssc-backend:latest
# ⚠️ Change 'sscappregistry' to your ACR name

# In 08-frontend.yaml
image: sscappregistry.azurecr.io/ssc-frontend:latest
# ⚠️ Change 'sscappregistry' to your ACR name
```

Or set environment variable:
```bash
export ACR_NAME="your-acr-name"
# Then the deploy.sh script will use this
```

---

## 6. Email Configuration (Optional but Recommended)

### File: `k8s/02-secrets.yaml`

```yaml
SENDGRID_FROM_EMAIL: "niteesh.kl@jillellagroup.com"
# ⚠️ Change to your verified sender email

SMTP_FROM_EMAIL: "noreply@yourdomain.com"
# ⚠️ Change to your domain email
```

---

## 7. Resource Configuration (Recommended)

### Files: `k8s/07-backend.yaml`, `k8s/08-frontend.yaml`

Review and adjust based on your workload:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

---

## 8. Storage Size (Optional)

### File: `k8s/03-storage.yaml`

Adjust storage sizes based on data volume:

```yaml
# PostgreSQL
storage: 20Gi  # ⚠️ Adjust based on expected data size

# MongoDB
storage: 20Gi  # ⚠️ Adjust based on expected data size

# Redis
storage: 5Gi   # Usually sufficient
```

---

## 9. SSL/TLS Configuration (Recommended)

### File: `k8s/10-cert-issuer.yaml`

Update email for Let's Encrypt notifications:

```yaml
email: admin@yourdomain.com  # ⚠️ Change to your email
```

---

## 10. CORS Origins (Required)

### File: `k8s/01-configmap.yaml`

Update CORS allowed origins:

```yaml
CORS_ORIGINS: '["https://yourdomain.com","https://www.yourdomain.com"]'
# ⚠️ Add all domains that will access your API
```

---

## 11. Azure Resource Configuration (Required)

### File: `deploy.sh`

Update default values:

```bash
RESOURCE_GROUP="${RESOURCE_GROUP:-ssc-app-rg}"       # ⚠️ Your resource group
CLUSTER_NAME="${CLUSTER_NAME:-ssc-aks-cluster}"     # ⚠️ Your cluster name
ACR_NAME="${ACR_NAME:-sscappregistry}"               # ⚠️ Your ACR name
LOCATION="${LOCATION:-eastus}"                       # ⚠️ Your Azure region
```

---

## 12. API Keys Validation

### File: `k8s/02-secrets.yaml`

Verify all API keys are valid and active:

- ✅ Google OAuth credentials
- ✅ Microsoft OAuth credentials
- ✅ Duo Security keys
- ✅ SendGrid API key
- ✅ Twilio credentials

**Test each service before deployment:**
```bash
# Test SendGrid
curl -X POST https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"personalizations":[{"to":[{"email":"test@example.com"}]}],"from":{"email":"test@example.com"},"subject":"Test","content":[{"type":"text/plain","value":"Test"}]}'

# Test Twilio
curl -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID.json" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"
```

---

## ✅ Final Pre-Deployment Checklist

Before running `./deploy.sh`, ensure:

- [ ] Changed `SECRET_KEY` to strong random value
- [ ] Changed `JWT_SECRET_KEY` to strong random value
- [ ] Changed `DB_PASSWORD` to strong password
- [ ] Replaced all `yourdomain.com` with actual domain
- [ ] Updated ACR name in deployment files
- [ ] Updated OAuth redirect URIs in provider consoles
- [ ] Updated email addresses for notifications
- [ ] Verified all API keys are valid
- [ ] Reviewed resource limits
- [ ] Reviewed storage sizes
- [ ] Updated CORS origins
- [ ] Updated Azure resource names
- [ ] Have DNS access to point domain to Load Balancer IP
- [ ] Backed up current configuration

---

## Post-Deployment Steps

After successful deployment:

1. **Get Load Balancer IP:**
   ```bash
   kubectl get svc -n ingress-nginx
   ```

2. **Configure DNS:**
   - Add A record: `yourdomain.com` → `<Load Balancer IP>`
   - Add A record: `www.yourdomain.com` → `<Load Balancer IP>`

3. **Enable SSL:**
   ```bash
   kubectl apply -f k8s/10-cert-issuer.yaml
   ```

4. **Test OAuth:**
   - Test Google login
   - Test Microsoft login
   - Verify redirect URIs work

5. **Monitor Application:**
   ```bash
   kubectl get pods
   kubectl logs -f deployment/backend
   kubectl logs -f deployment/frontend
   ```

6. **Set up backups:**
   - Database backup jobs
   - Configuration backup to Git
   - Disaster recovery plan

---

## Security Recommendations

### Use Azure Key Vault (Recommended for Production)

Instead of storing secrets in YAML files, use Azure Key Vault:

```bash
# Install CSI driver
helm repo add csi-secrets-store-provider-azure https://azure.github.io/secrets-store-csi-driver-provider-azure/charts
helm install csi csi-secrets-store-provider-azure/csi-secrets-store-provider-azure

# Create Key Vault
az keyvault create --name ssc-app-kv --resource-group $RESOURCE_GROUP --location $LOCATION

# Store secrets in Key Vault
az keyvault secret set --vault-name ssc-app-kv --name db-password --value "your-password"
az keyvault secret set --vault-name ssc-app-kv --name jwt-secret --value "your-jwt-secret"
```

### Network Security

```bash
# Enable network policies
kubectl apply -f k8s/network-policies.yaml

# Restrict database access to backend only
# Configure Azure Firewall rules
# Enable Azure DDoS Protection
```

---

## Support

If you encounter issues:

1. Check pod status: `kubectl get pods`
2. Check pod logs: `kubectl logs <pod-name>`
3. Check events: `kubectl get events --sort-by='.lastTimestamp'`
4. Review documentation: `deploy/aks/ARCHITECTURE.md`
5. Quick reference: `deploy/aks/QUICK-REFERENCE.md`

---

## Notes

- All secrets in `02-secrets.yaml` are currently from development `.env` files
- These are **NOT SAFE** for production use
- Generate new random values for all security keys
- Use strong, unique passwords
- Consider using Azure Key Vault for secret management
- Enable Azure Monitor for logging and alerting
- Set up automated backups
- Test disaster recovery procedures

**DO NOT skip these security steps!**
