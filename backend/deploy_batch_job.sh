#!/bin/bash
# Documentation https://dev.to/petercsiba/using-dockerfilebase-with-flyio-4nfj-temp-slug-3511944

# e.g. deploy_batch_job.sh scraper/fly.toml
SERVICE_PATH=$1

# Set variables
DOCKERFILE="batch_jobs/Dockerfile.base"
# Here `web-scraping-batch-jobs-base-registry` is a dummy app on fly.io I just use for storing base docker images
APP_NAME="web-scraping-batch-jobs-base-registry"
IMAGE_NAME="registry.fly.io/$APP_NAME"
# we do --platform linux/amd64 to match the one fly.io builders have
#   https://github.com/superfly/rchab/blob/8d37d90dc7d418660b50a10f288715fda4a00b5d/build.sh#L7
PLATFORM="linux/amd64"  # or whichever platform Fly.io uses

echo "Logging into fly.io registry"
# Authentication successful. You can now tag and push images to registry.fly.io/{your-app}
fly auth docker

echo "Building batch jobs base image $DOCKERFILE ($PLATFORM) to {$IMAGE_NAME}"

# Build the image locally
docker build --platform $PLATFORM -t $IMAGE_NAME:latest -f $DOCKERFILE .

# Get the image ID (content hash), removing the "sha256:" prefix
IMAGE_ID=$(docker inspect --format='{{.Id}}' $IMAGE_NAME:latest | cut -d: -f2)
echo "Image ID: $IMAGE_ID (content hash)"
FULL_IMAGE_NAME="$IMAGE_NAME:$IMAGE_ID"

# Tag the image with its content hash
docker tag $IMAGE_NAME:latest $FULL_IMAGE_NAME

# Check if the image already exists in the registry
if docker manifest inspect $FULL_IMAGE_NAME > /dev/null 2>&1; then
    echo "Image $FULL_IMAGE_NAME"
    echo " -- already exists in the registry."
    echo " -- Skipping push."
else
    echo "Pushing new image $FULL_IMAGE_NAME to the registry."
    docker push $IMAGE_NAME:$IMAGE_ID
    docker push $IMAGE_NAME:latest
fi

echo "Deploying the batch job $SERVICE_PATH"
# To debug problems with Fly.io app builders you can find them at https://fly.io/dashboard/web-scraping/builders
# or with CLI fly logs -a fly-builder-falling-tree-2202 (or whatever is your builder name printed during the process)
fly deploy --config $SERVICE_PATH
