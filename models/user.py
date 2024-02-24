#!/usr/bin/python3
""" holds class User"""
import hashlib
import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class User(BaseModel, Base):
    """Representation of a user """
    if models.storage_t == 'db':
        __tablename__ = 'users'
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        first_name = Column(String(128), nullable=True)
        last_name = Column(String(128), nullable=True)
        places = relationship("Place", backref="user")
        reviews = relationship("Review", backref="user")

    def __init__(self, *args, **kwargs):
        """initializes user"""
        if 'password' in kwargs:
            if kwargs.get('password'):
                kwargs['password'] = hashlib.md5(kwargs['password'].encode()).hexdigest()
        super().__init__(*args, **kwargs)

    def to_dict(self, include_password=False):
        """returns a dictionary representation of the User instance"""
        new_dict = super().to_dict()
        if not include_password and 'password' in new_dict:
            del new_dict['password']
        return new_dict
