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

@app.get('/supplier/{supplied_id}')
async def get_specific_supplied(supplied_id:int):
    response=await supplier_pydantic.from_queryset_single(Supplier.get(id=supplied_id))
    return {"status": "ok", "data": response}

@app.put('/supplier/{supplied_id}')
async def update_supplier(supplier_id:int,update_info:supplier_pydanticIn):
    supplier=await Supplier.get(id=supplier_id)
    update_info=update_info.dict(exclude_unset=True)
    supplier.name=update_info['name']
    supplier.company=update_info['company']
    supplier.phone=update_info['phone']
    supplier.email=update_info['email']
    await supplier.save()
    response=await supplier_pydantic.from_tortoise_orm(supplier)
    return {"status":"ok","data":response}

@app.delete("/supplier/{supplied_id}")
async def delete_supploer(supplied_id):
    await Supplier.get(id=supplied_id).delete()
    return {"status":"ok"}

@app.post('/product/{supplier_id}')
async def add_product(supplier_id:int,product_details:product_pydanticIn):
    supplier=await Supplier.get(id=supplier_id)
    product=await product_details.dict(exclude_unset=True)
    product_details['revenue']+=product_details['quantity_in_sold']*product_details['price_unity']
    product_obj=await Product.create(**product_details,supplied_by=supplier)
    response=product_pydantic.from_tortoise_orm(product_obj)
    return {'status':"ok","data":response}


@app.get('/product')
async def get_all_prodicts():
    response=await product_pydantic.from_queryset(Product.all())
    return {'status':"ok","data":response}

@app.get("/product/{id}")
async def specific_product(id:int):
    response=await product_pydantic.from_queryset_single(Product.get(id=id))
    return {"status":"ok","data":response}

@app.put("/product/{id}")
async def update_product(id:int,update_info:product_pydanticIn):
    product=await Product.get(id=id)
    update_info=update_info.dict(exclude_unset=True)
    product.name=update_info['name']
    product.quantity_in_sold=update_info['quantity_in_sold']
    product.quantity_in_stock=update_info['quantity_in_stock']
    product.revenue+=update_info['quantity_in_sold']*update_info['price_unity']
    product.price_unity=update_info['price_unity']
    await  product.save()
    response=await product_pydantic.from_tortoise_orm(product)
    return {"status": "ok", "data": response}

@app.delete("/product/{id}")
async def delete_product(id:int):
    await Product.filter(id=id).delete()
    return {"status": "ok", "data": response}