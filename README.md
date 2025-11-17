# Mantis Material React Admin Template

## 🚀 Getting Started

Follow these steps to set up the project:

1. Navigate to your root (full-version / seed) folder

```
c:> cd mantis-material-react
```

2. Install packages

```
npm install
```

3. Run project

```
npm run start
```

## 🆚 Difference Between Full Version and Seed

The <b>full-version</b> of the Mantis Admin Template includes a complete, ready-to-use dashboard with all features, pages, components, and configurations pre-integrated—ideal for production use or exploring the full capabilities of the template.

The <b>seed version</b> offers a minimal setup with only essential dependencies and folder structure, allowing developers to build their project from a clean slate. This version is best suited for those who prefer full control over customization and want to integrate components gradually.

👉 [Refer more here](https://codedthemes.gitbook.io/mantis/integration/seed)

## 🧪 Mock/Fake Backend

We use a mock backend to provide necessary data and handle JWT authentication as well. This mock backend is shared across various apps for consistent data handling. You can check the network tab to trace API calls. You can find the mock backend server in the following GitHub repository:

🔗 GitHub Repo: [MOCK API](https://github.com/phoenixcoded20/mock-data-api-nextjs)

## 👥 Community

Need further help? Reach out to community
<br/>
💬 [Join us on Discord](https://discord.com/invite/p2E2WhCb6s)



##Deploy 

 Step 1: Rebuild Frontend

  cd C:\SSC\SSC\full-version
  docker build --build-arg VITE_APP_API_URL=https://authsecure.internal.jillellagroup.com --build-arg
  VITE_APP_BASE_URL=https://authsecure.internal.jillellagroup.com -t jgacr.azurecr.io/auth-frontend:latest .

  Step 2: Push to ACR

  az acr login --name jgacr
  docker push jgacr.azurecr.io/auth-frontend:latest

  Step 3: Restart Frontend

  kubectl rollout restart deployment auth-frontend -n ssc

  Step 4: Verify

  kubectl get pods -n ssc -l app=auth-frontend

  Once the pod is running, visit:
  https://authsecure.internal.jillellagroup.com/login