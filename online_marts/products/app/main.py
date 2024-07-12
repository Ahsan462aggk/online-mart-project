# main.py
from aiokafka import AIOKafkaConsumer,AIOKafkaProducer
from contextlib import asynccontextmanager
from typing import Optional, Annotated,List
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends,HTTPException
from typing import AsyncGenerator
import asyncio
import json
from app.Cruds.product_cruds import new_product,check_product,Check_productid,delete_product_by_id,update_product_by_id
from app.models.product_models import ProductUpdate,Product
from app.database import engine
from app.deps import get_session ,get_kafka_producer




def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-product-group-consumer",
        auto_offset_reset='earliest'
    )

    # Start the consumer.
    await consumer.start()
    try:
        async for message in consumer:
            print("RAW")
            print(f"Received message on topic {message.topic}")
            product= json.loads(message.value.decode())
            print("TYPE", (type(product)))
            print(f"Product Data {product}")
            with next(get_session()) as session:
                print("SAVING DATA TO DATABSE")
                db_insert_product = new_product(
                    product=Product(**product), session=session)
                print("DB_INSERT_PRODUCT", db_insert_product)    

           ## new_todo = todo_pb2.Todo()
            ##new_todo.ParseFromString(message.value)
            ##print(f"\n\n Consumer Deserialized data: {new_todo}")
        # Here you can add code to process each message.
        # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
# loop = asyncio.get_event_loop()
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("creating tables.")
    # loop.run_until_complete(consume_messages('todos2', 'broker:19092'))
    asyncio.create_task(consume_messages('Products', 'broker:19092'))
    # create_db_and_tables()
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan,
              title="Hello Kafka With FastAPI",
              version="0.0.1",
              )




@app.get("/manage_products/all",response_model=list[Product])
def check_all_product(session:Annotated[Session,Depends(get_session)]):
    return check_product(session)




@app.post("/manage_products/", response_model=Product)
async def create_product(product: Product,session:Annotated[Session,Depends(get_session)],producer:Annotated[AIOKafkaProducer,Depends(get_kafka_producer)]):
    product_dict = {field: getattr(product, field) for field in product.dict()}
    product_json = json.dumps(product_dict).encode("utf-8")
    print("todoJSON:", product_json)
    await producer.send_and_wait("Products", product_json)
    return product
    
    

@app.get("/manage_product/{id}",response_model=Product)
def check_single_product(id: int,session:Annotated[Session,Depends(get_session)]):
    try:
        return Check_productid(product_id=id,session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    
@app.patch("/manage_products/{product_id}",response_model=List[ProductUpdate])
def update_product(product_id: int,product:ProductUpdate,session:Annotated[Session,Depends(get_session)]):
    try:
        return update_product_by_id(product_id=product_id,to_update_product_data=product,session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
     raise HTTPException(status_code=500, detail=str(e))
@app.delete("/manage_product/{id}",response_model=dict)
def delete_single_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Delete a single product by ID"""
    try:
        return delete_product_by_id(product_id=product_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))