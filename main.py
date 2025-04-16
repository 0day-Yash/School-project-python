#!/usr/bin/env python3
# AI-Powered Smart Library Management System

import os
import sys
import sqlite3
import csv
import json
import datetime
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure directories exist
for directory in ['database', 'data', 'ai', 'logs']:
    os.makedirs(os.path.join(os.path.dirname(__file__), directory), exist_ok=True)

class LibraryDatabase:
    def __init__(self, db_path='database/books.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print("Connected to the database successfully.")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            sys.exit(1)
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # Books table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT,
                isbn TEXT UNIQUE,
                description TEXT,
                availability BOOLEAN DEFAULT 1,
                due_date TEXT,
                hash TEXT UNIQUE
            )
            ''')
            
            # Borrowing history table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrow_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                user_name TEXT,
                borrow_date TEXT,
                return_date TEXT,
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
            ''')
            
            self.conn.commit()
            print("Tables created successfully.")
        except sqlite3.Error as e:
            print(f"Table creation error: {e}")
    
    def add_book(self, title, author, genre, isbn, description=""):
        """Add a new book to the database"""
        # Create hash for duplicate detection
        book_hash = self._create_book_hash(title, author, isbn)
        
        # Check for duplicates
        if self._is_duplicate(book_hash):
            print(f"Warning: The book '{title}' by {author} already exists in the database.")
            return False
        
        try:
            self.cursor.execute('''
            INSERT INTO books (title, author, genre, isbn, description, hash)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, author, genre, isbn, description, book_hash))
            self.conn.commit()
            print(f"Book '{title}' added successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error adding book: {e}")
            return False
    
    def _create_book_hash(self, title, author, isbn):
        """Create MD5 hash from book details for duplicate detection"""
        hash_string = f"{title.lower()}{author.lower()}{isbn}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _is_duplicate(self, book_hash):
        """Check if a book with the same hash already exists"""
        self.cursor.execute("SELECT COUNT(*) FROM books WHERE hash = ?", (book_hash,))
        count = self.cursor.fetchone()[0]
        return count > 0
    
    def search_books(self, query, filter_available=None):
        """Search for books by title, author, genre, or keywords"""
        search_query = f"%{query}%"
        sql_query = '''
        SELECT * FROM books 
        WHERE title LIKE ? OR author LIKE ? OR genre LIKE ? OR description LIKE ?
        '''
        params = (search_query, search_query, search_query, search_query)
        
        # Add availability filter if specified
        if filter_available is not None:
            sql_query += " AND availability = ?"
            params = params + (1 if filter_available else 0,)
        
        try:
            self.cursor.execute(sql_query, params)
            results = self.cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"Search error: {e}")
            return []
    
    def borrow_book(self, book_id, user_name, days=14):
        """Mark a book as borrowed and record in history"""
        try:
            # Check if book is available
            self.cursor.execute("SELECT availability FROM books WHERE id = ?", (book_id,))
            result = self.cursor.fetchone()
            
            if not result or not result[0]:
                print("Book is not available for borrowing.")
                return False
            
            # Calculate due date
            borrow_date = datetime.datetime.now()
            due_date = borrow_date + datetime.timedelta(days=days)
            
            # Update book availability
            self.cursor.execute('''
            UPDATE books 
            SET availability = 0, due_date = ? 
            WHERE id = ?
            ''', (due_date.strftime("%Y-%m-%d"), book_id))
            
            # Record in borrow history
            self.cursor.execute('''
            INSERT INTO borrow_history (book_id, user_name, borrow_date, return_date)
            VALUES (?, ?, ?, NULL)
            ''', (book_id, user_name, borrow_date.strftime("%Y-%m-%d")))
            
            self.conn.commit()
            print(f"Book borrowed successfully. Due date: {due_date.strftime('%Y-%m-%d')}")
            return True
        except sqlite3.Error as e:
            print(f"Error borrowing book: {e}")
            return False
    
    def return_book(self, book_id):
        """Mark a book as returned and update history"""
        try:
            # Check if book is borrowed
            self.cursor.execute("SELECT availability FROM books WHERE id = ?", (book_id,))
            result = self.cursor.fetchone()
            
            if not result or result[0]:
                print("Book is not currently borrowed.")
                return False
            
            # Update book availability
            self.cursor.execute('''
            UPDATE books 
            SET availability = 1, due_date = NULL 
            WHERE id = ?
            ''', (book_id,))
            
            # Update borrow history
            return_date = datetime.datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute('''
            UPDATE borrow_history 
            SET return_date = ? 
            WHERE book_id = ? AND return_date IS NULL
            ''', (return_date, book_id))
            
            self.conn.commit()
            print("Book returned successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error returning book: {e}")
            return False
    
    def export_to_csv(self, filename='data/books.csv'):
        """Export books data to CSV file"""
        try:
            self.cursor.execute("SELECT * FROM books")
            books = self.cursor.fetchall()
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow([description[0] for description in self.cursor.description])
                # Write data
                writer.writerows(books)
            
            print(f"Data exported to {filename} successfully.")
            return True
        except (sqlite3.Error, IOError) as e:
            print(f"Export error: {e}")
            return False
    
    def export_to_json(self, filename='data/books.json'):
        """Export books data to JSON file"""
        try:
            self.cursor.execute("SELECT * FROM books")
            books = self.cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = [description[0] for description in self.cursor.description]
            book_list = [dict(zip(columns, book)) for book in books]
            
            with open(filename, 'w') as jsonfile:
                json.dump(book_list, jsonfile, indent=4)
            
            print(f"Data exported to {filename} successfully.")
            return True
        except (sqlite3.Error, IOError) as e:
            print(f"Export error: {e}")
            return False
    
    def import_from_csv(self, filename='data/books.csv'):
        """Import books from CSV file"""
        try:
            with open(filename, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                imported_count = 0
                
                for row in reader:
                    # Skip if book already exists
                    book_hash = self._create_book_hash(row['title'], row['author'], row['isbn'])
                    if not self._is_duplicate(book_hash):
                        self.add_book(
                            row['title'], 
                            row['author'], 
                            row['genre'], 
                            row['isbn'], 
                            row.get('description', '')
                        )
                        imported_count += 1
            
            print(f"Imported {imported_count} books from {filename}.")
            return True
        except (IOError, KeyError) as e:
            print(f"Import error: {e}")
            return False
    
    def check_overdue_books(self):
        """Check for overdue books and log them"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        try:
            self.cursor.execute('''
            SELECT b.id, b.title, b.author, b.due_date, h.user_name 
            FROM books b 
            JOIN borrow_history h ON b.id = h.book_id 
            WHERE b.availability = 0 AND b.due_date < ? AND h.return_date IS NULL
            ''', (today,))
            
            overdue_books = self.cursor.fetchall()
            
            if overdue_books:
                log_file = os.path.join(os.path.dirname(__file__), 'logs/overdue_log.txt')
                with open(log_file, 'a') as f:
                    f.write(f"\n--- Overdue Books Report ({today}) ---\n")
                    for book in overdue_books:
                        book_id, title, author, due_date, user = book
                        f.write(f"Book: {title} by {author}\n")
                        f.write(f"Due Date: {due_date}\n")
                        f.write(f"Borrowed by: {user}\n")
                        f.write("-" * 40 + "\n")
                
                print(f"Found {len(overdue_books)} overdue books. Check logs/overdue_log.txt for details.")
            else:
                print("No overdue books found.")
                
            return overdue_books
        except sqlite3.Error as e:
            print(f"Error checking overdue books: {e}")
            return []
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")


class BookRecommender:
    def __init__(self, library_db):
        self.library_db = library_db
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def get_recommendations_by_description(self, book_id, num_recommendations=5):
        """Recommend books based on description similarity"""
        try:
            # Get all books with descriptions
            self.library_db.cursor.execute("SELECT id, title, author, description FROM books WHERE description != ''")
            books = self.library_db.cursor.fetchall()
            
            if not books:
                print("No books with descriptions found.")
                return []
            
            # Get target book
            target_book = None
            for book in books:
                if book[0] == book_id:
                    target_book = book
                    break
            
            if not target_book:
                print(f"Book with ID {book_id} not found or has no description.")
                return []
            
            # Extract descriptions and create TF-IDF matrix
            book_ids = [book[0] for book in books]
            descriptions = [book[3] for book in books]
            tfidf_matrix = self.vectorizer.fit_transform(descriptions)
            
            # Calculate similarity
            target_idx = book_ids.index(book_id)
            cosine_similarities = cosine_similarity(tfidf_matrix[target_idx], tfidf_matrix).flatten()
            
            # Get top similar books (excluding the target book)
            similar_indices = cosine_similarities.argsort()[:-(num_recommendations+2):-1]
            similar_indices = [idx for idx in similar_indices if book_ids[idx] != book_id]
            
            # Get recommended books
            recommendations = []
            for idx in similar_indices[:num_recommendations]:
                recommendations.append({
                    'id': book_ids[idx],
                    'title': books[idx][1],
                    'author': books[idx][2],
                    'similarity': cosine_similarities[idx]
                })
            
            return recommendations
        except Exception as e:
            print(f"Recommendation error: {e}")
            return []
    
    def get_recommendations_by_genre(self, genre, num_recommendations=5):
        """Recommend books based on genre"""
        try:
            self.library_db.cursor.execute('''
            SELECT id, title, author, genre 
            FROM books 
            WHERE genre LIKE ? AND availability = 1
            LIMIT ?
            ''', (f"%{genre}%", num_recommendations))
            
            books = self.library_db.cursor.fetchall()
            recommendations = [{
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'genre': book[3]
            } for book in books]
            
            return recommendations
        except sqlite3.Error as e:
            print(f"Genre recommendation error: {e}")
            return []
    
    def get_recommendations_by_author(self, author, num_recommendations=5):
        """Recommend books by the same author"""
        try:
            self.library_db.cursor.execute('''
            SELECT id, title, author, genre 
            FROM books 
            WHERE author LIKE ? AND availability = 1
            LIMIT ?
            ''', (f"%{author}%", num_recommendations))
            
            books = self.library_db.cursor.fetchall()
            recommendations = [{
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'genre': book[3]
            } for book in books]
            
            return recommendations
        except sqlite3.Error as e:
            print(f"Author recommendation error: {e}")
            return []
    
    def get_recommendations_by_borrow_history(self, user_name, num_recommendations=5):
        """Recommend books based on user's borrowing history"""
        try:
            # Get genres and authors the user has borrowed before
            self.library_db.cursor.execute('''
            SELECT DISTINCT b.genre, b.author 
            FROM books b 
            JOIN borrow_history h ON b.id = h.book_id 
            WHERE h.user_name = ?
            ''', (user_name,))
            
            user_preferences = self.library_db.cursor.fetchall()
            
            if not user_preferences:
                print(f"No borrowing history found for user {user_name}.")
                return []
            
            # Get books with similar genres or by the same authors
            recommendations = []
            for genre, author in user_preferences:
                # Get books with similar genre
                if genre:
                    genre_recs = self.get_recommendations_by_genre(genre, 2)
                    recommendations.extend(genre_recs)
                
                # Get books by the same author
                if author:
                    author_recs = self.get_recommendations_by_author(author, 2)
                    recommendations.extend(author_recs)
            
            # Remove duplicates and limit to requested number
            unique_recommendations = []
            seen_ids = set()
            
            for rec in recommendations:
                if rec['id'] not in seen_ids and len(unique_recommendations) < num_recommendations:
                    seen_ids.add(rec['id'])
                    unique_recommendations.append(rec)
            
            return unique_recommendations
        except sqlite3.Error as e:
            print(f"History recommendation error: {e}")
            return []


def main_menu():
    """Display the main menu and handle user input"""
    library = LibraryDatabase()
    recommender = BookRecommender(library)
    
    while True:
        print("\n===== AI-Powered Smart Library Management System =====")
        print("1. Add a new book")
        print("2. Search for books")
        print("3. Borrow a book")
        print("4. Return a book")
        print("5. Get book recommendations")
        print("6. Export data (CSV/JSON)")
        print("7. Import books from CSV")
        print("8. Check overdue books")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ")
        
        if choice == '1':
            # Add a new book
            title = input("Enter book title: ")
            author = input("Enter author name: ")
            genre = input("Enter genre: ")
            isbn = input("Enter ISBN: ")
            description = input("Enter book description (optional): ")
            
            library.add_book(title, author, genre, isbn, description)
        
        elif choice == '2':
            # Search for books
            query = input("Enter search term: ")
            availability = input("Filter by availability? (y/n): ").lower()
            
            filter_available = None
            if availability == 'y':
                filter_available = True
            elif availability == 'n':
                filter_available = False
            
            results = library.search_books(query, filter_available)
            
            if results:
                print("\nSearch Results:")
                for book in results:
                    print(f"ID: {book[0]} | Title: {book[1]} | Author: {book[2]} | ")
                    print(f"Genre: {book[3]} | Available: {'Yes' if book[6] else 'No'}")
                    if not book[6]:  # If not available
                        print(f"Due Date: {book[7]}")
                    print("-" * 50)
            else:
                print("No books found matching your search.")
        
        elif choice == '3':
            # Borrow a book
            book_id = input("Enter book ID to borrow: ")
            user_name = input("Enter your name: ")
            days = input("Enter loan period in days (default 14): ")
            
            try:
                book_id = int(book_id)
                days = int(days) if days else 14
                library.borrow_book(book_id, user_name, days)
            except ValueError:
                print("Please enter valid numbers.")
        
        elif choice == '4':
            # Return a book
            book_id = input("Enter book ID to return: ")
            
            try:
                book_id = int(book_id)
                library.return_book(book_id)
            except ValueError:
                print("Please enter a valid book ID.")
        
        elif choice == '5':
            # Get recommendations
            print("\nRecommendation Options:")
            print("1. By book similarity")
            print("2. By genre")
            print("3. By author")
            print("4. Based on borrowing history")
            
            rec_choice = input("Enter choice (1-4): ")
            
            if rec_choice == '1':
                book_id = input("Enter book ID to find similar books: ")
                try:
                    recommendations = recommender.get_recommendations_by_description(int(book_id))
                    if recommendations:
                        print("\nRecommended Books:")
                        for rec in recommendations:
                            print(f"ID: {rec['id']} | Title: {rec['title']} | Author: {rec['author']}")
                            print(f"Similarity: {rec['similarity']:.2f}")
                            print("-" * 50)
                except ValueError:
                    print("Please enter a valid book ID.")
            
            elif rec_choice == '2':
                genre = input("Enter genre: ")
                recommendations = recommender.get_recommendations_by_genre(genre)
                if recommendations:
                    print("\nRecommended Books:")
                    for rec in recommendations:
                        print(f"ID: {rec['id']} | Title: {rec['title']} | Author: {rec['author']}")
                        print("-" * 50)
            
            elif rec_choice == '3':
                author = input("Enter author: ")
                recommendations = recommender.get_recommendations_by_author(author)
                if recommendations:
                    print("\nRecommended Books:")
                    for rec in recommendations:
                        print(f"ID: {rec['id']} | Title: {rec['title']} | Author: {rec['author']}")
                        print("-" * 50)
            
            elif rec_choice == '4':
                user_name = input("Enter user name: ")
                recommendations = recommender.get_recommendations_by_borrow_history(user_name)
                if recommendations:
                    print("\nRecommended Books Based on Your History:")
                    for rec in recommendations:
                        print(f"ID: {rec['id']} | Title: {rec['title']} | Author: {rec['author']}")
                        print("-" * 50)
        
        elif choice == '6':
            # Export data
            print("\nExport Options:")
            print("1. Export to CSV")
            print("2. Export to JSON")
            
            export_choice = input("Enter choice (1-2): ")
            
            if export_choice == '1':
                library.export_to_csv()
            elif export_choice == '2':
                library.export_to_json()
        
        elif choice == '7':
            # Import books
            filename = input("Enter CSV file path (default: data/books.csv): ")
            filename = filename if filename else 'data/books.csv'
            library.import_from_csv(filename)
        
        elif choice == '8':
            # Check overdue books
            library.check_overdue_books()
        
        elif choice == '9':
            # Exit
            library.close()
            print("Thank you for using the Library Management System. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()