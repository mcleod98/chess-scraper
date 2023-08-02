from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GameRecord(Base):
    __tablename__ = "game"
    id = Column(Integer, primary_key=True)
    my_elo = Column(Integer)
    opp_elo = Column(Integer)
    result = Column(String)
    ending = Column(String)
    white = Column(Boolean)
    op_name = Column(String)
    date_played = Column(DateTime)
    moves = relationship('Move', back_populates='game')
    timecontrol = Column(String)

class Move(Base):
    __tablename__ = 'move'
    id = Column(Integer, primary_key=True)
    game = relationship('GameRecord', back_populates='moves')
    game_id = Column(Integer, ForeignKey("game.id"))
    movenumber = Column(Integer)
    move = Column(String)

class Download(Base):
    __tablename__ = 'download'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
