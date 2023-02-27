import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.main import Base
from app.models.enable_uuid import BinaryUUID


class Module(Base):
    """Declaracion de la tabla Module.

    Args:
        Base (_DeclarativeBase): Objeto de SQLalchemy

    Returns:
        str: Nos regresa string con la data
    """

    __tablename__ = "modules"
    # Fields for category and modules (obligatory)
    id = Column(BinaryUUID, primary_key=True, default=uuid4)
    # IDK
    # dependency_k = Column(BinaryUUID, default=uuid4)
    # For category and modules (obligatory)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(250), nullable=True)
    # For category and modules (obligatory)
    # iconCls = Column(String(100), nullable=False)
    # icon_shortcut = Column(String(100), nullable=True)
    # For modules (obligatory)
    # classname = Column(String(250), nullable=True)
    # width = Column(Integer, nullable=True)
    # height = Column(Integer, nullable=True)
    # position = Column(Boolean, nullable=False)
    # hidden = Column(Boolean, nullable=True, default=False)
    # minimizable = Column(Boolean, nullable=True, default=True)
    # closable = Column(Boolean, nullable=True, default=True)
    # leaf = Column(Boolean, nullable=True, default=False)
    actions = relationship("Actions", back_populates="actions_module")
    is_active = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=True, default=False)
    created_on = Column(DateTime, default=datetime.datetime.now, nullable=False)
    created_by = Column(BinaryUUID, nullable=True)
    updated_on = Column(DateTime, onupdate=datetime.datetime.now, nullable=True)
    updated_by = Column(BinaryUUID, nullable=True)

    def __repr__(self) -> str:
        """Metodo representativo.

        Returns:
            str: String de la data que hemos filtrado
        """
        return f"<Modules Info> | {self.id} | {self.name} | \
            {self.is_deleted} | {self.created_on} | \
            {self.updated_on} | {self.created_by}"
