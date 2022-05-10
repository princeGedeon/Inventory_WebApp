from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import supplier_pydantic,supplier_pydanticIn,product_pydantic,product_pydanticIn,Supplier,Product

#email
from fastapi import BackgroundTasks,UploadFile,File,Form
from starlette.responses import  JSONResponse
from starlette.requests import Request
from fastapi_mail import FastMail,MessageSchema,ConnectionConfig
from typing import List,ContextManager
from pydantic import BaseModel,EmailStr

#dotenv
from dotenv import dotenv_values
#credentials
credentials=dotenv_values('.env')
#adding CORS header
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()
#adding urls cors
origins=[
    "http://localhost:3000",
]
# add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=["*"]
)
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
    product_details=product_details.dict(exclude_unset=True)
    product_details['revenue'] += product_details['quantity_in_sold'] * product_details['price_unity']
    product_obj=await Product.create(**product_details,supplied_by=supplier)
    response= await product_pydantic.from_tortoise_orm(product_obj)
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

    product.quantity_in_stock=update_info['quantity_in_stock']
    product.revenue+=update_info['quantity_in_sold'] * update_info['price_unity']
    product.price_unity=update_info['price_unity']
    product.quantity_in_sold = update_info['quantity_in_sold']
    await  product.save()
    response=await product_pydantic.from_tortoise_orm(product)
    return {"status": "ok", "data": response}

@app.delete("/product/{id}")
async def delete_product(id:int):
    response=await Product.filter(id=id).delete()
    return {"status": "ok", "data": response}


class EmailSchema(BaseModel):
    email:List[EmailStr]

class EmailContent(BaseModel):
    message:str
    subject:str

conf=ConnectionConfig(
    MAIL_USERNAME=credentials['EMAIL'],
    MAIL_PASSWORD=credentials['PASS'],
    MAIL_FROM="guedjegedeon03@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    )
@app.post('/email/{product}')
async def send_mail(product_id:int,content: EmailContent):
    product=await Product.get(id=product_id)
    supplier=await product.supplied_by
    supplier_email=[supplier.email]

    html=f"""
    <h1>Prince Gedeon PRo</h1>
    <br>
    <p>{content.subject}</p>
     <br>
    <p>{content.message}</p>
     <br>
    <h6>Best </h6>
    <h6>Prince Business</h6>s
    """
    message = MessageSchema(
        subject=content.subject,
        recipients=supplier_email,  # Liste des receveur
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return {"status":"ok"}
