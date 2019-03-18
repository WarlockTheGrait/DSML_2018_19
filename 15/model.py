from sqlalchemy import Column, Integer, Text, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Index

Base = declarative_base()


class Book(Base):
    __tablename__ = 'book'

    book_id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    annotation = Column(Text, nullable=False)
    genre = Column(String(50), nullable=False)
    file = Column(String(50), nullable=False)


class Section(Base):
    __tablename__ = 'section'
    __table_args__ = (Index('book_id_idx', 'book_id'),)

    section_id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    book_id = Column(Integer, nullable=False)


class Paragraph(Base):
    __tablename__ = 'paragraph'
    __table_args__ = (Index('section_id_idx', 'section_id'),)

    paragraph_id = Column(Integer, primary_key=True)
    section_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)


class Chunk(Base):
    __tablename__ = 'chunk'
    __table_args__ = (Index('author_idx', 'author'),)

    chunk_id = Column(Integer, primary_key=True)
    author = Column(String(100), nullable=False)
    book_id = Column(String(100), nullable=False)
    text = Column(Text, nullable=False)