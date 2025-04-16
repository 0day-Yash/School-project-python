# 📚 AI-Powered Smart Library Management System

Welcome to the **AI-Powered Smart Library Management System** – a Python-based project built for managing a library using smart features like AI-based recommendations, automated borrowing logs, and a simple database.

This project is designed for high schoolers, hobby coders, or beginners with a basic understanding of Python, file handling, and libraries like SQLite and `scikit-learn`.

## ✅ Key Features

### 1. 📖 Book Database & Storage
- Stores book details (title, author, genre, ISBN, availability) in an SQLite database
- Supports CSV/JSON export for backups
- Import bulk books from CSV files

### 2. 🧠 AI-Based Book Recommendations
- Recommends books based on genre, author, or past borrow history
- Uses TF-IDF from scikit-learn to compare book descriptions

### 3. 🔍 Smart Search & Filtering
- Search for books by title, author, genre, or keywords
- Filter by available or borrowed status

### 4. 🔁 Borrowing & Return System
- Lets users borrow or return books
- Tracks due dates and notifies (text logs) users for overdue books

### 5. 📛 Duplicate Book Detection
- Detects duplicate books using MD5 hashing
- Warns admin if a book already exists in the database

## 🛠️ Project Structure

```
/library_system
├── main.py                # Main application file
├── database/              # SQLite database storage
│   └── books.db           # Books database
├── data/                  # Data import/export directory
│   ├── books.csv          # Sample CSV data
│   └── books.json         # JSON export
├── ai/                    # AI components
├── logs/                  # System logs
│   └── overdue_log.txt    # Overdue books log
```

## 📦 Requirements

```
pip install scikit-learn
```

Python modules used:
- sqlite3
- csv, json, datetime, hashlib
- sklearn (TF-IDF)
- os, sys for file handling

## 🚀 Getting Started

1. Clone this repository
2. Install the required packages: `pip install scikit-learn`
3. Run the application: `python main.py`
4. Follow the on-screen menu to manage your library

## 📋 Usage Guide

1. **Add Books**: Add new books with title, author, genre, ISBN, and description
2. **Search Books**: Find books using keywords and filter by availability
3. **Borrow/Return**: Track book borrowing with due dates
4. **Get Recommendations**: Get AI-powered book recommendations
5. **Import/Export**: Backup your library data or import books in bulk
6. **Check Overdue**: Monitor overdue books and generate reports

## 🤝 Contributing

Feel free to fork this project and add your own features or improvements!