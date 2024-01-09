import sqlite3
import hashlib
import random

connectdb = sqlite3.connect('users.db')

cursor = connectdb.cursor()

currencies_supported = ("BTC", "ETH", "USD", "HKD", "EUR")
forex_supported = {"USD", "HKD", "EUR"}

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, fname TEXT, lname TEXT, ETH INT, BTC INT, USD INT, HKD INT, EUR INT)")

cursor.execute("CREATE TABLE IF NOT EXISTS usernames (id INTEGER, username TEXT, password TEXT, number INT, email STR, FOREIGN KEY (id) REFERENCES users (id))")

def hash_password(password:str):
    salt = password[0:int(len(password)/2)]
    number = random.randint(0, 100)
    
    password = salt + password + salt*number
    
    hashpass = hashlib.sha256(password.encode())
    
    hashpass = hashpass.hexdigest()
    
    return (hashpass, number)


def password_hash(password:str, number:int):
    salt = password[0:int(len(password)/2)]
    
    password = salt + password + salt*number
    
    hashpass = hashlib.sha256(password.encode())
    
    hashpass = hashpass.hexdigest()
    
    return hashpass


def check_username(username:str):
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    
    cursor.execute(f"SELECT * FROM usernames WHERE username = '{username}'")
    
    if cursor.fetchall():
        return False
    else:
        return True
    
    
def make_admin():
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()

    
    cursor.execute("INSERT INTO users (fname, lname, ETH, BTC, USD, HKD, EUR) VALUES (?, ?, ?, ?, ?, ?, ?)", ('admin', 'admin', 999, 999.9, 999.99, 999.999, 999.9999)) 
    user_id = cursor.lastrowid 
    
    cursor.execute("INSERT INTO usernames (id, username, password, number, email) VALUES (?, ?, ?, ?, ?)", (user_id, "admin", "admin", 3, "admin"))
    
    connectdb.commit()
    
def password_check(password:str):
    if password.__len__() >= 8:
        return True
    else:
        return (False, "Password must be atleast 8 characters")
    
def email_check(email:str):
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    
    cursor.execute(f"SELECT * FROM usernames WHERE email = '{email}'")
    
    if cursor.fetchall():
        return False
    else:
        return True


def del_users(ids:tuple):
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    
    for id in ids:
        cursor.execute(f"DELETE FROM users WHERE id = {id}")
    
    connectdb.commit()

def new_user(fname: str, lname: str, username:str, password:str, email:str, ETH: float, BTC: float, USD: float, HKD: float, EUR: float):
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    
    if check_username(username) == True:
        cursor.execute("INSERT INTO users (fname, lname, ETH, BTC, USD, HKD, EUR) VALUES (?, ?, ?, ?, ?, ?, ?)", (fname, lname, ETH, BTC, USD, HKD, EUR)) 
        user_id = cursor.lastrowid 

        password_hash = hash_password(password)
        
        password = password_hash[0]
        number = password_hash[1]

        cursor.execute("INSERT INTO usernames (id, username, password, number, email) VALUES (?, ?, ?, ?, ?)", (user_id, username, password, number, email))

        connectdb.commit()
    
        return True
    
    else:
        return False


def update_user_multi(id: int, ETH_change=0, BTC_change=0, USD_change=0, HKD_change=0, EUR_change=0):
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    
    cursor.execute(f"SELECT ETH FROM users WHERE id = {id}")
    ETH_total = cursor.fetchone()[0] + ETH_change
    
    cursor.execute(f"SELECT BTC FROM users WHERE id = {id}")
    BTC_total = cursor.fetchone()[0] + BTC_change
    
    cursor.execute(f"SELECT USD FROM users WHERE id = {id}")
    USD_total = cursor.fetchone()[0] + USD_change
    
    cursor.execute(f"SELECT HKD FROM users WHERE id = {id}")
    HKD_total = cursor.fetchone()[0] + HKD_change
    
    cursor.execute(f"SELECT EUR FROM users WHERE id = {id}")
    EUR_total = cursor.fetchone()[0] + EUR_change
    
    cursor.execute("UPDATE users SET ETH = ?, BTC = ?, USD = ?, HKD = ?, EUR = ? WHERE id = ?", (ETH_total, BTC_total, USD_total, HKD_total, EUR_total, id))
    connectdb.commit()
    
    
def update_user_single(id: int, currency: str, amount: float):
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    
    if currency.upper() in currencies_supported:
        cursor.execute(f"SELECT {currency.upper()} FROM users WHERE id = {id}")
        currency_total = cursor.fetchone()[0] + amount
        
        cursor.execute(f"UPDATE users SET {currency.upper()} = {currency_total} WHERE id = {id}")
        connectdb.commit()
        
    else:
        return (False, 200)
        

def get_user(id:int, currencies = None):
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    
    currency_values = {}
    
    if currencies == None:
        cursor.execute(f"SELECT * FROM users WHERE id = {id}")
        return cursor.fetchone()
        
    for currency in currencies:
        if currency.upper() not in currencies_supported:
            None
        else:
            cursor.execute(f"SELECT {currency} FROM users WHERE id = {id}")
            value = cursor.fetchone()
            currency_values[currency.upper()] = value[0]
            
    return currency_values

def get_id(username:str):
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    
    if check_username(username) == True:
        return (False, "Invalid Username")
    
    cursor.execute("SELECT id FROM usernames WHERE username = ?", (username,))
    return cursor.fetchone()[0]

def check_password(username:str, password:str):
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    
    if check_username(username) == True:
        return (False, "Invalid Username")
        
    cursor.execute("SELECT password, number FROM usernames WHERE username = ?", (username,))
    passvar = cursor.fetchone()
    
    if passvar[0] == password_hash(password, passvar[1]):
        return True
    else:
        return (False, "Invalid Password")


def get_all():
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    return rows

def get_id_from_username(username:str):
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    
    cursor.execute(f"SELECT id FROM usernames WHERE username = '{username}'")
    return cursor.fetchone()

def get_all_usernames():
    connectdb = sqlite3.connect('users.db')

    cursor = connectdb.cursor()
    cursor.execute("SELECT * FROM usernames")
    rows = cursor.fetchall()
    return rows
