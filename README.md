# Simple Blogging Platform

A simple blogging platform built with Flask that includes user authentication, blog post creation, editing, and deletion.

## Features

- User registration and authentication
- Create, read, update, and delete blog posts
- Responsive design using Bootstrap
- SQLite database for data storage

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/simple-blog-platform.git
   cd simple-blog-platform
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following content:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///blog.db
   ```

5. Run the application:
   ```
   python run.py
   ```

6. Open your browser and navigate to `http://localhost:12000`

## Project Structure

```
blog_platform/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── post.py
│   │   └── user.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── blog.py
│   │   └── main.py
│   ├── static/
│   │   └── css/
│   │       └── main.css
│   ├── templates/
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── blog/
│   │   │   ├── create_post.html
│   │   │   └── post.html
│   │   ├── base.html
│   │   └── index.html
│   ├── __init__.py
│   └── forms.py
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

## Technologies Used

- Flask: Web framework
- Flask-Login: User authentication
- Flask-SQLAlchemy: Database ORM
- Flask-WTF: Form handling
- Bootstrap: Frontend styling
- SQLite: Database

## License

This project is licensed under the MIT License - see the LICENSE file for details.
