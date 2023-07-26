from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Sequence


class Base(DeclarativeBase):
    pass


class AssociationTable(Base):
    __tablename__ = 'Associations'

    catalog_id = Column(Integer, primary_key=True)
    item_id = Column(Integer, primary_key=True)


class Catalog(Base):
    __tablename__ = 'Catalogs'

    catalog_id = Column(Integer, Sequence('catalog_id', metadata=Base.metadata), primary_key=True)
    name = Column(String)


class Item(Base):
    __tablename__ = 'Items'

    item_id = Column(Integer, Sequence('item_id', metadata=Base.metadata), primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Integer)
    picture_url = Column(String)








