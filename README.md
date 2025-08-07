# Financial Fraud Detection System

A comprehensive web-based fraud detection system built with FastAPI backend and modern web frontend. The system analyzes financial transactions in real-time and flags potentially fraudulent activities based on multiple detection algorithms.

## Features

### 🔐 Authentication System
- User registration and login
- JWT-based authentication
- Secure password hashing with bcrypt

### 🛡️ Fraud Detection Algorithms
- **Blacklisted IP Detection**: Flags transactions from known malicious IP addresses
- **Blacklisted Account Detection**: Identifies transactions to/from blacklisted recipient accounts
- **Time-based Analysis**: Detects transactions at odd hours (12 AM - 4 AM)
- **Amount Anomaly Detection**: Uses z-score analysis to identify abnormal transaction amounts
- **Geographic Drift Detection**: Flags transactions >500km from last known location

### 📊 Web Interface
- **Transaction Input Form**: Easy-to-use form for entering transaction details
- **Real-time Analysis**: Instant fraud detection results with detailed reasoning
- **Transaction History**: View all processed transactions
- **Flagged Transactions**: Dedicated view for fraudulent transactions
- **Blacklist Management**: View and manage blacklisted items

### 🗄️ Database Integration
- MongoDB for data persistence
- Automatic blacklist initialization
- Transaction logging and audit trail

## Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **Database**: MongoDB with PyMongo
- **Authentication**: JWT tokens, bcrypt password hashing
- **Geolocation**: GeoPy for distance calculations
- **Analytics**: NumPy, SciPy for statistical analysis
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI**: Modern responsive design with Font Awesome icons

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MongoDB (local installation or MongoDB Atlas)
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fraud-detection-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=fraud_detection
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

### 4. Start MongoDB
Make sure MongoDB is running on your system:
```bash
# For local MongoDB installation
mongod

# Or use MongoDB Atlas (cloud)
# Update MONGO_URI in .env with your Atlas connection string
```

### 5. Run the Application
```bash
python main.py
```

The application will start on `http://localhost:8000`

## Usage

### Access the Web Interface
1. Open your browser and go to `http://localhost:8000/app`
2. Click "Sign In" to create an account or log in
3. Fill out the registration form or use existing credentials

### Check Transactions for Fraud
1. Navigate to the "New Transaction" tab
2. Fill out the transaction form with the following fields:
   - **Transaction ID**: Unique identifier (e.g., TXN123456789)
   - **Timestamp**: Date and time of transaction
   - **Amount**: Transaction amount (must be positive)
   - **Currency**: Select from USD, EUR, GBP, INR, JPY
   - **Location**: City name (e.g., "Chennai", "New York")
   - **Card Type**: Visa, MasterCard, American Express, Discover
   - **Recipient Account**: Account number receiving the funds

3. Click "Check for Fraud" to analyze the transaction
4. View the detailed results including:
   - Fraud status (Safe/Fraudulent)
   - Risk score (0-100%)
   - Detailed fraud indicators if applicable

### View Transaction History
- **Transaction History**: View all processed transactions
- **Flagged Transactions**: See only transactions flagged as fraudulent
- **Blacklist**: View all blacklisted IPs and accounts

## API Endpoints

### Authentication
- `POST /signup` - User registration
- `POST /login` - User login

### Fraud Detection
- `POST /check_fraud` - Analyze transaction for fraud
- `GET /transactions` - Get all transactions
- `GET /flagged_transactions` - Get flagged transactions only
- `GET /blacklist` - Get blacklist items

### Utility
- `GET /` - API health check
- `GET /app` - Serve web application

## Fraud Detection Logic

### Risk Scoring System
Each fraud indicator contributes to a total risk score:
- **Blacklisted IP**: +30 points
- **Blacklisted Account**: +40 points
- **Odd Hours Transaction**: +15 points
- **Amount Anomaly (z-score > 2)**: +20 points
- **Geographic Drift (>500km)**: +25 points

A transaction is flagged as fraudulent if:
- Any fraud indicator is detected, OR
- Total risk score ≥ 30%

### Automatic Blacklisting
When a transaction is flagged as fraudulent, the recipient account is automatically added to the blacklist for future detection.

## Predefined Test Data

The system comes with predefined blacklisted items for testing:

**Blacklisted IPs:**
- 192.168.1.100
- 10.0.0.50
- 172.16.0.25
- 203.0.113.45
- 198.51.100.78

**Blacklisted Accounts:**
- ACC123456789
- ACC987654321
- ACC555666777
- ACC111222333

## Development

### Project Structure
```
fraud-detection-system/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # Documentation
├── static/                # Frontend files
│   ├── index.html         # Main web interface
│   ├── styles.css         # Styling
│   └── script.js          # JavaScript functionality
```

### Adding New Fraud Detection Rules
To add new fraud detection algorithms:

1. Create a new detection function in `main.py`
2. Add it to the `detect_fraud()` function
3. Assign appropriate risk score points
4. Update the frontend to display new fraud reasons

### Database Schema

**Users Collection:**
```json
{
  "_id": "ObjectId",
  "username": "string",
  "email": "string",
  "password": "hashed_string",
  "created_at": "datetime"
}
```

**Transactions Collection:**
```json
{
  "_id": "ObjectId",
  "transaction_id": "string",
  "timestamp": "string",
  "amount": "float",
  "location": "string",
  "card_type": "string",
  "currency": "string",
  "recipient_account_number": "string",
  "is_fraud": "boolean",
  "fraud_reasons": ["array of strings"],
  "risk_score": "float",
  "checked_by": "string",
  "checked_at": "datetime"
}
```

**Blacklist Collection:**
```json
{
  "_id": "ObjectId",
  "type": "string", // "ip" or "account"
  "value": "string",
  "added_at": "datetime",
  "reason": "string"
}
```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **Input Validation**: Pydantic models for request validation
- **CORS Protection**: Configurable cross-origin resource sharing
- **SQL Injection Prevention**: MongoDB NoSQL database
- **XSS Protection**: Input sanitization and validation

## Performance Considerations

- **Async/Await**: FastAPI's async support for better performance
- **Database Indexing**: Consider adding indexes on frequently queried fields
- **Caching**: Implement Redis caching for frequently accessed data
- **Rate Limiting**: Add rate limiting for API endpoints
- **Connection Pooling**: MongoDB connection pooling for better performance

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check MONGO_URI in .env file
   - Verify network connectivity

2. **Authentication Issues**
   - Check SECRET_KEY in .env file
   - Clear browser localStorage and try again
   - Verify JWT token expiration

3. **Geolocation Errors**
   - Some locations might not be found
   - Check internet connectivity for geocoding
   - Consider using more specific location names

4. **Port Already in Use**
   - Change port in main.py: `uvicorn.run(app, host="0.0.0.0", port=8001)`
   - Or kill existing process on port 8000

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Create an issue in the repository

---

Built with ❤️ for financial security and fraud prevention.
