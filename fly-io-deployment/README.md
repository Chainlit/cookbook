Title: Deploy to Fly.io
Tags: [deployment]

# Tutorial repo for deploying to Fly.io

## Quickstart

### Prerequisites

- Python >= 3.8
- A Fly.io account

### Step 1: Install the Fly CLI

Install the Fly CLI to deploy apps using command lines.

For macOS:

```shell
brew install flyctl
```

For other operating systems, follow the [installation guide](https://fly.io/docs/getting-started/installing-flyctl/).

### Step 2: Login to Fly

Sign up and log in to Fly.

```shell
flyctl auth signup
flyctl auth login
```

### Step 3: Run Chainlit App Locally

Test your app locally before deploying.

Clone the example if needed:

```shell
git clone https://github.com/Chainlit/cookbook.git chainlit-cookbook
cd chainlit-cookbook/fly-io-deployment
```

Run your app:

```shell
chainlit run app.py
```

### Step 4: Prepare Procfile and requirements.txt

Create a `Procfile` with the command to start your app:

web: python -m chainlit run app.py -h --port 8080


Ensure you have a `requirements.txt` listing all Python dependencies.

### Step 5: Create Fly Project

Set up a payment method on Fly.io (no charge for the free plan).

Then, create your Fly project:

```shell
flyctl launch
```

Answer "No" to all prompts during setup.

### Step 6: Deploy

Deploy your app:

```shell
flyctl deploy
```

After deployment, set the app instance count to 1:

```shell
flyctl scale count 1
```


This is necessary because Fly.io doesn't support sticky WebSocket sessions by default.

Visit your app at the provided hostname from the `flyctl launch` output.

## Additional Notes

- If you require features like autoscaling and sticky sessions, consider deploying on AWS ECS or GCP with a load balancer that supports these features.
- For detailed deployment steps and troubleshooting, refer to the [blog post](https://dev.to/willydouhard/how-to-deploy-your-chainlit-app-to-flyio-38ja) and check the deployed [example app](https://summer-pond-3349.fly.dev/).

![App running](https://github.com/Chainlit/chainlit/assets/13104895/cbcb8078-ab4d-4e4c-8e4e-7aaa51ca1fd0)


