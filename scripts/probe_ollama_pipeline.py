"""Measure synthetic API requests without printing document or generated content."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from smoke_stack import login, multipart, request_json, require


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ai-url', default='http://localhost:18000')
    parser.add_argument('--backend-url', help='Exercise seeded USER login and the backend instead of direct AI requests')
    parser.add_argument('--expect', choices=['OLLAMA', 'RULE_BASED'])
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    fixture = root / 'sample_files/resumes/01_data_science_senior.pdf'
    token = login(args.backend_url, 'user@example.test', 'User@123456') if args.backend_url else None
    for endpoint in ('analyze-resume', 'analyze-match'):
        started = time.monotonic()
        body, content_type = multipart(
            {'jobDescription': 'Senior data scientist: Python, SQL, Pandas, scikit-learn, model deployment and stakeholder communication.', 'targetRole': 'Senior Data Scientist'},
            {'file': fixture},
        )
        url = f'{args.backend_url}/api/analyses/{endpoint.removeprefix("analyze-")}' if args.backend_url else f'{args.ai_url}/api/{endpoint}'
        status, result = request_json(url, method='POST', token=token, body=body, content_type=content_type, timeout_seconds=180)
        require(status == (201 if args.backend_url else 200), f'{endpoint}: HTTP {status}')
        if args.backend_url:
            result = result['result']
        metadata = result['ai']
        print(json.dumps({'endpoint': endpoint, 'elapsedSeconds': round(time.monotonic() - started, 2), 'ai': metadata, 'method': result.get('matchBreakdown', {}).get('method')}), flush=True)
        if args.expect:
            require(metadata['provider'] == args.expect, f'{endpoint}: unexpected provider')
            require(metadata['usedFallback'] == (args.expect == 'RULE_BASED'), f'{endpoint}: unexpected fallback metadata')


if __name__ == '__main__':
    main()
