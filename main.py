from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import nest_asyncio
import databaseconnection
from schemas import *
import math

nest_asyncio.apply()

db = databaseconnection.DBConnection()
async def inition():
    await db.initialize_connection()
asyncio.run(inition())


app = FastAPI()
app.mount('/templates', StaticFiles(directory='templates'), name='templates')
templates = Jinja2Templates(directory="templates")



@app.post('/api/NewCatalog', response_model=BaseResponse)
async def new_catalog(name: str):
    try:
        await db.new_catalog(name)
        response = BaseResponse(error=False, message='OK', payload=None)
    except Exception as e:
        response = BaseResponse(error=True, message=str(e), payload=None)
    return response


@app.get('/api/CatalogList', response_model=CatalogListResponse)
async def catalog_list(limit: int = 10, offset: int = 0):
    try:
        cataloglst = await db.get_catalogs(limit, offset)
        catalogs = []
        for id, name in cataloglst:
            catalogs.append(Catalog(id=id, name=name))

        response = CatalogListResponse(error=False, message='OK', payload=CatalogList(totalcount=len(catalogs), catalogs=catalogs))
    except Exception as e:
        response = BaseResponse(error=True, message=str(e), payload=None)
    return response


@app.get('/api/ItemsList', response_model=ItemListResponse)
async def items_list(limit: int = 10, offset: int = 0):
    try:
        itemlst = await db.get_items(limit, offset)
        items = []
        for id, name, description, price, picture_url in itemlst:
            items.append(Item(id=id, name=name, description=description, price=price, picture_url=picture_url))

        response = ItemListResponse(error=False, message='OK', payload=ItemList(totalcount=len(items), items=items))
    except Exception as e:
        response = BaseResponse(error=True, message=str(e), payload=None)
    return response


@app.get('/api/ItemsInCatalogList', response_model=ItemListResponse)
async def items_in_catalog_list(catalog_id: int, limit: int = 10, offset: int = 0):
    try:
        itemlst = await db.get_items_in_catalog(catalog_id, limit, offset)
        items = []
        for id, name, description, price, picture_url in itemlst:
            items.append(Item(id=id, name=name, description=description, price=price, picture_url=picture_url))

        response = ItemListResponse(error=False, message='OK', payload=ItemList(totalcount=len(items), items=items))
    except Exception as e:
        response = BaseResponse(error=True, message=str(e), payload=None)
    return response


@app.post('/api/NewItem', response_model=BaseResponse)
async def new_item(name: str, description: str, price: int, picture_url: str = db.default_icon, catalog_id: int = None):
    try:
        item_id = await db.new_item(name, description, price, picture_url)
        if catalog_id != None:
            await db.new_association(catalog_id, item_id)

        response = BaseResponse(error=False, message='OK', payload=None)
    except Exception as e:
        response = BaseResponse(error=True, message=str(e), payload=None)
    return response


@app.post('/api/DeleteItem', response_model=BaseResponse)
async def delete_item(item_id: int):
    try:
        await db.delete_item(item_id)
        response = BaseResponse(error=False, message='OK', payload=None)
    except Exception as e:
        response = BaseResponse(error=True, message=str(e), payload=None)
    return response


@app.post('/api/NewAssociation', response_model=BaseResponse)
async def new_association(catalog_id: int, item_id: int):
    try:
        await db.new_association(catalog_id, item_id)
        response = BaseResponse(error=False, message='OK', payload=None)
    except Exception as e:
        response = BaseResponse(error=True, message=str(e), payload=None)
    return response


@app.post('/api/DeleteAssociation', response_model=BaseResponse)
async def delete_association(catalog_id: int, item_id: int):
    try:
        await db.delete_association(catalog_id, item_id)
        response = BaseResponse(error=False, message='OK', payload=None)
    except Exception as e:
        response = BaseResponse(error=True, message=str(e), payload=None)
    return response


@app.get('/CatalogEditor', response_class=HTMLResponse)
async def main_page(request: Request):
    catalogs = await db.get_catalogs(15, 0)
    itemlst = await db.get_items()
    items, page_num = await return_items(itemlst)
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "catalogs": catalogs,
                                                     "items": items,
                                                     "selected_catalog_id": 0,
                                                     "page_num": page_num})


@app.get('/CatalogEditor/ItemList', response_class=HTMLResponse)
async def item_list_page(request: Request, catalog_id: int):
    catalogs = await db.get_catalogs(15, 0)
    if catalog_id == 0:
        itemlst = await db.get_items()
    else:
        itemlst = await db.get_items_in_catalog(catalog_id, 0, 0)

    items, page_num = await return_items(itemlst)
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "catalogs": catalogs,
                                                     "items": items,
                                                     "selected_catalog_id": catalog_id,
                                                     "page_num": page_num})


@app.get('/CatalogEditor/NewCatalog', response_class=HTMLResponse)
async def new_catalog_page(request: Request, catalog_name: str):
    try:
        await db.new_catalog(catalog_name)
    except Exception as e:
        print(str(e))


@app.get('/CatalogEditor/NewItem', response_class=HTMLResponse)
async def new_item_page(request: Request, name: str, price: int, description: str, picture_url: str = db.default_icon, catalog_id: int = 0):
    try:
        if picture_url == '':
            picture_url = db.default_icon
        item_id = await db.new_item(name, description, price, picture_url)
        if catalog_id != 0:
            await db.new_association(catalog_id, item_id)

    except Exception as e:
        print(str(e))


@app.get('/CatalogEditor/DeleteItem', response_class=HTMLResponse)
async def delete_item(request: Request, item_id: int):
    await db.delete_item(item_id)


@app.get('/CatalogEditor/AItemsInCatalog', response_class=HTMLResponse)
async def a_items_in_catalog(request: Request, catalog_id: int):
    catalogs = await db.get_catalogs(15, 0)
    items = await db.get_items_in_catalog(catalog_id, 0, 0)
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "catalogs": catalogs,
                                                     "Aitems": items,
                                                     "selected_Acatalog_id": catalog_id,
                                                     "page_num": 0,
                                                     "items": [[]]})


@app.get('/CatalogEditor/ItemsInOtherCatalogs', response_class=HTMLResponse)
async def items_in_other_catalogs(request: Request, catalog_id: int):
    catalogs = await db.get_catalogs(15, 0)
    items = await db.get_items_in_other_catalogs(catalog_id)
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "catalogs": catalogs,
                                                     "Aitems": items,
                                                     "selected_Acatalog_id": catalog_id,
                                                     "page_num": 0,
                                                     "items": [[]]})


@app.get('/CatalogEditor/NewAssosiation', response_class=HTMLResponse)
async def new_assosiation(request: Request, catalog_id: int, item_id: int):
    await db.new_association(catalog_id, item_id)


@app.get('/CatalogEditor/DeleteAssosiation', response_class=HTMLResponse)
async def delete_assosiation(request: Request, catalog_id: int, item_id: int):
    await db.delete_association(catalog_id, item_id)


async def return_items(itemlst: list):
    items = []
    items_per_page = db.items_per_page
    page_num = math.ceil(len(itemlst)/items_per_page)
    j = -1
    for i in range(len(itemlst)):
        if i % items_per_page == 0:
            items.append([])
            j += 1
        items[j].append(itemlst[i])

    return items, page_num

