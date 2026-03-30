"""
AI-powered code summarization using SAP AI Core
"""

import os
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional


class AISummarizer:
    """Generate AI-powered summaries of code and architecture using SAP AI Core"""

    def __init__(self,
                 auth_url: Optional[str] = None,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 base_url: Optional[str] = None,
                 resource_group: Optional[str] = None):
        """
        Initialize AI summarizer with SAP AI Core credentials

        Args:
            auth_url: SAP AI Core auth URL (defaults to AICORE_AUTH_URL env var)
            client_id: Client ID (defaults to AICORE_CLIENT_ID env var)
            client_secret: Client secret (defaults to AICORE_CLIENT_SECRET env var)
            base_url: API base URL (defaults to AICORE_BASE_URL env var)
            resource_group: Resource group (defaults to AICORE_RESOURCE_GROUP env var)
        """
        self.auth_url = auth_url or os.environ.get('AICORE_AUTH_URL')
        self.client_id = client_id or os.environ.get('AICORE_CLIENT_ID')
        self.client_secret = client_secret or os.environ.get('AICORE_CLIENT_SECRET')
        self.base_url = base_url or os.environ.get('AICORE_BASE_URL')
        self.resource_group = resource_group or os.environ.get('AICORE_RESOURCE_GROUP', 'default')

        # Validate required credentials
        if not all([self.auth_url, self.client_id, self.client_secret, self.base_url]):
            raise ValueError(
                "Missing SAP AI Core credentials. Required env vars: "
                "AICORE_AUTH_URL, AICORE_CLIENT_ID, AICORE_CLIENT_SECRET, AICORE_BASE_URL"
            )

        self.access_token = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with SAP AI Core and get access token"""
        try:
            response = requests.post(
                f"{self.auth_url}/oauth/token",
                auth=(self.client_id, self.client_secret),
                data={'grant_type': 'client_credentials'},
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            self.access_token = response.json()['access_token']
        except Exception as e:
            raise RuntimeError(f"Failed to authenticate with SAP AI Core: {e}")

    def _call_llm(self, prompt: str, max_tokens: int = 1024) -> str:
        """
        Call SAP AI Core LLM endpoint

        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response

        Returns:
            Generated text response
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'AI-Resource-Group': self.resource_group,
            'Content-Type': 'application/json'
        }

        # SAP AI Core typically uses OpenAI-compatible format
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        try:
            # Adjust endpoint based on your SAP AI Core deployment
            # Common patterns: /v2/inference/deployments/{deployment_id}/chat/completions
            response = requests.post(
                f"{self.base_url}/v2/inference/deployments/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            # Extract text from response (adjust based on actual API format)
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                raise ValueError(f"Unexpected response format: {result}")

        except Exception as e:
            print(f"Warning: LLM call failed: {e}")
            raise

    def summarize_codebase(self, analysis_result: Dict) -> Dict[str, Dict]:
        """
        Generate summaries for all files in the codebase

        Args:
            analysis_result: Output from CodebaseAnalyzer

        Returns:
            Dict mapping file paths to summary data
        """
        summaries = {}

        # Generate project overview
        project_summary = self._generate_project_summary(analysis_result)
        summaries['_project_overview'] = project_summary

        # Generate file summaries
        for file_data in analysis_result['files'][:20]:  # Limit for MVP
            file_path = file_data['path']
            try:
                summary = self._generate_file_summary(file_data, analysis_result)
                summaries[file_path] = summary
            except Exception as e:
                print(f"Warning: Failed to summarize {file_path}: {e}")
                summaries[file_path] = {'error': str(e)}

        # Generate glossary
        glossary = self._generate_glossary(analysis_result)
        summaries['_glossary'] = glossary

        return summaries

    def _generate_project_summary(self, analysis_result: Dict) -> Dict:
        """Generate high-level project overview"""
        prompt = f"""Analyze this codebase and provide a concise summary:

Project: {Path(analysis_result['project_path']).name}
Files: {analysis_result['file_count']}
Tech Stack: {', '.join(analysis_result['tech_stack'])}

Structure:
{analysis_result['structure']}

Provide:
1. What this project does (2-3 sentences)
2. Main components and their purpose
3. Key architectural patterns

Be concise and focus on helping a new developer understand the project quickly."""

        response_text = self._call_llm(prompt, max_tokens=1024)

        return {
            'summary': response_text,
            'tech_stack': analysis_result['tech_stack'],
            'file_count': analysis_result['file_count']
        }

    def _generate_file_summary(self, file_data: Dict, analysis_result: Dict) -> Dict:
        """Generate summary for a single file"""
        # Read file content
        try:
            with open(file_data['path'], 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()[:4000]  # Limit content size
        except Exception:
            content = "[Could not read file content]"

        prompt = f"""Analyze this code file and explain it clearly:

File: {file_data['name']}
Extension: {file_data['extension']}
Lines: {file_data['lines']}
Classes: {[c['name'] for c in file_data.get('classes', [])]}
Functions: {[f['name'] for f in file_data.get('functions', [])]}

Code excerpt:
```
{content[:2000]}
```

Provide:
1. One-line summary (what this file does)
2. Why this file exists (its role in the project)
3. Key functions/classes and their purpose
4. Any important logic or patterns

Be concise - aim for 3-4 sentences total."""

        response_text = self._call_llm(prompt, max_tokens=512)

        return {
            'summary': response_text,
            'classes': file_data.get('classes', []),
            'functions': file_data.get('functions', []),
            'imports': file_data.get('imports', [])
        }

    def _generate_glossary(self, analysis_result: Dict) -> Dict:
        """Generate glossary of key terms"""
        terms = analysis_result.get('glossary_terms', {})
        tech_stack = analysis_result.get('tech_stack', [])

        # Combine terms
        all_terms = list(terms.keys())[:30]  # Limit terms

        if not all_terms:
            return {'terms': {}}

        prompt = f"""Create a glossary for this codebase.

Project uses: {', '.join(tech_stack)}
Key terms found: {', '.join(all_terms[:20])}

For each important term, provide:
- A clear, concise definition (1 sentence)
- Why it matters in this project

Focus on terms a new developer would need to know.
Format as: Term: Definition

Provide definitions for the 10 most important terms."""

        response_text = self._call_llm(prompt, max_tokens=1024)

        return {
            'definitions': response_text,
            'tech_stack_terms': tech_stack
        }
