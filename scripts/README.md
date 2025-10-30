# Scripts Directory

This directory contains utility and test scripts for the UP2D8 project.

## Structure

```
scripts/
├── tests/           # Test scripts for different features
│   ├── test_analytics.sh
│   ├── test_analytics_e2e.sh
│   ├── test_complete_system.sh
│   ├── test_digest.sh
│   ├── test_feedback_final.sh
│   ├── test_feedback_simple.sh
│   ├── test_feedback_system.sh
│   ├── test_rag_python.py
│   ├── test_rag_quick.sh
│   ├── test_rag_system.sh
│   ├── test_scheduled_digests.sh
│   ├── test_scraping.sh
│   └── test_techcrunch.sh
│
└── utils/           # Utility scripts
    ├── check_articles.sh
    ├── create_test_user.sh
    └── fix_analytics.py
```

## Test Scripts

All test scripts are located in `scripts/tests/` and are used for manual testing and validation of various features:

- **Analytics Tests**: `test_analytics.sh`, `test_analytics_e2e.sh`
- **Complete System**: `test_complete_system.sh` - Full end-to-end system test
- **Digest Tests**: `test_digest.sh`, `test_scheduled_digests.sh`
- **Feedback System**: `test_feedback_*.sh`
- **RAG/Chat Tests**: `test_rag_*.sh`
- **Scraping Tests**: `test_scraping.sh`, `test_techcrunch.sh`

## Utility Scripts

Utility scripts in `scripts/utils/` help with common development tasks:

- `check_articles.sh` - Check article database state
- `create_test_user.sh` - Create test users for development
- `fix_analytics.py` - Fix analytics data issues

## Usage

All scripts should be run from the repository root:

```bash
# Run a test script
./scripts/tests/test_scraping.sh

# Run a utility script
./scripts/utils/create_test_user.sh
```

Make sure scripts have execute permissions:

```bash
chmod +x scripts/tests/*.sh
chmod +x scripts/utils/*.sh
```

## Notes

- These scripts are for development and testing only
- For automated testing, use `pytest` in `backend/tests/`
- Some scripts may require the backend to be running
- Check individual scripts for specific requirements
