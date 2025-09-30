# NLP Query Engine for Employee Data

A natural language query system that dynamically adapts to employee database schemas and handles both structured data and unstructured documents without hard-coding table names or relationships.

## 🎯 Project Overview

This system automatically discovers database schemas, processes natural language queries, and provides intelligent search across both SQL databases and document collections. It's designed to work with any reasonable employee database structure without requiring code changes.

## ✨ Key Features

- **Dynamic Schema Discovery**: Automatically detects tables, columns, and relationships
- **Natural Language Processing**: Converts human queries to SQL and document searches
- **Hybrid Search**: Combines database queries with document retrieval
- **Performance Optimization**: Caching, connection pooling, and async operations
- **Production Ready**: Handles concurrent users with sub-2-second response times
- **Adaptive Design**: Works with various database schemas without modification

## 🏗️ Architecture

```
project/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── ingestion.py      # Data ingestion endpoints
│   │   │   ├── query.py          # Query processing endpoints
│   │   │   └── schema.py         # Schema discovery endpoints
│   │   ├── services/
│   │   │   ├── schema_discovery.py    # Database schema analysis
│   │   │   ├── document_processor.py  # Document processing & embeddings
│   │   │   └── query_engine.py        # Query classification & execution
│   │   ├── models/               # Data models
│   │   └── main.py              # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DatabaseConnector.js   # DB connection interface
│   │   │   ├── DocumentUploader.js    # File upload interface
│   │   │   ├── QueryPanel.js          # Query input interface
│   │   │   └── ResultsView.js         # Results display
│   │   └── App.js
│   └── public/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL/MySQL (or SQLite for demo)
- 8GB RAM minimum

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nlp-query-engine
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Copy and configure environment
   cp .env.example .env
   # Edit .env with your database connection details
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Database Setup**
   ```bash
   # For PostgreSQL
   createdb employee_db
   
   # Run migrations (if any)
   python manage.py migrate
   ```

### Running the Application

1. **Start Backend**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm start
   ```

3. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📊 Usage Guide

### 1. Connect Database

1. Navigate to the "Connect Data" section
2. Enter your database connection string:
   ```
   postgresql://username:password@localhost:5432/employee_db
   ```
3. Click "Connect & Analyze"
4. View the discovered schema visualization

### 2. Upload Documents

1. Go to the "Documents" tab
2. Drag and drop files (PDF, DOCX, TXT, CSV)
3. Monitor processing progress
4. View ingestion status and metrics

### 3. Query Data

1. Navigate to "Query Data"
2. Enter natural language queries like:
   - "How many employees do we have?"
   - "Show me Python developers in Engineering"
   - "Average salary by department"
3. View results with performance metrics
4. Export results as CSV/JSON

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/db_name
DB_POOL_SIZE=10

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=32

# Cache
CACHE_TTL_SECONDS=300
CACHE_MAX_SIZE=1000

# Performance
MAX_CONCURRENT_QUERIES=10
QUERY_TIMEOUT_SECONDS=30
```

### Configuration File (config.yml)

```yaml
database:
  connection_string: ${DATABASE_URL}
  pool_size: 10
  timeout: 30

embeddings:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  batch_size: 32
  max_chunk_size: 1000

cache:
  ttl_seconds: 300
  max_size: 1000

performance:
  max_concurrent_users: 10
  response_time_target: 2.0
```

## 🧪 Testing

### Run Unit Tests
```bash
cd backend
pytest tests/ -v
```

### Run Integration Tests
```bash
pytest tests/integration/ -v
```

### Performance Benchmarks
```bash
python scripts/benchmark.py
```

### Test with Different Schemas

The system is tested with various schema patterns:

**Schema Variation 1:**
```sql
employees (emp_id, full_name, dept_id, position, annual_salary, join_date, office_location)
departments (dept_id, dept_name, manager_id)
```

**Schema Variation 2:**
```sql
staff (id, name, department, role, compensation, hired_on, city, reports_to)
documents (doc_id, staff_id, type, content, uploaded_at)
```

**Schema Variation 3:**
```sql
personnel (person_id, employee_name, division, title, pay_rate, start_date)
divisions (division_code, division_name, head_id)
```

## 📈 Performance Features

- **Query Caching**: Intelligent caching with TTL-based invalidation
- **Connection Pooling**: Efficient database connection management
- **Async Operations**: Non-blocking I/O for better concurrency
- **Batch Processing**: Optimized embedding generation
- **Result Pagination**: Handles large datasets efficiently

## 🔍 Supported Query Types

### Basic Queries
- Employee counts and statistics
- Salary analysis by department
- Hiring trends and dates
- Reporting relationships

### Complex Queries
- Top performers by department
- Skill-based searches with salary filters
- Performance review analysis
- Turnover rate calculations

### Document Queries
- Resume keyword searches
- Contract clause retrieval
- Performance review analysis
- Skills and experience matching

## 🛡️ Security & Production Features

- **SQL Injection Prevention**: Parameterized queries and validation
- **Error Handling**: Graceful degradation and user-friendly messages
- **Logging & Monitoring**: Comprehensive query and performance logging
- **Resource Management**: Memory and connection limits
- **Input Validation**: Sanitized user inputs and file uploads

## 🚨 Known Limitations

- Complex multi-table joins may require query simplification
- Large file uploads limited to 10MB per file
- Vector search accuracy depends on document quality
- Cache invalidation is time-based, not event-based
- Limited to SQL databases (PostgreSQL, MySQL, SQLite)

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify connection string format
   - Check database server status
   - Ensure proper credentials and permissions

2. **Slow Query Performance**
   - Check database indexes
   - Monitor concurrent query load
   - Review query complexity

3. **Document Processing Errors**
   - Verify file format support
   - Check file size limits
   - Ensure sufficient memory

4. **Schema Discovery Issues**
   - Verify database permissions
   - Check for foreign key constraints
   - Review table naming conventions

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug
```

## 📚 API Documentation

### Core Endpoints

- `POST /api/ingest/database` - Connect and analyze database
- `POST /api/ingest/documents` - Upload and process documents
- `GET /api/ingest/status/{job_id}` - Check processing status
- `POST /api/query` - Process natural language queries
- `GET /api/schema` - Get discovered schema information

### Example API Usage

```python
import requests

# Connect database
response = requests.post('/api/ingest/database', 
    json={'connection_string': 'postgresql://...'})

# Upload documents
files = {'files': open('resume.pdf', 'rb')}
response = requests.post('/api/ingest/documents', files=files)

# Query data
response = requests.post('/api/query', 
    json={'query': 'Show me Python developers'})
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or issues:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Open an issue on GitHub
- Contact the development team
