from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


# Модель для пользователей
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    settings = Column(JSON, default={})
    progress = Column(JSON, default={})
    words_added = Column(JSON, default={})


# Модель для слов
class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    text = Column(String)
    translation = Column(String)
    next_repeat = Column(DateTime, default=datetime.utcnow)
    repeat_count = Column(Integer, default=0)
    difficulty = Column(Float, default=0.0)


# Модель для статистики
class Stat(Base):
    __tablename__ = 'stats'

    user_id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer, default=0)
    activity_log = Column(JSON, default=[])
