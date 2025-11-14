# API Configuration

This directory contains API configuration files needed for the article search functionality.

## Setup Instructions

### 1. Scopus API Key

1. Copy `ScopusAPI.template.md` to `ScopusAPI.md`
2. Replace `[YOUR_SCOPUS_API_KEY_HERE]` with your actual Scopus API key
3. Replace `[YOUR_INSTTOKEN_HERE]` with your actual Scopus insttoken

### 2. Semantic Scholar API Key

1. Copy `SemanticAPI.template.md` to `SemanticAPI.md`
2. Replace `[YOUR_SEMANTIC_SCHOLAR_API_KEY_HERE]` with your actual Semantic Scholar API key

### 3. Environment Variables (Alternative Method)

You can also set API keys as environment variables:

```bash
export SCOPUS_API_KEY="your_scopus_api_key"
export SCOPUS_INSTTOKEN="your_scopus_insttoken"
export SEMANTIC_API_KEY="your_semantic_scholar_api_key"
```

## Security Note

⚠️ **Never commit actual API keys to the repository!**

The `.gitignore` file is configured to ignore `*API.md` files to prevent accidental commits of sensitive information. Only the template files (`*API.template.md`) should be committed.
