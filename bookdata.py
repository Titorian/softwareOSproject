import sqlite3





    
class Books:
    def __init__(self,title, author, copies, genre):
        self.title= title
        self.author = author
        self.copies = copies
        self.genre = genre



#varibles to hold book information
# book_title=input()
# book_author=input()
# num_of_copies=int(input())
# genre=input()

#creates a book object to be added to the database
def createbook(title,author,num_of_copies,genre):
    book = Books(title,author,num_of_copies,genre)
    return book


#books
# book1  = Books("Shadow of the Moon", "Lena Carter", 12, "Fantasy")
# book2  = Books("Digital Fortress", "Aaron Blake", 5, "Thriller")
# book3  = Books("The Last Algorithm", "Maya Singh", 8, "Sci-Fi")
# book4  = Books("Echoes of War", "Daniel Hayes", 3, "Historical Fiction")
# book5  = Books("Mind Over Matter", "Sophia Reed", 10, "Self-Help")
# book6  = Books("The Silent Forest", "Ethan Cole", 6, "Mystery")
# book7  = Books("Quantum Dreams", "Noah Bennett", 4, "Science Fiction")
# book8  = Books("Broken Chains", "Ava Morales", 7, "Drama")
# book9  = Books("Cooking with Fire", "Gordon Hale", 15, "Cooking")
# book10 = Books("The Art of Focus", "Liam Brooks", 9, "Productivity")
# book11 = Books("Ocean Depths", "Isabella Cruz", 2, "Adventure")
# book12 = Books("Hidden Truths", "Oliver Grant", 11, "Crime")   


def get_connection():
    return sqlite3.connect('book_database')

def get_books():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    connection.close()
    return books






# command1 = """CREATE TABLE IF NOT EXISTS
# books(titles TEXT PRIMARY KEY, author TEXT, copies INT, genre TEXT)"""
# cursor.execute(command1)

# #adding books to databse
# cursor.execute("INSERT INTO books (titles, author,copies,genre) VALUES (?, ?,?,?)",(book1.title,book1.author,book1.copies,book1.genre))
# cursor.execute("INSERT INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)", (book2.title, book2.author, book2.copies, book2.genre))
# cursor.execute("INSERT INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)", (book3.title, book3.author, book3.copies, book3.genre))
# cursor.execute("INSERT INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)", (book4.title, book4.author, book4.copies, book4.genre))
# cursor.execute("INSERT INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)", (book5.title, book5.author, book5.copies, book5.genre))
# cursor.execute("INSERT INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)", (book6.title, book6.author, book6.copies, book6.genre))
# cursor.execute("INSERT INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)", (book7.title, book7.author, book7.copies, book7.genre))
# cursor.execute("INSERT INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)", (book8.title, book8.author, book8.copies, book8.genre))
# cursor.execute("INSERT INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)", (book9.title, book9.author, book9.copies, book9.genre))
# cursor.execute("INSERT INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)", (book10.title, book10.author, book10.copies, book10.genre))
# cursor.execute("INSERT INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)", (book11.title, book11.author, book11.copies, book11.genre))
# cursor.execute("INSERT INTO books (titles, author, copies, genre) VALUES (?, ?, ?, ?)", (book12.title, book12.author, book12.copies, book12.genre))


# cursor.execute("SELECT * FROM books")
# results=cursor.fetchall()
# print(results)