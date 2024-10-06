# **Project Overview**

Shanyrak is a dynamic real estate marketplace that connects property owners and seekers in Kazakhstan. The platform allows users to create, modify, and delete property listings, along with the ability to add and manage comments. This Minimum Viable Product (MVP) focuses on essential features like user registration, property management, and commenting functionality.


# **Features**

User Registration: Users can register on the platform by providing essential details like email, phone number, password, name, and city.

User Authentication: Utilizing OAuth2PasswordBearer, the platform ensures secure user authentication.

User Profile Management: Authenticated users can update their personal information, including phone number, name, and city.

Property Listing Creation: Users can create property listings with details such as type, price, address, area, number of rooms, and a description.

Property Listing Modification and Deletion: Authenticated users can modify and delete their property listings.

Commenting System: Users can add comments to property listings, providing valuable insights and feedback.

Comment Management: Users can modify and delete their comments on property listings.

API Endpoints: The project exposes various API endpoints for user registration, authentication, property listing management, and commenting.


# **Technology Stack**

FastAPI: A modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.

SQLAlchemy: A powerful and flexible SQL toolkit and Object-Relational Mapping (ORM) library for Python.

Alembic: A lightweight database migration tool for usage with SQLAlchemy.


# **Installation**
Clone the Repository:
```
git clone https://github.com/dimalbek/Shanyrak.git
cd Shanyrak
```

Set up a Virtual Environment (optional but recommended):
```
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install Dependencies:
```
pip install poetry # if not installed
poetry install
```

Initialize the Database:
```
alembic upgrade head
```

Run the Application:
```
uvicorn app.main:app --reload
```
The API will now be accessible at http://127.0.0.1:8000 .
You may check endpoints at http://127.0.0.1:8000/docs .


# **API Endpoints**

User Authentication

POST /auth/users: Register a new user.
POST /auth/users/login: Log in with email and password.
GET /auth/users/me: View user profile information.
PATCH /auth/users/me: Modify profile information.
POST /auth/users/favorites/shanyraks/{id}: Add post to favorite
DELETE /auth/users/favorites/shanyraks/{id}: Delete post from favorite
GET /auth/users/favorites/shanyraks: Get list of favorite posts
Property Listings

POST /shanyraks: Create a new property listing
GET /shanyraks: Get list of propersy listing
GET /shanyraks/{id}: Retrieve details of a property listing.
PATCH /shanyraks/{id}: Modify details of a property listing.
DELETE /shanyraks/{id}: Delete a property listing.
Comments

POST /shanyraks/{id}/comments: Add a comment to a property listing.
GET /shanyraks/{id}/comments: Retrieve comments for a property listing.
PATCH /shanyraks/{id}/comments/{comment_id}: Modify a comment on a property listing.
DELETE /shanyraks/{id}/comments/{comment_id}: Delete a comment on a property listing.

## **Author**
Developed by Dinmukhamed Albek.
