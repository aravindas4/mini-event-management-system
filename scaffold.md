# Domain-Driven Development Project Structure Template

This document provides a comprehensive template for setting up a modularized codebase following Domain-Driven Development (DDD) principles, based on the UrbanPiper Billing Service architecture.

## 📁 Project Structure Overview

```
project-root/
├── app/                              # Main application code
│   ├── __init__.py
│   ├── base/                         # Shared base classes and utilities
│   │   ├── __init__.py
│   │   ├── controllers/              # Base HTTP controllers
│   │   │   └── base_controller.py
│   │   ├── models/                   # Base domain models
│   │   │   ├── base_model.py
│   │   │   └── mysql_base.py
│   │   ├── repositories/             # Base repository patterns
│   │   │   └── base_repository.py
│   │   ├── requests/                 # Base request DTOs
│   │   │   ├── __init__.py
│   │   │   └── base_request.py
│   │   └── responses/                # Base response DTOs
│   │       └── base_response.py
│   │
│   ├── core/                         # Core application infrastructure
│   │   ├── __init__.py
│   │   ├── api/                      # HTTP API utilities
│   │   │   └── base_http_api.py
│   │   ├── constants/                # Application constants
│   │   │   └── app_constants.py
│   │   ├── context/                  # Application context
│   │   │   ├── __init__.py
│   │   │   └── context.py
│   │   ├── database.py               # Database connection setup
│   │   ├── enums/                    # Application-level enums
│   │   │   └── app.py
│   │   ├── exception_handlers.py     # Global exception handlers
│   │   ├── middlewares/              # HTTP middlewares
│   │   │   ├── exception_handling_middleware.py
│   │   │   └── request_logging_middleware.py
│   │   ├── schemas/                  # Core schemas
│   │   │   └── user_identity_headers.py
│   │   ├── services/                 # Core services
│   │   │   └── http_service.py
│   │   └── utils/                    # Utilities
│   │       └── user_identity_headers.py
│   │
│   ├── exceptions/                   # Custom exceptions
│   │   ├── __init__.py
│   │   ├── Enums/
│   │   │   └── exception_codes.py
│   │   ├── base_exception.py
│   │   ├── client_exception.py
│   │   ├── forbidden_exception.py
│   │   ├── invariant_violation_exception.py
│   │   ├── not_found_exception.py
│   │   ├── rate_limit_exception.py
│   │   ├── server_exception.py
│   │   ├── unauthorized_exception.py
│   │   └── validation_exception.py
│   │
│   ├── [domain_name]/               # Domain-specific modules (e.g., invoicing, user_management)
│   │   ├── __init__.py
│   │   ├── actions/                  # Domain actions/use cases
│   │   │   ├── __init__.py
│   │   │   ├── create_entity_action.py
│   │   │   └── update_entity_action.py
│   │   ├── controllers/              # HTTP controllers
│   │   │   └── entity_controller.py
│   │   ├── enums/                    # Domain-specific enums
│   │   │   ├── __init__.py
│   │   │   └── entity_status_enum.py
│   │   ├── models/                   # Domain models
│   │   │   ├── __init__.py
│   │   │   └── entity.py
│   │   ├── repositories/             # Data access layer
│   │   │   ├── __init__.py
│   │   │   └── entity_repository.py
│   │   ├── requests/                 # Request DTOs
│   │   │   └── create_entity_request.py
│   │   ├── responses/                # Response DTOs
│   │   │   └── entity_response.py
│   │   ├── routes.py                 # FastAPI routes
│   │   ├── schemas/                  # Data transfer objects
│   │   │   ├── __init__.py
│   │   │   └── entity_dto.py
│   │   └── services/                 # Domain services
│   │       ├── __init__.py
│   │       └── entity_service.py
│   │
│   └── [integration_name]/           # External integrations (e.g., zenskar, stripe)
│       ├── __init__.py
│       ├── actions/                  # Integration actions
│       │   ├── __init__.py
│       │   └── process_webhook_action.py
│       ├── api/                      # API clients
│       │   ├── base_api.py
│       │   └── integration_api.py
│       ├── controllers/              # Integration controllers
│       │   ├── __init__.py
│       │   └── webhook_controller.py
│       ├── models/                   # Integration models
│       │   ├── __init__.py
│       │   └── webhook_log.py
│       ├── repositories/             # Integration repositories
│       │   └── __init__.py
│       ├── responses/                # Integration responses
│       │   ├── __init__.py
│       │   └── webhook_response.py
│       ├── routes.py                 # Integration routes
│       ├── schemas/                  # Integration schemas
│       │   ├── __init__.py
│       │   └── webhook_dto.py
│       └── services/                 # Integration services
│           ├── __init__.py
│           └── integration_service.py
│
├── config/                           # Configuration management
│   ├── __init__.py
│   ├── app.py                        # Application settings
│   ├── caching.py                    # Cache configuration
│   ├── database.py                   # Database settings
│   ├── logging.py                    # Logging configuration
│   ├── sentry.py                     # Error monitoring
│   ├── settings.py                   # Main settings aggregator
│   └── [integration_name].py         # Integration-specific config
│
├── docker/                           # Docker configuration
│   └── entrypoint.sh                 # Container entrypoint
│
├── docs/                             # Documentation
│   ├── README.md
│   └── getting-started.md
│
├── migrations/                       # Database migrations
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── migration_files.py
│
├── tests/                            # Test suite
│   ├── conftest.py                   # Test configuration
│   ├── e2e/                          # End-to-end tests
│   │   ├── __init__.py
│   │   └── test_entity_e2e.py
│   ├── fixtures/                     # Test fixtures
│   │   ├── database.py
│   │   └── domains/
│   │       └── [domain_name]/
│   │           └── factories/
│   │               └── entity_factory.py
│   ├── test_health.py                # Health check tests
│   └── unit/                         # Unit tests
│       ├── [domain_name]/
│       │   ├── test_entity_actions.py
│       │   ├── test_entity_model.py
│       │   └── test_entity_service.py
│       └── [integration_name]/
│           └── test_integration_service.py
│
├── Dockerfile                        # Docker image definition
├── README.md                         # Project documentation
├── alembic.ini                       # Database migration config
├── codecov.yml                       # Code coverage config
├── main.py                           # FastAPI application entry point
├── pyproject.toml                    # Python project configuration
├── pytest.ini                        # Test configuration
├── requirements.txt                  # Production dependencies
├── requirements-dev.txt              # Development dependencies
└── version.py                        # Version management
```

