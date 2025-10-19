# Number Calculator

A simple web application that allows users to add two numbers. The frontend is built with HTML, CSS, and vanilla JavaScript, while the backend uses FastAPI (Python).

## Project Structure

```
resume-hero/
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── styles.css          # CSS styling
│   └── script.js           # JavaScript functionality
├── backend/
│   ├── main.py             # FastAPI application
│   └── requirements.txt    # Python dependencies
└── README.md               # This file
```

## Features

- Two numeric input fields (side by side)
- Input validation (only accepts numbers)
- Add button to perform calculation
- Real-time input validation
- Responsive design
- Error handling
- Clean, modern UI

## Prerequisites

- Python 3.8 or higher
- A modern web browser
- pip (Python package installer)

## Installation and Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

The frontend is static HTML/CSS/JS, so no additional setup is required. You can serve it using any web server or open it directly in a browser.

## Running the Application

### Start the Backend Server

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate your virtual environment (if you created one):
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Start the FastAPI server:
   ```bash
   python main.py
   ```

   The server will start on `http://localhost:8000`

### Start the Frontend

You have several options to serve the frontend:

#### Option 1: Using Python's built-in server
```bash
cd frontend
python -m http.server 8080
```
Then open `http://localhost:8080` in your browser.

#### Option 2: Using Node.js http-server (if you have Node.js installed)
```bash
cd frontend
npx http-server -p 8080
```
Then open `http://localhost:8080` in your browser.

#### Option 3: Open directly in browser
Simply open the `frontend/index.html` file directly in your web browser.

## Testing the Application

### Manual Testing

1. Open the frontend in your browser
2. Enter two numbers in the input fields
3. Click the "Add" button
4. Verify that the result appears below the button in green, bold text
5. Test with different number combinations:
   - Positive numbers: 5 + 3 = 8
   - Negative numbers: -5 + 3 = -2
   - Decimal numbers: 3.5 + 2.1 = 5.6
   - Zero: 0 + 5 = 5

### API Testing

You can test the backend API directly using curl:

```bash
# Test the addition endpoint
curl -X POST "http://localhost:8000/add" \
     -H "Content-Type: application/json" \
     -d '{"number1": 5, "number2": 3}'

# Expected response:
# {"result": 8, "operation": "addition"}
```

### Health Check

Test if the backend is running:

```bash
curl http://localhost:8000/health
```

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

### Common Issues

1. **Frontend can't connect to backend**
   - Ensure the backend server is running on port 8000
   - Check that there are no firewall issues blocking the connection
   - Verify the API_BASE_URL in `frontend/script.js` matches your backend URL

2. **CORS errors**
   - The backend is configured to allow all origins for development
   - In production, update the CORS settings in `backend/main.py`

3. **Port already in use**
   - If port 8000 is occupied, you can change it in `backend/main.py`
   - Update the API_BASE_URL in `frontend/script.js` accordingly

4. **Python dependencies issues**
   - Ensure you're using Python 3.8 or higher
   - Try recreating the virtual environment
   - Check that pip is up to date: `pip install --upgrade pip`

## Development

### Backend Development

The backend uses FastAPI with automatic reload enabled. Any changes to `main.py` will automatically restart the server.

### Frontend Development

The frontend is vanilla HTML/CSS/JS, so changes are immediately visible when you refresh the browser.

## Production Deployment

For production deployment:

1. Update CORS settings in `backend/main.py` to specify exact allowed origins
2. Use a production WSGI server like Gunicorn
3. Serve the frontend through a proper web server like Nginx
4. Set up proper logging and monitoring
5. Use environment variables for configuration

## License

This project is open source and available under the MIT License.