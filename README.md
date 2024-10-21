# TopStockAPI

### Overview
**TopStockAPI** is a Django REST API that provides information about stocks, including real-time data and analysis features. The API allows users to retrieve stock details, analyze stock performance, and obtain ratings for different trading strategies.

---

### Key Features
- **Stock Information Retrieval**: Retrieve detailed information about different stocks, including current prices, historical data, and performance metrics.
- **Stock Analysis**: Provides analyses based on various trading strategies (e.g., swing trading, day trading, position trading, scalp trading).
- **RESTful Endpoints**: A set of RESTful API endpoints to interact with the stock data.

---

### Project Structure
The project is structured as follows:

```
TopStockAPI-main/
|— README.md
|— stockproject/
    |— Dockerfile                # Docker configuration for the API
    |— db.sqlite3                # SQLite database file for local development
    |— manage.py                 # Django's management script
    |— requirements.txt          # Python dependencies
    |— stockproject/             # Django project settings and configurations
    |— stocks/                   # Main application containing stock functionalities
        |— admin.py              # Django admin configurations
        |— models.py             # Models for stock data
        |— serializers.py        # Serializers for converting data to/from JSON
        |— views.py              # Views that handle API requests
        |— urls.py               # URL routing for the API
        |— stock_analyses/       # Scripts for stock analysis and calculating ratings
        |— stock_info/           # Modules for retrieving and processing stock information
```

---

### Installation

#### Prerequisites
- **Python 3.8+**
- **Docker**

#### Steps to Set Up the Project

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd TopStockAPI-main/stockproject
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Run the Server**
   ```bash
   python manage.py runserver
   ```
   The server will start at `http://127.0.0.1:8000/`.

---

### Running with Docker

1. **Build the Docker Image**
   ```bash
   docker build -t topstockapi .
   ```

2. **Run the Docker Container**
   ```bash
   docker run -p 8000:8000 topstockapi
   ```
   This will run the API in a Docker container and expose it on port 8000.

---

### API Endpoints

- **`GET /stocks/`**: Retrieve a list of all stocks with basic information.
- **`GET /stocks/<symbol>/`**: Retrieve details about a specific stock.
- **`GET /stocks/analyze/`**: Run an analysis on a specific stock or group of stocks.

---
