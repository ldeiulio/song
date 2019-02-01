from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship, backref, sessionmaker


Base = declarative_base()
engine = create_engine('postgresql+pg8000://test:pass@localhost:5432/song')
session = sessionmaker(bind=engine)()


def create_all():
    Base.metadata.create_all(engine)


class Song(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"), unique=True, nullable=False)

    def as_dictionary(self):
        return {
            "id": self.id,
            "file": self.file.as_dictionary()
        }


class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    path = Column(String)

    song = relationship("Song", backref=backref("file", uselist=False))

    def as_dictionary(self):
        return {
            "id": self.id,
            "name": self.file_name,
            "path": self.path
        }
