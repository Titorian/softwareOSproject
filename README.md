# 📚 Library Management System

A web-based library management system built with Flask and SQLite. Users can browse books, check them out, and return them. Staff accounts have access to an admin panel for managing the book inventory.

---

## Features

### Users
- Register and log in securely with bcrypt-hashed passwords
- Browse available books with a search bar
- Check out books (one copy per user)
- Return books from the home page
- View currently checked out books on their profile page

### Staff / Librarians
- Separate login that redirects to the staff panel
- Add new books to the library
- Delete books from the library
- View all user accounts and their checked out books with timestamps
- Protected routes — regular users cannot access staff pages

### Security
- Passwords hashed with bcrypt
- Session-based authentication
- All routes protected with session checks
- Login lockout after 3 failed attempts (60 second cooldown)

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite (two separate databases)
- **Frontend:** HTML, CSS, Jinja2 templating
- **Auth:** bcrypt

---

## Project Structure

```
softwareOSproject/
│
├── app.py                  # Main Flask application
├── book_database.db        # Books, checkouts, checkout log (auto-generated)
├── usernames_pass_database.db  # User accounts (auto-generated)
│
└── templates/
    ├── index.html          # Login page
    ├── register.html       # Registration page
    ├── forgot.html         # Forgot password page
    ├── userbooks.html      # Book browsing page (users)
    ├── userhome.html       # User home/profile page
    ├── books.html          # Browse Page ONLY
    ├── modifylib.html      # Staff panel - modify books
    └── admin.html          # Staff panel - view user accounts
```

---

## Setup & Installation

### 1. Install dependencies
```bash
pip install flask bcrypt
```

### 2. Run the app
```bash
python app.py
```

The databases are created automatically on every run. The app will be available at:
```
http://127.0.0.1:5000
```

> **Note:** The databases reset every time the app restarts. All book copy counts and checkouts are restored to their original values.

---

## Default Accounts

### Staff
| Username | Password  |
|----------|-----------|
| admin    | Admin123  |

### Users
| Username    | Password    |
|-------------|-------------|
| tim101      | ilikecats22 |
| jon3        | test12      |
| catwomen    | iamcool10   |
| heyguys21   | password4   |
| iluvreading | doggo8      |

---

## Routes

### Public
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Login page |
| `/login` | POST | Authenticate user |
| `/register` | GET, POST | Create new account |
| `/forgot` | GET, POST | Reset password |
| `/logout` | GET | Clear session |

### User (login required)
| Route | Method | Description |
|-------|--------|-------------|
| `/dashboard` | GET | Browse books |
| `/home` | GET | User profile and checked out books |
| `/checkout/<book>` | POST | Check out a book |
| `/return/<book>` | POST | Return a book |

### Staff only
| Route | Method | Description |
|-------|--------|-------------|
| `/staff` | GET | Staff panel — modify books |
| `/accounts` | GET | View all users and checkouts |
| `/add_book` | POST | Add a new book |
| `/delete_book/<title>` | GET | Delete a book |

---

## Database Structure

### book_database.db

**books**
| Column | Type | Description |
|--------|------|-------------|
| title | TEXT | Book title (primary identifier) |
| author | TEXT | Author name |
| copies | INTEGER | Number of available copies |
| genre | TEXT | Book genre |

**checkout**
| Column | Type | Description |
|--------|------|-------------|
| username | TEXT | User who checked out |
| book | TEXT | Book title |

**checkout_log**
| Column | Type | Description |
|--------|------|-------------|
| username | TEXT | User who checked out |
| book | TEXT | Book title |
| checkout_time | TEXT | Timestamp of checkout |

### usernames_pass_database.db

**login**
| Column | Type | Description |
|--------|------|-------------|
| username | TEXT | Unique username |
| passwords | TEXT | bcrypt hashed password |
| role | TEXT | `user` or `staff` |
