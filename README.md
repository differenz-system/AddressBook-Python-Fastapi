# FastAPI Address Book API

## Overview
This repository contains a **FastAPI Address Book API** that allows users to manage their contacts. It includes user authentication, contact creation, retrieval, updating, and deletion functionalities. The project demonstrates secure, scalable, and efficient API development using FastAPI and SQLAlchemy followed by **[Differenz System](http://www.differenzsystem.)**.

## Features
1. **User Authentication:**
   - Register users with username, email, and password.
   - Authenticate users using JSON Web Tokens (JWT).

2. **Contact Management:**
   - Retrieve all contacts for the authenticated user.
   - Add new contacts.
   - Update existing contact details.
   - Delete contacts.

3. **Security:**
   - Password hashing with `bcrypt`.
   - JWT-based authentication and authorization.

## Prerequisites
1. [Python 3.8+](https://www.python.org/downloads/)
2. [MySQL](https://www.mysql.com/)
3. [Pip](https://pip.pypa.io/en/stable/)

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/differenz-system/AddressBook-Python-Fastapi
cd AddressBook-Python-Fastapi
```

### 2. Set Up the Environment
1. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add the following configuration:
   ```env
   DATABASE_URL=mysql+pymysql://<user>:<password>@<host>/<database>
   SECRET_KEY=ChangeMe
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. Initialize the database:
   ```bash
   python -c "from main import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

### 3. Run the Application
Start the FastAPI application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Authentication
#### Register
**POST** `/auth/register`

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "<JWT Token>",
  "token_type": "bearer"
}
```

#### Login
**POST** `/auth/token`

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "<JWT Token>",
  "token_type": "bearer"
}
```

### Contacts
#### Get All Contacts
**GET** `/contacts`

**Headers:**
```http
Authorization: Bearer <JWT Token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "1234567890",
    "address": "123 Main St"
  }
]
```

#### Add a Contact
**POST** `/contacts`

**Headers:**
```http
Authorization: Bearer <JWT Token>
```

**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "1234567890",
  "address": "123 Main St"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "1234567890",
  "address": "123 Main St"
}
```

#### Update a Contact
**PUT** `/contacts/{contact_id}`

**Headers:**
```http
Authorization: Bearer <JWT Token>
```

**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "phone": "9876543210",
  "address": "456 Elm St"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "phone": "9876543210",
  "address": "456 Elm St"
}
```

#### Delete a Contact
**DELETE** `/contacts/{contact_id}`

**Headers:**
```http
Authorization: Bearer <JWT Token>
```

**Response:**
```json
{
  "message": "Contact deleted"
}
```

## Troubleshooting
### Common Issues
1. **Database Connection Error:** Verify the `DATABASE_URL` in the `.env` file.
2. **Invalid JWT Token:** Ensure the token is valid and not expired.
3. **Dependency Issues:** Run `pip install -r requirements.txt` to ensure all dependencies are installed.

### Useful Commands
- Run the server: `uvicorn main:app --reload`
- Activate the virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

## Support
If you encounter any issues, feel free to [open an issue](https://github.com//differenz-system/AddressBook-Python-Fastapi/issues).
