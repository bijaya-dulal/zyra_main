"""
Defines the SQLAlchemy Declarative Base class for all models to inherit from.
This file is imported by all models and must NOT import the main DB engine/session setup.
"""
from sqlalchemy.orm import declarative_base

# The Base class that all your ORM models will inherit.
Base = declarative_base()