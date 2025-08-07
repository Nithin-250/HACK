# Quick Start Guide

Get the Financial Fraud Detection System up and running in 5 minutes!

## 🚀 Instant Setup

### 1. Run Setup (First Time Only)
```bash
python setup.py
```

This will:
- ✅ Check Python version (3.8+ required)
- ✅ Install all dependencies
- ✅ Create configuration files
- ✅ Verify installation

### 2. Start MongoDB
```bash
# Option A: Local MongoDB
mongod

# Option B: Use MongoDB Atlas (cloud)
# Update MONGO_URI in .env file with your Atlas connection string
```

### 3. Start the Application
```bash
python run.py
```

### 4. Open Your Browser
Go to: **http://localhost:8000/app**

## 🎯 Test the System

### Create Account
1. Click "Sign In" → "Sign up"
2. Enter username, email, password
3. Click "Sign Up" then sign in

### Test Fraud Detection
Try these test cases:

**Safe Transaction:**
- Transaction ID: `TXN001`
- Amount: `100.00`
- Location: `New York`
- Card Type: `Visa`
- Recipient Account: `ACC999888777`

**Fraudulent Transaction (Blacklisted Account):**
- Transaction ID: `TXN002`
- Amount: `5000.00`
- Location: `Chennai`
- Card Type: `MasterCard`
- Recipient Account: `ACC123456789` ← This is blacklisted!

**Fraudulent Transaction (Odd Hours):**
- Transaction ID: `TXN003`
- Timestamp: Set to 2:00 AM
- Amount: `1000.00`
- Location: `London`
- Card Type: `Visa`
- Recipient Account: `ACC111222333` ← This is also blacklisted!

## 📱 Web Interface Features

### Navigation Tabs
- **New Transaction**: Submit transactions for fraud analysis
- **Transaction History**: View all processed transactions
- **Flagged Transactions**: See only fraudulent transactions
- **Blacklist**: View blacklisted IPs and accounts

### What to Look For
- ✅ **Green results**: Safe transactions
- ❌ **Red results**: Fraudulent transactions
- 📊 **Risk scores**: 0-100% fraud probability
- 🔍 **Fraud reasons**: Detailed explanation of why a transaction was flagged

## 🛠️ Troubleshooting

### Common Issues

**"MongoDB connection error"**
```bash
# Make sure MongoDB is running
mongod
# Or check your .env file for correct MONGO_URI
```

**"Module not found"**
```bash
# Run setup again
python setup.py
```

**"Port 8000 already in use"**
```bash
# Kill existing process or change port in main.py
lsof -ti:8000 | xargs kill -9
```

## 🔧 Configuration

Edit `.env` file to customize:
```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=fraud_detection
SECRET_KEY=your-secret-key-here
```

## 📊 API Documentation

Once running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## 🎉 You're Ready!

The system is now detecting fraud in real-time. Each transaction you submit will be:
1. Analyzed against 5+ fraud detection algorithms
2. Scored for risk (0-100%)
3. Automatically blacklisted if fraudulent
4. Stored for future reference

**Happy fraud hunting! 🕵️‍♂️**