## 🏗️ Architecture Principles

### 1. Domain-Driven Design (DDD)
- **Domain Separation**: Each business domain has its own module
- **Bounded Contexts**: Clear boundaries between domains
- **Domain Services**: Business logic encapsulated in services
- **Repository Pattern**: Data access abstraction

### 2. Layered Architecture
- **Presentation Layer**: Controllers and routes
- **Application Layer**: Actions and services
- **Domain Layer**: Models and business logic
- **Infrastructure Layer**: Repositories and external APIs

### 3. Clean Architecture
- **Dependency Inversion**: Abstract dependencies through interfaces
- **Separation of Concerns**: Each layer has specific responsibilities
- **Testability**: Easy to unit test individual components

## 📋 Implementation Guidelines

### Setting up a New Domain

1. **Create Domain Directory Structure**
```bash
mkdir -p app/your_domain/{actions,controllers,enums,models,repositories,requests,responses,schemas,services}
touch app/your_domain/__init__.py
touch app/your_domain/routes.py
```

2. **Define Domain Models**
```python
# app/your_domain/models/your_entity.py
from sqlalchemy import Column, Integer, String
from app.base.models.mysql_base import MySQLBaseModel

class YourEntity(MySQLBaseModel):
    __tablename__ = "your_entities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    # Add domain-specific fields
```

3. **Create Repository**
```python
# app/your_domain/repositories/your_entity_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.base.repositories.base_repository import BaseRepository
from app.your_domain.models.your_entity import YourEntity

class YourEntityRepository(BaseRepository[YourEntity]):
    def __init__(self, db: Session):
        super().__init__(model=YourEntity, db=db)
    
    def get_by_name(self, name: str) -> Optional[YourEntity]:
        return self.db.query(YourEntity).filter(YourEntity.name == name).first()
```

4. **Implement Service Layer**
```python
# app/your_domain/services/your_entity_service.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_primary_db
from app.your_domain.repositories.your_entity_repository import YourEntityRepository

class YourEntityService:
    def __init__(self, db: Annotated[Session, Depends(get_primary_db)]):
        self.repository = YourEntityRepository(db)
    
    def create_entity(self, entity_data: dict) -> YourEntity:
        return self.repository.create(entity_data)
```

5. **Create Controller**
```python
# app/your_domain/controllers/your_entity_controller.py
from typing import Annotated
from fastapi import Depends
from app.base.controllers.base_controller import BaseController
from app.your_domain.services.your_entity_service import YourEntityService

class YourEntityController(BaseController):
    def __init__(self, service: Annotated[YourEntityService, Depends()]):
        self.service = service
```

6. **Define Routes**
```python
# app/your_domain/routes.py
from typing import Annotated
from fastapi import APIRouter, Depends
from app.your_domain.controllers.your_entity_controller import YourEntityController

router = APIRouter(prefix="/your-entities", tags=["your-entities"])
YourEntityControllerDep = Annotated[YourEntityController, Depends()]

@router.get("/")
def get_entities(controller: YourEntityControllerDep):
    return controller.service.get_all()
```

