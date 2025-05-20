from fastapi import FastAPI
from backend.app.Controllers.auth import auth_router
from backend.app.Controllers.category import category_router
from backend.app.Controllers.products import products_router
from backend.app.Controllers.Order import order_router
from backend.app.Controllers.cart import cart_router


app = FastAPI()

app.include_router(auth_router.router)
app.include_router(category_router.router)
app.include_router(products_router.router)
app.include_router(order_router.router)
app.include_router(cart_router.router)
