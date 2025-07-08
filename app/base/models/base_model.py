import sqlalchemy.orm

Base = sqlalchemy.orm.declarative_base()


class MySQLBaseModel(Base):
    """
    Base model for all MySQL entities
    """

    __abstract__ = True

    def to_dict(self):
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def from_dict(cls, data: dict):
        """Create model from dictionary"""
        return cls(**data)