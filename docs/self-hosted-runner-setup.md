# Self-Hosted Runner Setup Guide

This guide explains how to set up a self-hosted runner for the V-AGI repository to enable GitHub Actions without requiring a paid GitHub plan.

## Why Self-Hosted Runners?

Private repositories on GitHub Free have limited or no access to GitHub-hosted runners. Self-hosted runners provide:
- Free CI/CD execution
- Full control over the build environment
- Ability to run on your own infrastructure

## Prerequisites

- A server (physical, VM, or cloud instance) with:
  - Linux (Ubuntu 20.04+ recommended)
  - At least 2 CPU cores
  - At least 4GB RAM
  - 20GB+ disk space
- Network access to GitHub

## Quick Setup

### 1. Create a Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Create a new token with `repo` scope
3. Save the token for later use

### 2. Register the Runner

1. Go to the repository: `https://github.com/vantisCorp/V-AGI/settings/actions/runners/new`
2. Select "New self-hosted runner"
3. Choose "Linux" as the operating system
4. Follow the commands shown on the page

### 3. Install and Configure

```bash
# Create a directory for the runner
mkdir -p ~/actions-runner && cd ~/actions-runner

# Download the latest runner package
curl -o actions-runner-linux-x64-2.321.0.tar.gz \
  https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-x64-2.321.0.tar.gz

# Extract the installer
tar xzf ./actions-runner-linux-x64-2.321.0.tar.gz

# Configure the runner (use the token from step 1)
./config.sh --url https://github.com/vantisCorp/V-AGI \
  --token YOUR_RUNNER_TOKEN

# Install the runner as a service
sudo ./svc.sh install

# Start the service
sudo ./svc.sh start
```

### 4. Verify the Runner

Check that the runner is online:
- Go to `https://github.com/vantisCorp/V-AGI/settings/actions/runners`
- The runner should show as "Online"

## Using the Self-Hosted Runner

The CI workflow is configured to use `ubuntu-latest` by default. To use your self-hosted runner, update the workflow:

```yaml
jobs:
  test:
    runs-on: self-hosted  # Change from ubuntu-latest
```

## Security Considerations

- Self-hosted runners have access to your infrastructure
- Only run workflows from trusted sources
- Consider using runner groups to limit access
- Regularly update the runner software

## Alternative: Make Repository Public

If your project can be open-source:
1. Go to repository Settings
2. Scroll to "Danger Zone"
3. Click "Change visibility"
4. Select "Public"

Public repositories get free GitHub Actions minutes.

## Troubleshooting

### Runner not picking up jobs
- Check the runner is online in Settings → Actions → Runners
- Verify the runner labels match the workflow `runs-on` value

### Job fails immediately
- Check runner logs: `~/actions-runner/_diag/Runner_*.log`
- Ensure the runner has Docker installed if using container jobs

### Permission denied errors
- Ensure the runner user has appropriate permissions
- Check file ownership in the workspace directory