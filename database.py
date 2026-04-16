import sqlite3
import bcrypt
#Method to convert dummy account passwords to hash
def passwordtohash(passd):
    hashed_password = bcrypt.hashpw(passd.encode(), bcrypt.gensalt())
    return hashed_password

#connection to database
connection = sqlite3.connect('usernmaes_pass_database')
cursor = connection.cursor()

#create table
command1 = """CREATE TABLE IF NOT EXISTS
login(username TEXT PRIMARY KEY, passwords TEXT)"""
cursor.execute(command1)


#adding to table

cursor.execute("INSERT INTO login (username, passwords) VALUES (?, ?)",("tim101", passwordtohash('ilikecats22')))
cursor.execute("INSERT INTO login (username,passwords) VALUES (?,?)", ('jon3', passwordtohash('test12')))
cursor.execute("INSERT INTO login (username,passwords) VALUES (?,?)",('dr.doom', passwordtohash('boomboom34')))
cursor.execute("INSERT INTO login (username,passwords) VALUES (?,?)", ('catwomen', passwordtohash('iamcool10')))
cursor.execute("INSERT INTO login (username,passwords) VALUES (?,?)", ('heyguys21', passwordtohash('password4')))
cursor.execute("INSERT INTO login (username,passwords) VALUES (?,?)", ('iluvreading', passwordtohash('doggo8')))


#get results

cursor.execute("SELECT * FROM login")
results=cursor.fetchall()
print(results)


