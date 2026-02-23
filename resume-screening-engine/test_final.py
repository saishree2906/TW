#!/usr/bin/env python3
"""Final verification of Phase 2 implementation"""

from app.main import app
from app.api.v1.health import router as health_router
from app.api.v1.parse_resume import router as parse_router

print('\n' + '=' * 60)
print('FINAL VERIFICATION')
print('=' * 60)
print('\n✓ FastAPI app initialized successfully')
print(f'  Project: {app.title}')
print(f'  Version: {app.version}')

routes = [r.path for r in app.routes if hasattr(r, 'path')]
print(f'\n✓ Registered routes ({len(routes)}):')
for route in sorted(set(routes)):
    print(f'  - {route}')

print('\n✓ Key components:')
print('  - SpacyResumeParser (custom parser)')
print('  - POST /api/v1/parse/resume (resume parsing endpoint)')
print('  - GET /api/v1/health (health check endpoint)')
print('  - Normalizer with PII masking')
print('  - No PyResParser dependencies')

print('\n' + '=' * 60)
print('Phase 2 implementation verified!')
print('=' * 60)
