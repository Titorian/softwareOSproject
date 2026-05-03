import sqlite3
import bcrypt


#account class
class Accounts:
    def __init__(self,username, password):
        self.username= username
        self.password = password

#Method to convert dummy account passwords to hash
def passwordtohash(passd):
    hashed_password = bcrypt.hashpw(passd.encode(), bcrypt.gensalt())
    return hashed_password

#connection to database
def get_connection2():
        return sqlite3.connect('usernmaes_pass_database')

# #adding to table

# cursor.execute("INSERT INTO login (username, passwords) VALUES (?, ?)",("tim101", passwordtohash('ilikecats22')))
# cursor.execute("INSERT INTO login (username,passwords) VALUES (?,?)", ('jon3', passwordtohash('test12')))
# cursor.execute("INSERT INTO login (username,passwords) VALUES (?,?)",('dr.doom', passwordtohash('boomboom34')))
# cursor.execute("INSERT INTO login (username,passwords) VALUES (?,?)", ('catwomen', passwordtohash('iamcool10')))
# cursor.execute("INSERT INTO login (username,passwords) VALUES (?,?)", ('heyguys21', passwordtohash('password4')))
# cursor.execute("INSERT INTO login (username,passwords) VALUES (?,?)", ('iluvreading', passwordtohash('doggo8')))


#get results

# cursor.execute("SELECT * FROM login")
# results=cursor.fetchall()
# print(results)


