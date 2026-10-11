"""Repository base class for common CRUD operations."""

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository class with common CRUD operations."""

    def __init__(self, model: Type[T], db: Session):
        """Initialize repository."""
        self.model = model
        self.db = db

    def create(self, **kwargs) -> T:
        """Create a new record."""
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: int) -> Optional[T]:
        """Get record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update a record."""
        db_obj = self.get_by_id(id)
        if db_obj:
            for key, value in kwargs.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        """Hard delete a record."""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False

    def soft_delete(self, id: int) -> Optional[T]:
        """Soft delete a record (set deleted_at)."""
        from datetime import datetime

        db_obj = self.get_by_id(id)
        if db_obj and hasattr(db_obj, "deleted_at"):
            db_obj.deleted_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def get_active(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all active (non-deleted) records."""
        if hasattr(self.model, "deleted_at"):
            return (
                self.db.query(self.model)
                .filter(self.model.deleted_at.is_(None))
                .offset(skip)
                .limit(limit)
                .all()
            )
        return self.get_all(skip, limit)

    def count(self) -> int:
        """Count all records."""
        return self.db.query(self.model).count()

    def count_active(self) -> int:
        """Count all active records."""
        if hasattr(self.model, "deleted_at"):
            return self.db.query(self.model).filter(self.model.deleted_at.is_(None)).count()
        return self.count()
