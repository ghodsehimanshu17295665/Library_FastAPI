# 📚 Library Management System API

A robust REST API for managing a digital library using **FastAPI** and **PostgreSQL**. This system supports operations for authors, books, categories, students, courses, book issuance, fines, authentication, and now includes **pagination** and **email notifications**.

---

## ✨ Key Features

✅ Full CRUD operations for Authors, Books, Categories, Courses, Students, and Fines  
✅ JWT-based Authentication (Login, Signup, Logout)  
✅ Role-based restrictions (e.g., only admins can manage books)  
✅ Secure password hashing  
✅ Issued Book tracking & fine calculation APIs  
✅ Swagger Documentation included by default  
✅ Limit-Offset Pagination support for listing APIs  
✅ Email Notification System integrated (e.g., registration success, due reminders)  
✅ Follows clean architecture with routers and modular design  

---

## 🗂️ Project Structure
```
Library_FastAPI/
├── app/
│ ├── init.py
│ ├── main.py # FastAPI entry point
│ ├── auth.py # JWT authentication utilities
│ ├── database.py # Database setup and session
│ ├── models.py # SQLAlchemy models
│ ├── schemas.py # Pydantic schemas
│ ├── utils/ # Utility modules (pagination, email)
│ │ ├── pagination.py # Custom limit-offset pagination class
│ │ └── email.py # Email utility for notifications
│ ├── routers/ # API route handlers
│ │ ├── author.py
│ │ ├── book.py
│ │ ├── category.py
│ │ ├── course.py
│ │ ├── issued_book.py
│ │ └── user.py
├── requirements.txt
├── README.md
└── .env.example
```

---

## 🛠️ Technologies Used

- **FastAPI** - High-performance web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database models
- **Pydantic** - Data validation and parsing
- **JWT (Simple JWT)** - Token-based authentication
- **Docker** - (Optional for containerized setup)
- **Black** & **isort** - For code formatting and import sorting
- **SMTP (Email)** - Used for sending email notifications
- **Custom Pagination** - Reusable limit-offset pagination utility

---

## 🚀 Installation

```bash
1. **Clone the Repository**

git clone https://github.com/ghodsehimanshu17295665/Library_FastAPI.git
cd Library_FastAPI

2. **Create Virtual Environment**

python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

3. **Install Dependencies**

pip install -r requirements.txt

4. **Configure Environment Variables**
Rename .env.example to .env and add your DB and email details:

DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your_jwt_secret

# For email notifications
EMAIL_HOST=smtp.yourmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@example.com
EMAIL_PASSWORD=your_email_password
EMAIL_FROM_NAME=Library API

5. **Run the Application**

uvicorn app.main:app --reload

6. **Access API**

Swagger UI: http://127.0.0.1:8000/docs  
Redoc UI: http://127.0.0.1:8000/redoc
```

## 📩 Pagination Support
```bash
You can now paginate list endpoints using query parameters:

GET /books/?limit=5&offset=10

limit: Number of records to return (default: 5)

offset: Number of records to skip (default: 0)

✅ Pagination is applied across multiple list APIs like books, authors, categories, etc.
```

## Authentication
```bash
Register (Students): POST /users/register

Login: POST /users/login

Authenticated actions require Bearer Token in Authorization header.
```

## 🧾 Git Branch Guide
```bash

| Branch Name                   | Purpose                                              |
|------------------------------|------------------------------------------------------|
| `main`                       | Stable production-ready version                      |
| `task01-model-creation`      | Added models for Author, Book, Category, etc.        |
| `task02-author-crud-api`     | CRUD API implementation for Authors                  |
| `task03-crud-api`            | CRUD APIs for Book, Category, Course                 |
| `task04-IssuedBooks-crudAPI`| Issued books CRUD & fine logic added                 |
| `task06-applyPagination`     | Applied pagination and integrated email notification |
```
