# QA Test Planner Agent

![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![Google ADK](https://img.shields.io/badge/Built%20with-Google%20ADK-green)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)

> **⚠️ DISCLAIMER: THIS IS NOT AN OFFICIALLY SUPPORTED GOOGLE PRODUCT. THIS PROJECT IS INTENDED FOR DEMONSTRATION PURPOSES ONLY. IT IS NOT INTENDED FOR USE IN A PRODUCTION ENVIRONMENT.**

## Overview

The QA Test Planner Agent is an intelligent assistant built with the Google Agent Development Kit (ADK) combined with Gemini Flash 2.5 Thinking capabilities to streamline the test planning process for software development teams. This AI-powered agent bridges the gap between product requirements and quality assurance by automatically analyzing PRDs from Confluence and generating comprehensive test plans in a Jira Xray compatible format.

### Why Use QA Test Planner Agent?

- **Save Time**: Reduce the manual effort of creating test plans from product requirements
- **Improve Coverage**: AI-powered analysis helps identify testing scenarios that might be overlooked
- **Standardize Process**: Generate consistent test plan formats that integrate with your existing tools

## Features

- **🔍 Search Confluence**: Easily search for and retrieve Product Requirement Documents (PRDs) and other relevant documents within your Confluence space
- **📊 Document Evaluation**: Get AI expert analysis of PRDs with suggestions for areas needing clarification or improvement
- **📝 Test Plan Generation**: Create detailed test plans in a Jira Xray compatible format (Markdown table) ready for implementation

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) - An extremely fast Python package installer and resolver
- Atlassian Confluence account with API access, with a space that contains Product Requirement Documents (PRDs)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/qa-test-planner-agent.git
   cd qa-test-planner-agent
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

### Configuration

The agent requires credentials to access Confluence. These are managed via a `.env` file inside the `qa_test_planner` directory.

1. Rename qa_test_planner_example to qa_test_planner directory and copy the .env.example file to .env

2. **Add the following environment variables** to the `.env` file with your Confluence details:

   ```env
   CONFLUENCE_URL="https://your-domain.atlassian.net"
   CONFLUENCE_USERNAME="your-email@example.com"
   CONFLUENCE_TOKEN="your-confluence-api-token"
   CONFLUENCE_PRD_SPACE_ID="YOUR_PRD_SPACE_ID"
   ```

   - `CONFLUENCE_URL`: The URL of your Confluence instance
   - `CONFLUENCE_USERNAME`: Your email address for Confluence
   - `CONFLUENCE_TOKEN`: Your Confluence API token (generate one [here](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/))
   - `CONFLUENCE_PRD_SPACE_ID`: The ID of the Confluence space containing your PRDs

## Usage

Start the agent with the following command from the project root:

```bash
uv run adk web
```

This will initialize the agent and launch a web interface where you can:

1. **Search for PRDs** by title, content, or other criteria
2. **View and analyze** document content with AI assistance
3. **Generate test plans** based on the selected PRD
4. **Export** the resulting test plan as CSV

## Example Workflow

1. Start the agent using `uv run adk web`
2. In the web UI, search for a specific PRD by name or content
3. Review the PRD with AI-generated insights
4. Request a test plan generation
5. Export the test plan as CSV

## Deployment to Cloud Run

gcloud run deploy qa-test-planner-agent \
                  --source . \
                  --port 8080 \
                  --project {YOUR_PROJECT_ID} \
                  --allow-unauthenticated \
                  --region us-central1 \
                  --update-env-vars GOOGLE_GENAI_USE_VERTEXAI=1 \
                  --update-env-vars GOOGLE_CLOUD_PROJECT={YOUR_PROJECT_ID} \
                  --update-env-vars GOOGLE_CLOUD_LOCATION=global \
                  --update-env-vars CONFLUENCE_URL={YOUR_CONFLUENCE_URL} \
                  --update-env-vars CONFLUENCE_USERNAME={YOUR_CONFLUENCE_USERNAME} \
                  --update-env-vars CONFLUENCE_TOKEN={YOUR_CONFLUENCE_TOKEN} \
                  --update-env-vars CONFLUENCE_PRD_SPACE_ID={YOUR_PRD_SPACE_ID} \
                  --memory 1G
