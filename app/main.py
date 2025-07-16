from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth.auth import router as auth_router
from app.api.user.users import router as users_router
from app.api.product.products import router as product_router
from app.api.order.order import router as orders_router
from app.api.category.category import router as categories_router
from app.api.cart.cart import router as cart_router
from app.api.review.review import router as reviews_router
from app.api.admin.admin import router as admin_router
from pydantic_settings import BaseSettings
from app.api.upload.upload import router as upload_router
from app.core.config import Settings
import cloudinary
app = FastAPI(title="FastAPI E-commerce Auth")

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(product_router, prefix="/product", tags=["Product"])

app.include_router(orders_router, prefix="/orders", tags=["Orders"])

app.include_router(cart_router, prefix="/cart", tags=["Cart"])

app.include_router(reviews_router, tags=["Reviews"])

app.include_router(admin_router, tags=["Admin"])

app.include_router(categories_router, prefix="/categories", tags=["Categories"])

app.include_router(upload_router, prefix="/upload", tags=["Upload"])

settings = Settings()
cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET
)
