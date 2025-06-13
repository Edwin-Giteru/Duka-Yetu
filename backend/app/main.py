import uvicorn
from fastapi import FastAPI
from backend.app import auth_router
from backend.app import category_router
from backend.app import products_router
from backend.app import order_router
from backend.app import cart_router
from backend.app import payment_router
from backend.app import feedback_router


app = FastAPI()

app.include_router(auth_router.router)
app.include_router(category_router.router)
app.include_router(products_router.router)
app.include_router(order_router.router)
app.include_router(cart_router.router)
app.include_router(payment_router.router)
app.include_router(feedback_router.router)

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)