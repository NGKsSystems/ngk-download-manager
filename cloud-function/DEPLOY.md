# Cloud Function Deployment Guide

## What This Does
This Cloud Function lets your phone app remotely start/stop your GCE VM and check its status.

## Prerequisites
1. GCP project with Compute Engine enabled
2. gcloud CLI installed
3. Service account with permissions:
   - Compute Instance Admin (v1)
   - Compute Viewer

## Setup Steps

### 1. Set Static IP (Do this first!)

```bash
# Reserve a static IP
gcloud compute addresses create download-manager-ip --region=us-central1

# Get the reserved IP
gcloud compute addresses describe download-manager-ip --region=us-central1

# Assign it to your VM
gcloud compute instances delete-access-config instance-20251120-182738 \
    --zone=us-central1-a \
    --access-config-name="External NAT"

gcloud compute instances add-access-config instance-20251120-182738 \
    --zone=us-central1-a \
    --address=<STATIC_IP_FROM_ABOVE>
```

### 2. Deploy Cloud Function

```bash
cd cloud-function

# Generate a random API key
API_KEY=$(openssl rand -hex 32)
echo "Save this API key: $API_KEY"

# Deploy to GCP
gcloud functions deploy vm-control \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=vm_control \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID,GCP_ZONE=us-central1-a,INSTANCE_NAME=instance-20251120-182738,API_KEY=$API_KEY
```

**Replace `YOUR_PROJECT_ID` with your actual GCP project ID!**

### 3. Get Function URL

```bash
gcloud functions describe vm-control --region=us-central1 --gen2
```

Look for `url:` in the output. This is your Cloud Function endpoint.

Example: `https://us-central1-YOUR_PROJECT.cloudfunctions.net/vm-control`

## Testing

### Start VM
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  https://YOUR_FUNCTION_URL/start-vm
```

### Check Status
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://YOUR_FUNCTION_URL/vm-status
```

### Stop VM
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  https://YOUR_FUNCTION_URL/stop-vm
```

## Configuration for Mobile App

Save these values for the mobile app:
- **Cloud Function URL**: `https://...cloudfunctions.net/vm-control`
- **API Key**: (the generated key)
- **Static VM IP**: (from step 1)

## Security Notes

- API key is stored as environment variable in Cloud Function (not in code)
- Never commit the API key to git
- Mobile app will send API key in Authorization header
- Cloud Function has CORS enabled for mobile access

## Costs

- **Cloud Function**: ~$0.40 per million requests
- **Static IP**: ~$1.46/month while VM is stopped, FREE while running
- Very cheap for personal use!

## Troubleshooting

### "Permission denied" error
```bash
# Grant your user account permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member=user:YOUR_EMAIL@gmail.com \
    --role=roles/compute.instanceAdmin.v1
```

### Function timeout
Increase timeout:
```bash
gcloud functions deploy vm-control --timeout=60s [... other flags ...]
```

### Check logs
```bash
gcloud functions logs read vm-control --region=us-central1 --limit=50
```
