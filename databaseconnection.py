from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy import update, delete, or_, not_
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Connection

from models import *


class CConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f'__asyncpg_{prefix}_{uuid4()}__'


class DBConnection:
    def __init__(self):
        self.items_per_page = 5
        self.default_icon = 'https://yetty.ru/upload/cube.png'
        try:
            print('trying to init')
            host = 'databases'
            port = '5432'
            user = 'postgres'
            password = '1777'
            database = 'customname'

            self.engine = create_async_engine(f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}",
                                              connect_args={
                                                  "statement_cache_size": 0,
                                                  "prepared_statement_cache_size": 0,
                                                  "connection_class": CConnection,
                                              })
            self.metadata = Base.metadata
            self.connection = self.engine.connect()
            self.session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
            print('connected')
        except Exception as e:
            print("Ошибка при работе с PostgreSQL", e)

        self.session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)


    async def initialize_connection(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print('connection initializated')

    @asynccontextmanager
    async def create_session(self):
        async with self.session() as db:
            try:
                yield db
            except:
                await db.rollback()
                raise
            finally:
                await db.close()

    async def new_catalog(self, name):
        async with self.create_session() as session:
            new_catalog = Catalog(name=name)
            session.add(new_catalog)
            await session.commit()

    async def get_catalogs(self, limit: int, offset: int):
        async with self.create_session() as session:
            stmt = select(Catalog.catalog_id, Catalog.name)
            if limit != 0:
                stmt = stmt.limit(limit).offset(offset)
            result = (await session.execute(stmt)).all()

        return result

    async def get_items(self, limit: int = 0, offset: int = 0):
        async with self.create_session() as session:
            stmt = select(Item.item_id, Item.name, Item.description, Item.price, Item.picture_url)
            if limit != 0:
                stmt = stmt.limit(limit).offset(offset)

            result = (await session.execute(stmt)).all()
            return result

    async def get_items_in_other_catalogs(self, catalog_id: int):
        async with self.create_session() as session:
            stmt = select(Item.item_id, Item.name, Item.description, Item.price, Item.picture_url)
            stmt = stmt.order_by(Item.item_id)
            result = (await session.execute(stmt)).all()
            stmt = select(AssociationTable.item_id, AssociationTable.catalog_id)
            associations = (await session.execute(stmt)).all()
            for i in associations:
                if i[0] == catalog_id:
                    for j in range(len(result)):
                        if result[j][0] == i[1]:
                            result.pop(j)
                            break

            return result

    async def get_items_in_catalog(self, catalog_id: int, limit: int, offset: int):
        async with self.create_session() as session:
            stmt = select(AssociationTable.item_id, Item.name, Item.description, Item.price, Item.picture_url).\
                where(AssociationTable.catalog_id == catalog_id).\
                join_from(Item, AssociationTable, Item.item_id == AssociationTable.item_id)

            if limit != 0:
                stmt = stmt.limit(limit).offset(offset)

            stmt = stmt.order_by(AssociationTable.item_id)

            result = (await session.execute(stmt)).all()
            return result

    async def new_item(self, name: str, description: str, price: int, picture_url: str):
        async with self.create_session() as session:
            new_item = Item(name=name, description=description, price=price, picture_url=picture_url)
            session.add(new_item)
            await session.commit()
            stmt = select(Item.item_id).where((Item.name == name), (Item.description == description), (Item.price == price))
            result = int((await session.execute(stmt)).first()[0])
            return result

    async def delete_item(self, item_id: int):
        async with self.create_session() as session:
            stmt = delete(Item).where(Item.item_id == item_id)
            await session.execute(stmt)
            stmt = delete(AssociationTable).where(AssociationTable.item_id == item_id)
            await session.execute(stmt)
            await session.commit()

    async def new_association(self, catalog_id: int, item_id: int):
        async with self.create_session() as session:
            new_association = AssociationTable(catalog_id=catalog_id, item_id=item_id)
            session.add(new_association)
            await session.commit()

    async def delete_association(self, catalog_id: int, item_id: int):
        async with self.create_session() as session:
            stmt = delete(AssociationTable).where((AssociationTable.catalog_id == catalog_id),
                                                   (AssociationTable.item_id == item_id))
            await session.execute(stmt)
            await session.commit()


