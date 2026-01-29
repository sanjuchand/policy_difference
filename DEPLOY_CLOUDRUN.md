# Deploy Policy Diff to Google Cloud Run

This guide walks you through deploying the Policy Diff application to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account**
   - Sign up at https://cloud.google.com/
   - New accounts get $300 free credit for 90 days
   - Free tier continues after trial ends

2. **Install Google Cloud SDK**
   ```bash
   # macOS (using Homebrew)
   brew install --cask google-cloud-sdk

   # Or download from:
   # https://cloud.google.com/sdk/docs/install
   ```

3. **Authenticate**
   ```bash
   gcloud auth login
   ```

## Quick Deployment (Automated)

### Step 1: Create a Google Cloud Project

```bash
# Create new project (or use existing)
export PROJECT_ID="policy-diff-$(date +%s)"
gcloud projects create $PROJECT_ID --name="Policy Diff Analyzer"

# Set as active project
gcloud config set project $PROJECT_ID

# Link billing account (required for Cloud Run)
# Go to: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID
# Or use: gcloud billing accounts list
# Then: gcloud billing projects link $PROJECT_ID --billing-account=ACCOUNT_ID
```

### Step 2: Run Deployment Script

```bash
# Make script executable
chmod +x deploy-cloudrun.sh

# Deploy (will take 5-10 minutes first time)
./deploy-cloudrun.sh
```

The script will:
- Enable required Google Cloud APIs
- Build Docker container (~2.5GB with all ML dependencies)
- Deploy to Cloud Run
- Output your live URL

## Manual Deployment (Step by Step)

If you prefer manual control:

### 1. Set Configuration
```bash
export PROJECT_ID="your-project-id"
export SERVICE_NAME="policy-diff-analyzer"
export REGION="us-central1"
```

### 2. Enable APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Build Container
```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
```

**Note:** First build takes ~10 minutes due to ML dependencies. Subsequent builds are faster (cached layers).

### 4. Deploy to Cloud Run
```bash
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300s \
  --max-instances 10 \
  --allow-unauthenticated \
  --port 8080
```

### 5. Get Your URL
```bash
gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)'
```

## Configuration Details

### Resource Allocation

| Resource | Value | Reason |
|----------|-------|--------|
| **Memory** | 4Gi | ML models (spaCy, transformers) need 2-3GB |
| **CPU** | 2 vCPU | Faster PDF processing and embedding generation |
| **Timeout** | 300s | Large PDFs can take 1-2 minutes to process |
| **Max Instances** | 10 | Limit concurrent costs |

### Cost Optimization

To reduce costs, adjust in `deploy-cloudrun.sh`:

**For light usage:**
```bash
MEMORY="2Gi"     # Reduce to 2GB
CPU="1"          # Use 1 vCPU
MAX_INSTANCES="3" # Limit scaling
```

**For demo/testing only:**
```bash
MEMORY="2Gi"
CPU="1"
MAX_INSTANCES="1"  # No scaling
--min-instances=0  # Scale to zero when idle
```

## Updating Your Deployment

After making code changes:

```bash
# Option 1: Use deployment script
./deploy-cloudrun.sh

# Option 2: Manual update
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --region $REGION
```

## Features Available

✅ **Working:**
- PDF parsing and text extraction
- Document chunking (paragraph/sentence/section)
- PII detection and tokenization (Presidio + spaCy)
- Embedding-based semantic similarity
- Text diff with significance scoring
- HTML and JSON report generation

❌ **Not Available:**
- LLM semantic analysis (requires Ollama server - not included)

## Monitoring & Logs

### View Logs
```bash
# Stream logs in real-time
gcloud run services logs tail $SERVICE_NAME --region $REGION

# View in console
https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/logs
```

### Monitor Costs
```bash
# View billing
https://console.cloud.google.com/billing

# Set budget alerts (recommended!)
https://console.cloud.google.com/billing/budgets
```

### Recommended Budget Alert
1. Go to Billing → Budgets & Alerts
2. Set budget: $20/month
3. Set alerts at: 50%, 90%, 100%

## Troubleshooting

### Build Fails: "Out of memory"
Increase Cloud Build machine type:
```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --machine-type=n1-highcpu-8
```

### Cold Start is Slow
First request after idle takes 30-60 seconds (loading ML models). Options:
1. Keep warm with min-instances: `--min-instances=1` (costs ~$10-15/month)
2. Accept cold starts (free)

### Deployment Times Out
Increase timeout in Cloud Build:
```bash
gcloud builds submit --timeout=20m --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
```

### Container is Too Large
Current image: ~2.5GB (acceptable for Cloud Run). If needed to reduce:
1. Use smaller spaCy model: `en_core_web_sm` instead of `en_core_web_lg`
2. Remove chromadb if not using RAG features

## Security

### Make Service Private
Remove `--allow-unauthenticated` and require authentication:
```bash
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --region $REGION \
  --no-allow-unauthenticated
```

Then access with:
```bash
gcloud run services proxy $SERVICE_NAME --region $REGION
```

### Add Custom Domain
```bash
gcloud run domain-mappings create \
  --service $SERVICE_NAME \
  --domain your-domain.com \
  --region $REGION
```

## Clean Up (Delete Everything)

```bash
# Delete Cloud Run service
gcloud run services delete $SERVICE_NAME --region $REGION

# Delete container images
gcloud container images delete gcr.io/$PROJECT_ID/$SERVICE_NAME

# Delete entire project (careful!)
gcloud projects delete $PROJECT_ID
```

## Support

- **Cloud Run Docs:** https://cloud.google.com/run/docs
- **Pricing Calculator:** https://cloud.google.com/products/calculator
- **Free Tier:** https://cloud.google.com/free

## Estimated Costs

Based on your usage pattern:

| Usage Level | Comparisons/Month | Est. Cost |
|-------------|-------------------|-----------|
| **Light** | 300 (10/day) | **$0** (free tier) |
| **Medium** | 3,000 (100/day) | **$0** (free tier) |
| **Heavy** | 30,000 (1,000/day) | **~$12/month** |
| **Very Heavy** | 100,000+ | **~$40-60/month** |

**Free tier covers:**
- 2 million requests/month
- 180,000 vCPU-seconds (50 hours)
- 360,000 GiB-seconds (100 hours at 1GB)

Most users stay within free tier!
