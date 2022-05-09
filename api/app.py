from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import supplier_pydantic,supplier_pydanticIn,product_pydantic,product_pydanticIn,Supplier,Product

app=FastAPI()

#Intégration Model et API
register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={'models':['models']},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get('/')
async def index():
    return {"msg":"Hello world"}

@app.post('/supplier',name='Supplier')
async def add_supplier(supllier_info:supplier_pydanticIn):
    supllier_obj=await Supplier.create(**supllier_info.dict(exclude_unset=True))
    response=await supplier_pydantic.from_tortoise_orm(supllier_obj)
    return {"status":"ok","data":response}

@app.get('/supplier',name="Supplier")
async def get_all_supllier():
    response=await supplier_pydantic.from_queryset(Supplier.all())
    return {"status":"ok","data":response}