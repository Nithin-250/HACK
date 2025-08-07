from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import List, Optional
import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import bcrypt
import jwt
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import numpy as np
from scipy import stats
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "fraud_detection")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")

# MongoDB client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
transactions_collection = db.transactions
blacklist_collection = db.blacklist
users_collection = db.users

# Security
security = HTTPBearer()
geolocator = Nominatim(user_agent="fraud_detection_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize predefined blacklisted data
    await initialize_blacklist()
    yield
    # Shutdown: Close MongoDB connection
    client.close()

app = FastAPI(
    title="Financial Fraud Detection System",
    description="A comprehensive fraud detection system for financial transactions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class Transaction(BaseModel):
    transaction_id: str
    timestamp: str = Field(..., description="Format: 'YYYY-MM-DD HH:MM:SS'")
    amount: float = Field(..., gt=0)
    location: str = Field(..., description="City name like 'Chennai'")
    card_type: str
    currency: str = Field(default="USD")
    recipient_account_number: str

class TransactionResponse(BaseModel):
    transaction_id: str
    timestamp: str
    amount: float
    location: str
    card_type: str
    currency: str
    recipient_account_number: str
    is_fraud: bool
    fraud_reasons: List[str]
    risk_score: float

# Predefined blacklisted data
BLACKLISTED_IPS = [
    "192.168.1.100",
    "10.0.0.50",
    "172.16.0.25",
    "203.0.113.45",
    "198.51.100.78"
]

BLACKLISTED_ACCOUNTS = [
    "ACC123456789",
    "ACC987654321",
    "ACC555666777",
    "ACC111222333"
]

async def initialize_blacklist():
    """Initialize predefined blacklisted IPs and accounts"""
    try:
        # Add blacklisted IPs
        for ip in BLACKLISTED_IPS:
            blacklist_collection.update_one(
                {"type": "ip", "value": ip},
                {"$set": {"type": "ip", "value": ip, "added_at": datetime.now()}},
                upsert=True
            )
        
        # Add blacklisted accounts
        for account in BLACKLISTED_ACCOUNTS:
            blacklist_collection.update_one(
                {"type": "account", "value": account},
                {"$set": {"type": "account", "value": account, "added_at": datetime.now()}},
                upsert=True
            )
        
        logger.info("Blacklist initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing blacklist: {e}")

def get_coordinates(location: str) -> tuple:
    """Get latitude and longitude for a location"""
    try:
        location_data = geolocator.geocode(location)
        if location_data:
            return (location_data.latitude, location_data.longitude)
        return None
    except Exception as e:
        logger.error(f"Error geocoding location {location}: {e}")
        return None

def calculate_distance(loc1: str, loc2: str) -> float:
    """Calculate distance between two locations in kilometers"""
    try:
        coords1 = get_coordinates(loc1)
        coords2 = get_coordinates(loc2)
        
        if coords1 and coords2:
            return geodesic(coords1, coords2).kilometers
        return 0
    except Exception as e:
        logger.error(f"Error calculating distance: {e}")
        return 0

def is_odd_hour(timestamp_str: str) -> bool:
    """Check if transaction is at odd hours (12 AM to 4 AM)"""
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        return 0 <= hour <= 4
    except Exception as e:
        logger.error(f"Error parsing timestamp: {e}")
        return False

def calculate_z_score(current_amount: float, card_type: str) -> float:
    """Calculate z-score for amount anomaly detection"""
    try:
        # Get last 5 transactions for this card type
        recent_transactions = list(
            transactions_collection.find(
                {"card_type": card_type}
            ).sort("timestamp", -1).limit(5)
        )
        
        if len(recent_transactions) < 2:
            return 0  # Not enough data
        
        amounts = [t["amount"] for t in recent_transactions]
        mean_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        
        if std_amount == 0:
            return 0
        
        z_score = abs((current_amount - mean_amount) / std_amount)
        return z_score
    except Exception as e:
        logger.error(f"Error calculating z-score: {e}")
        return 0

def check_geographic_drift(location: str, card_type: str) -> bool:
    """Check if current location is >500km from last known location"""
    try:
        # Get last transaction for this card type
        last_transaction = transactions_collection.find_one(
            {"card_type": card_type},
            sort=[("timestamp", -1)]
        )
        
        if not last_transaction:
            return False  # No previous transaction
        
        last_location = last_transaction["location"]
        distance = calculate_distance(location, last_location)
        
        return distance > 500
    except Exception as e:
        logger.error(f"Error checking geographic drift: {e}")
        return False

def detect_fraud(transaction: Transaction, client_ip: str = None) -> tuple:
    """Main fraud detection logic"""
    fraud_reasons = []
    risk_score = 0
    
    # Check blacklisted IP
    if client_ip:
        blacklisted_ip = blacklist_collection.find_one({"type": "ip", "value": client_ip})
        if blacklisted_ip:
            fraud_reasons.append("Blacklisted IP address")
            risk_score += 30
    
    # Check blacklisted recipient account
    blacklisted_account = blacklist_collection.find_one({
        "type": "account", 
        "value": transaction.recipient_account_number
    })
    if blacklisted_account:
        fraud_reasons.append("Blacklisted recipient account")
        risk_score += 40
    
    # Check odd hours
    if is_odd_hour(transaction.timestamp):
        fraud_reasons.append("Transaction at odd hours (12 AM - 4 AM)")
        risk_score += 15
    
    # Check amount anomaly
    z_score = calculate_z_score(transaction.amount, transaction.card_type)
    if z_score > 2:  # More than 2 standard deviations
        fraud_reasons.append(f"Abnormal transaction amount (z-score: {z_score:.2f})")
        risk_score += 20
    
    # Check geographic drift
    if check_geographic_drift(transaction.location, transaction.card_type):
        fraud_reasons.append("Geographic drift detected (>500km from last location)")
        risk_score += 25
    
    is_fraud = len(fraud_reasons) > 0 or risk_score >= 30
    
    return is_fraud, fraud_reasons, risk_score

def create_access_token(data: dict):
    """Create JWT access token"""
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Authentication endpoints
@app.post("/signup")
async def signup(user: UserCreate):
    """User registration"""
    try:
        # Check if user already exists
        existing_user = users_collection.find_one({"username": user.username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Hash password
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_doc = {
            "username": user.username,
            "email": user.email,
            "password": hashed_password,
            "created_at": datetime.now()
        }
        
        result = users_collection.insert_one(user_doc)
        
        return {"message": "User created successfully", "user_id": str(result.inserted_id)}
    
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@app.post("/login")
async def login(user: UserLogin):
    """User login"""
    try:
        # Find user
        user_doc = users_collection.find_one({"username": user.username})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not bcrypt.checkpw(user.password.encode('utf-8'), user_doc["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user.username})
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error logging in"
        )

# Main fraud detection endpoint
@app.post("/check_fraud", response_model=TransactionResponse)
async def check_fraud_endpoint(
    transaction: Transaction, 
    username: str = Depends(verify_token)
):
    """Check if a transaction is fraudulent"""
    try:
        # Detect fraud
        is_fraud, fraud_reasons, risk_score = detect_fraud(transaction)
        
        # Store transaction in database
        transaction_doc = {
            "transaction_id": transaction.transaction_id,
            "timestamp": transaction.timestamp,
            "amount": transaction.amount,
            "location": transaction.location,
            "card_type": transaction.card_type,
            "currency": transaction.currency,
            "recipient_account_number": transaction.recipient_account_number,
            "is_fraud": is_fraud,
            "fraud_reasons": fraud_reasons,
            "risk_score": risk_score,
            "checked_by": username,
            "checked_at": datetime.now()
        }
        
        transactions_collection.insert_one(transaction_doc)
        
        # If fraudulent, add recipient account to blacklist
        if is_fraud:
            blacklist_collection.update_one(
                {"type": "account", "value": transaction.recipient_account_number},
                {
                    "$set": {
                        "type": "account",
                        "value": transaction.recipient_account_number,
                        "added_at": datetime.now(),
                        "reason": "Fraudulent transaction detected"
                    }
                },
                upsert=True
            )
            
            logger.info(f"Fraudulent transaction detected: {transaction.transaction_id}")
        
        return TransactionResponse(
            transaction_id=transaction.transaction_id,
            timestamp=transaction.timestamp,
            amount=transaction.amount,
            location=transaction.location,
            card_type=transaction.card_type,
            currency=transaction.currency,
            recipient_account_number=transaction.recipient_account_number,
            is_fraud=is_fraud,
            fraud_reasons=fraud_reasons,
            risk_score=risk_score
        )
    
    except Exception as e:
        logger.error(f"Error checking fraud: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing transaction"
        )

# Get all transactions
@app.get("/transactions")
async def get_transactions(username: str = Depends(verify_token)):
    """Get all transactions"""
    try:
        transactions = list(transactions_collection.find({}, {"_id": 0}).sort("checked_at", -1))
        return {"transactions": transactions}
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching transactions"
        )

# Get flagged transactions
@app.get("/flagged_transactions")
async def get_flagged_transactions(username: str = Depends(verify_token)):
    """Get all flagged (fraudulent) transactions"""
    try:
        flagged_transactions = list(
            transactions_collection.find(
                {"is_fraud": True}, 
                {"_id": 0}
            ).sort("checked_at", -1)
        )
        return {"flagged_transactions": flagged_transactions}
    except Exception as e:
        logger.error(f"Error getting flagged transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching flagged transactions"
        )

# Get blacklist
@app.get("/blacklist")
async def get_blacklist(username: str = Depends(verify_token)):
    """Get all blacklisted items"""
    try:
        blacklist_items = list(blacklist_collection.find({}, {"_id": 0}).sort("added_at", -1))
        return {"blacklist": blacklist_items}
    except Exception as e:
        logger.error(f"Error getting blacklist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching blacklist"
        )

# Health check
@app.get("/")
async def root():
    return {"message": "Financial Fraud Detection System API", "status": "active"}

# Serve the main HTML file
from fastapi.responses import FileResponse

@app.get("/app")
async def serve_app():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)