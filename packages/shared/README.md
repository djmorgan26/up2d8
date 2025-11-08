# Shared Package

Common code shared across all UP2D8 packages.

## Structure

- **types/** - Shared type definitions (Python TypedDict, TypeScript interfaces)
- **schemas/** - Data models and API contracts (Pydantic models, JSON schemas)
- **constants/** - Shared constants (API endpoints, error codes, etc.)
- **utils/** - Common utility functions

## Usage

### Python Packages (backend-api, functions)
```python
from packages.shared.schemas import Article, User
from packages.shared.constants import API_ENDPOINTS
```

### TypeScript/JavaScript (mobile-app)
```typescript
import { Article, User } from '@up2d8/shared/types';
import { API_ENDPOINTS } from '@up2d8/shared/constants';
```

## Adding Shared Code

When you find code duplicated across packages:
1. Extract it to the appropriate subdirectory
2. Update imports in all packages
3. Document the shared component
4. Run tests in all packages to ensure nothing breaks
