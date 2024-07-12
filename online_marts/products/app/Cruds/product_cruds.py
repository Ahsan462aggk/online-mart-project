from sqlmodel import Session,select
from app.models.product_models import Product,ProductUpdate
from fastapi import HTTPException
def new_product(product:Product,session:Session):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

def check_product(session:Session):
    db=session.exec(select(Product)).all()
    if db is None:
        return "No products found"
    return db


def Check_productid(product_id:int,session:Session):
    db2 =session.exec(select(Product).where(Product.id==product_id)).one_or_none()
    if db2 is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db2

def update_product_by_id(product_id: int, to_update_product_data:ProductUpdate, session: Session):

    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    hero_data = to_update_product_data.model_dump(exclude_unset=True)
    product.sqlmodel_update(hero_data)
    session.add(product)
    session.commit()
    return product,{"message":"product update sucessfully"}
def delete_product_by_id(product_id: int, session: Session):
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return {"message": "Product Deleted Successfully"}