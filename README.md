# Energy Market Optimizer

A powerful web service that optimizes charge/discharge cycles for energy storage systems based on electricity market data.

## 📋 Overview

Energy Market Optimizer helps users maximize profits from energy arbitrage operations by analyzing market prices and identifying the most profitable charge/discharge cycles based on real-time electricity market data.

## ✨ Features

- **Market Data Analysis**: Retrieve electricity price data via API or CSV upload
- **Cycle Optimization**: Automatically identify the most profitable charge/discharge cycles
- **Customizable Profit Threshold**: Set minimum profitability requirements
- **Result Export**: Download optimization results in JSON or CSV format
- **Responsive UI**: User-friendly interface that works on all devices
- **Visual Data Representation**: Clear presentation of optimization results with color-coded indicators

## 🔧 Technical Requirements

- Python 3.8+
- FastAPI framework
- Docker & Docker Compose (optional)
- Modern web browser

## 🚀 Installation & Deployment

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/energy_optimizer.git
   cd energy_optimizer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file as needed
   ```

5. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Deployment

1. Make sure Docker and Docker Compose are installed
2. Create .env file from .env.example
3. Build and run the container:
   ```bash
   docker-compose up -d
   ```

### Render Deployment

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add required environment variables
5. Deploy the service

## 📚 API Documentation

Once the service is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 Usage Examples

### Retrieving Market Data

```python
import requests

url = "http://localhost:8000/api/v1/market-data/"
params = {
    "start_date": "2023-01-01T00:00:00",
    "end_date": "2023-01-02T00:00:00"
}

response = requests.get(url, params=params)
data = response.json()
```

### Optimizing Cycles

```python
import requests

url = "http://localhost:8000/api/v1/optimization/optimize"
payload = {
    "start_date": "2023-01-01T00:00:00",
    "end_date": "2023-01-07T00:00:00",
    "threshold": 0.5
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
cycles = response.json()
```

## ⚙️ Configuration Options

The application can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| DEBUG | Enable debug mode | False |
| LOG_LEVEL | Logging level | "INFO" |
| ALLOW_TEST_DATA | Use test data when real data unavailable | True |
| API_RATE_LIMIT | API rate limit (requests per minute) | 60 |

## 🧪 Testing

Run the test suite with:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=app tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