7. **Register Routes in Main App**
```python
# main.py
from app.your_domain.routes import router as your_domain_router
app.include_router(your_domain_router)
```

### Configuration Management

1. **Environment-Based Configuration**
```python
# config/your_service.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class YourServiceConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    api_key: str = Field(validation_alias="YOUR_SERVICE_API_KEY")
    base_url: str = Field(default="https://api.yourservice.com", validation_alias="YOUR_SERVICE_BASE_URL")
```

2. **Database Configuration**
```python
# config/database.py
from pydantic import Field
from pydantic_settings import BaseSettings

class DatabaseConfig(BaseSettings):
    host: str = Field(default="localhost", validation_alias="DB_HOST")
    port: int = Field(default=5432, validation_alias="DB_PORT")
    user: str = Field(validation_alias="DB_USER")
    password: str = Field(validation_alias="DB_PASSWORD")
    database: str = Field(validation_alias="DB_NAME")
    
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
```

### Exception Handling

1. **Custom Domain Exceptions**
```python
# app/exceptions/your_domain_exception.py
from app.exceptions.base_exception import BaseException

class YourDomainException(BaseException):
    def __init__(self, message: str = "Domain-specific error occurred"):
        super().__init__(message, status_code=400)
```

2. **Global Exception Handler**
```python
# app/core/exception_handlers.py
from fastapi import FastAPI
from app.exceptions.your_domain_exception import YourDomainException

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(YourDomainException)
    async def your_domain_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message}
        )
```

### Testing Structure

1. **Unit Tests**
```python
# tests/unit/your_domain/test_your_entity_service.py
import pytest
from app.your_domain.services.your_entity_service import YourEntityService

class TestYourEntityService:
    def test_create_entity(self, db_session):
        service = YourEntityService(db_session)
        entity = service.create_entity({"name": "test"})
        assert entity.name == "test"
```

2. **Integration Tests**
```python
# tests/e2e/test_your_entity_e2e.py
def test_create_entity_endpoint(client):
    response = client.post("/your-entities/", json={"name": "test"})
    assert response.status_code == 201
    assert response.json()["name"] == "test"
```

### Dependency Injection

1. **FastAPI Dependencies**
```python
# Use type annotations for dependency injection
from typing import Annotated
from fastapi import Depends

# Define dependencies at module level
ServiceDep = Annotated[YourService, Depends()]
DBSession = Annotated[Session, Depends(get_db)]
```

2. **Service Dependencies**
```python
class YourService:
    def __init__(self, db: DBSession, external_api: ExternalApiDep):
        self.db = db
        self.external_api = external_api
```

## 🔧 Key Files and Their Purpose

### Core Application Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry point, middleware setup, route registration |
| `config/settings.py` | Centralized configuration management |
| `app/core/database.py` | Database connection and session management |
| `app/core/exception_handlers.py` | Global exception handling |

### Domain-Specific Files

| File | Purpose |
|------|---------|
| `models/` | Domain entities and data models |
| `repositories/` | Data access layer with repository pattern |
| `services/` | Business logic and use cases |
| `controllers/` | HTTP request handling |
| `actions/` | Specific business actions/use cases |
| `schemas/` | Data transfer objects (DTOs) |
| `enums/` | Domain-specific enumerations |

### Infrastructure Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Container image definition |
| `requirements.txt` | Python dependencies |
| `pyproject.toml` | Project configuration and tooling |
| `alembic.ini` | Database migration configuration |
| `pytest.ini` | Test configuration |

## 🚀 Quick Start Checklist

- [ ] Create project structure directories
- [ ] Set up virtual environment and dependencies
- [ ] Configure database connections
- [ ] Implement base classes (models, repositories, controllers)
- [ ] Set up exception handling
- [ ] Configure logging and monitoring
- [ ] Add your first domain module
- [ ] Set up testing framework
- [ ] Configure CI/CD pipeline
- [ ] Add documentation

## 📖 Best Practices

1. **Domain Isolation**: Keep domains separate with minimal cross-dependencies
2. **Dependency Injection**: Use FastAPI's built-in dependency injection
3. **Type Safety**: Use Python type hints throughout
4. **Error Handling**: Implement comprehensive exception handling
5. **Testing**: Write unit and integration tests for all components
6. **Documentation**: Document APIs using FastAPI's automatic documentation
7. **Configuration**: Use environment variables for configuration
8. **Logging**: Implement structured logging throughout the application

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Domain-Driven Design Reference](https://domainlanguage.com/ddd/)
- [Clean Architecture Principles](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)

---

This template provides a solid foundation for building scalable, maintainable applications following Domain-Driven Development principles. Adapt it to your specific needs and domain requirements.