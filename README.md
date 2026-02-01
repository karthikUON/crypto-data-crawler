# 🚀 Cryptocurrency Data Crawler

[![CI/CD Pipeline](https://github.com/karthikUON/crypto-data-crawler/actions/workflows/ci.yml/badge.svg)](https://github.com/karthikUON/crypto-data-crawler/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A production-ready cryptocurrency data engineering and DevOps pipeline built for the **Binance Accelerator Program - Software Engineer (DevOps & Data)** application.

## 📋 Overview

This project demonstrates a complete end-to-end data engineering pipeline that fetches real-time cryptocurrency prices from CoinGecko API, stores them in PostgreSQL, and exposes the data through a RESTful API. Built with modern DevOps practices including Docker containerization, CI/CD automation, and comprehensive testing.

## ✨ Key Features

- **🔄 Automated Data Pipeline**: Continuous cryptocurrency price data collection from CoinGecko API
- **🗄️ Robust Data Storage**: PostgreSQL database with optimized indexes for query performance
- **🌐 RESTful API**: FastAPI-based API with OpenAPI documentation
- **🐳 Full Containerization**: Multi-stage Docker builds with docker-compose orchestration
- **🔒 Security First**: Non-root containers, dependency scanning, code security analysis
- **✅ Comprehensive Testing**: Unit tests, integration tests, 80%+ code coverage
- **🚀 CI/CD Pipeline**: Automated linting, testing, security scans, and builds
- **📊 Production-Ready**: Structured logging, error handling, retry logic, health checks

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/karthikUON/crypto-data-crawler.git
cd crypto-data-crawler

# Start all services
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Get cryptocurrency prices
curl http://localhost:8000/api/v1/prices

# Stop services
docker-compose down
```

## 📚 API Documentation

Once the API is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run linting
black .
isort .
flake8 .
```

## 📁 Project Structure

```
crypto-data-crawler/
├── api/                      # FastAPI application
├── crawler/                  # Data crawler module
├── db/                       # Database module
├── tests/                    # Test suite
├── docker/                   # Docker configuration
├── .github/workflows/        # CI/CD pipeline
├── docker-compose.yml        # Service orchestration
├── requirements.txt          # Production dependencies
└── requirements-dev.txt      # Development dependencies
```

## 🛠️ Tech Stack

- **Python 3.11** - Modern Python with type hints
- **FastAPI** - High-performance async web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL 15** - Reliable relational database
- **Docker** - Containerization
- **GitHub Actions** - CI/CD automation
- **pytest** - Testing framework

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Karthik Lingala**

- GitHub: [@karthikUON](https://github.com/karthikUON)
- Project: Built for Binance Accelerator Program Application

---

**⭐ If you find this project useful, please consider giving it a star!**
