from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class Practice(Base):
    __tablename__ = "practices"

    id = Column(Integer, primary_key=True, index=True)
    internal_id = Column(String, unique=True, nullable=False)
    name = Column(String, index=True)
    address = Column(String)
    phone = Column(String)
    email = Column(String)

    tickets = relationship("Ticket", back_populates="practice")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    practice_id = Column(String, ForeignKey("practices.internal_id"), nullable=False)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON, nullable=False)

    # Neue Felder
    insurance_status = Column(Enum('privat', 'gesetzlich', name='insurance_status_enum'), nullable=False, default='gesetzlich')  # Krankenversicherungsstatus
    prescription_required = Column(Enum('yes', 'no', name='prescription_required_enum'), nullable=False, default='no')  # Rezept erforderlich

    practice = relationship("Practice", back_populates="tickets")

    def set_data(self, ticket_data):
        """
        Speichert das komplette Pydantic-Ticket als JSON.
        date, datetime und Enums werden korrekt serialisiert.
        """
        self.data = ticket_data.model_dump(mode="json")
