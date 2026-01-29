#!/bin/bash

# Google Cloud Run Deployment Script for Policy Diff
# This script automates the deployment process to Google Cloud Run

set -e  # Exit on error

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-policy-diff}"  # Replace with your project ID
SERVICE_NAME="policy-diff-analyzer"
REGION="${REGION:-us-central1}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
MEMORY="4Gi"  # 4GB memory for ML models
CPU="2"       # 2 vCPUs
TIMEOUT="300s" # 5 minutes timeout for processing large PDFs
MAX_INSTANCES="10"

echo "🚀 Deploying Policy Diff to Google Cloud Run"
echo "============================================="
echo "Project ID: ${PROJECT_ID}"
echo "Service Name: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "❌ Error: Not authenticated with gcloud."
    echo "Run: gcloud auth login"
    exit 1
fi

# Set project
echo "📝 Setting project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com

# Build container image
echo "🏗️  Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --memory ${MEMORY} \
    --cpu ${CPU} \
    --timeout ${TIMEOUT} \
    --max-instances ${MAX_INSTANCES} \
    --allow-unauthenticated \
    --port 8080

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo "============================================="
echo "🌐 Your app is live at:"
echo "   ${SERVICE_URL}"
echo ""
echo "📊 Monitor your service:"
echo "   https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}"
echo ""
echo "💰 View costs:"
echo "   https://console.cloud.google.com/billing"
echo ""
