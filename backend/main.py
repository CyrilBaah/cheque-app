from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import databases
import sqlalchemy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration from environment variables
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "cheque_db")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Define cheque table
cheques = sqlalchemy.Table(
    "cheques",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("cheque_number", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("manager_approved", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=datetime.utcnow),
)

# Create FastAPI app with enhanced documentation
app = FastAPI(
    title="Cheque Management API",
    description="""
    A REST API for managing cheques with manager approval tracking.
    
    ## Features
    
    * **Create cheques** with cheque number and approval status
    * **View all cheques** sorted by creation date
    * **Get individual cheque** details by ID
    * **Delete cheques** individually or clear all
    * **PostgreSQL database** backend for data persistence
    """,
    version="1.0.0",
    contact={
        "name": "Cheque App Support",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChequeCreate(BaseModel):
    """Model for creating a new cheque"""
    cheque_number: str = Field(
        ..., 
        description="Unique cheque number",
        example="CHQ-2026-001"
    )
    manager_approved: bool = Field(
        ..., 
        description="Whether the cheque has been approved by a manager",
        example=True
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "cheque_number": "CHQ-2026-001",
                "manager_approved": True
            }
        }

class ChequeResponse(BaseModel):
    """Model for cheque response data"""
    id: int = Field(..., description="Unique cheque ID", example=1)
    cheque_number: str = Field(..., description="Unique cheque number", example="CHQ-2026-001")
    manager_approved: bool = Field(..., description="Manager approval status", example=True)
    created_at: datetime = Field(..., description="Timestamp when the cheque was created")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "cheque_number": "CHQ-2026-001",
                "manager_approved": True,
                "created_at": "2026-01-15T12:00:00"
            }
        }

# Database connection events
@app.on_event("startup")
async def startup():
    await database.connect()
    # Create tables if they don't exist
    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# API endpoints
@app.get(
    "/",
    tags=["Health"],
    summary="API Health Check",
    description="Returns a simple message confirming the API is running"
)
async def root():
    """Check if the API is running and responsive"""
    return {"message": "Cheque App API", "status": "running", "version": "1.0.0"}

@app.post(
    "/api/cheques",
    response_model=ChequeResponse,
    tags=["Cheques"],
    summary="Create a new cheque",
    description="Create a new cheque with cheque number and manager approval status",
    status_code=201
)
async def create_cheque(cheque: ChequeCreate):
    """Create a new cheque in the database"""
    query = cheques.insert().values(
        cheque_number=cheque.cheque_number,
        manager_approved=cheque.manager_approved,
        created_at=datetime.utcnow()
    )
    last_record_id = await database.execute(query)
    
    # Fetch the created record
    select_query = cheques.select().where(cheques.c.id == last_record_id)
    created_cheque = await database.fetch_one(select_query)
    
    return created_cheque

@app.get(
    "/api/cheques",
    response_model=List[ChequeResponse],
    tags=["Cheques"],
    summary="Get all cheques",
    description="Retrieve a list of all cheques sorted by creation date (newest first)"
)
async def get_cheques():
    """Retrieve all cheques from the database, sorted by creation date in descending order"""
    query = cheques.select().order_by(cheques.c.created_at.desc())
    return await database.fetch_all(query)

@app.delete(
    "/api/cheques",
    tags=["Cheques"],
    summary="Delete all cheques",
    description="Remove all cheques from the database"
)
async def clear_cheques():
    """Delete all cheques from the database"""
    query = cheques.delete()
    await database.execute(query)
    return {"message": "All cheques cleared successfully"}

@app.get(
    "/api/cheques/{cheque_id}",
    response_model=ChequeResponse,
    tags=["Cheques"],
    summary="Get a specific cheque",
    description="Retrieve a single cheque by its ID",
    responses={
        404: {"description": "Cheque not found"}
    }
)
async def get_cheque(cheque_id: int = Path(..., description="The ID of the cheque to retrieve", example=1)):
    """Retrieve a specific cheque by its ID"""
    query = cheques.select().where(cheques.c.id == cheque_id)
    cheque = await database.fetch_one(query)
    if not cheque:
        raise HTTPException(status_code=404, detail="Cheque not found")
    return cheque

@app.delete(
    "/api/cheques/{cheque_id}",
    tags=["Cheques"],
    summary="Delete a specific cheque",
    description="Remove a single cheque from the database by its ID",
    responses={
        404: {"description": "Cheque not found"}
    }
)
async def delete_cheque(cheque_id: int = Path(..., description="The ID of the cheque to delete", example=1)):
    """Delete a specific cheque by its ID"""
    # Check if cheque exists
    select_query = cheques.select().where(cheques.c.id == cheque_id)
    cheque = await database.fetch_one(select_query)
    if not cheque:
        raise HTTPException(status_code=404, detail="Cheque not found")
    
    # Delete the cheque
    query = cheques.delete().where(cheques.c.id == cheque_id)
    await database.execute(query)
    return {"message": "Cheque deleted successfully"}
