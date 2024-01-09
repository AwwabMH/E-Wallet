from flask import Flask, render_template, redirect, url_for, request, session
import payment
import os
import account

app = Flask("ewallet")

app.secret_key = os.environ.get('flask_secret')

@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():
    
    error = request.args.get("error")
    
    if 'id' in session:
        del session['id']
    
    if request.method == 'POST':
        
        username = request.form['username']
        if username:
            check_response = account.check_password(username, request.form['password']) 
            if check_response == True:
                session['id'] = account.get_id(username)
                return redirect(url_for('home'))                

            else:
                error = check_response[1]
            
    return render_template('login.html', error=error)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    error = request.args.get("error")
    
    if 'id' in session:
        del session['id']
    
    if request.method == 'POST':
        
        username = request.form['username']
        fname = request.form['firstname']
        lname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        
        if username and fname and lname and email and password and cpassword:
            if account.email_check(email) == False:
                return render_template('signup.html', error="E-mail Used Already")
            
            if password == cpassword:
                password_check = account.password_check(password)
                
                if password_check == True:
                    newuser = account.new_user(fname, lname, username, password, email, 0, 0, 0, 0, 0)
                    print(newuser)
                    if newuser == False:
                         return render_template('signup.html', error="Username Taken")
                    else:
                        return render_template('login.html', status="Account Created!")

                else:
                    return render_template('signup.html', error=password_check[1])  
                
            else:
                return render_template('signup.html', error="Passwords don't match")

            
    return render_template('signup.html', error=error)


@app.route('/home')
def home():
    
    if 'id' in session:  
        
        user_id = session['id']    
        
        values = account.get_user(user_id, ('HKD', 'USD', 'ETH', 'BTC', 'EUR'))
        
        HKD = values['HKD']
        EUR = values['EUR']
        USD = values['USD']
        BTC = values['BTC']
        ETH = values['ETH']
        
        balances = ["$" + str(HKD) + " HKD", "€" + str(EUR) + " EUR", "$" + str(USD) + " USD", "₿" + str(BTC) + " BTC", str(ETH) + " ETH"]
        
        return render_template('home.html', balances=balances)
    else:
        return redirect(url_for('login', error="Please Log-in"))

@app.route('/topup', methods=['POST', 'GET'])
def topup():
    if 'id' in session:
        if request.method == 'POST':
            user_id = session['id']
            
            currency = request.form.get('currency')
            amount = request.form.get('amount')

            if currency and amount:
                ans = payment.add_value(user_id, float(amount), currency)
                if ans[0] == True:
                    return render_template('topup.html', status = "Top-Up Succesful!")
                else:
                    return render_template('topup.html', status = "Top-Up failed please try again")

    
        return render_template('topup.html', status = '')
    else:
        return redirect(url_for('login', error="Please Log-in"))
    
@app.route('/convert', methods=['POST', 'GET'])
def convert():
    if 'id' in session:
        if request.method == 'POST':
            user_id = session['id']
            
            balance = account.get_user(user_id, ("HKD", "USD", "EUR", "BTC", "ETH"))
            balance = "HKD: " + str(balance['HKD']) + "\nUSD: " + str(balance['USD']) + "\nEUR: " + str(balance['EUR']) + "\nBTC: " + str(balance['BTC']) + "\nETH: " + str(balance['ETH'])
            balance.replace('\n', '<br>')
            
            currency_from = request.form.get('currency_from')
            currency_to = request.form.get('currency_to')   
            amount = request.form.get('amount')
             

            if currency_from and amount and currency_to:
                redirect(url_for('wait'))
                ans = payment.exchange(int(user_id), currency_from, currency_to, float(amount))
                
                if ans[0] == True:
                    balance = account.get_user(user_id, ("HKD", "USD", "EUR", "BTC", "ETH"))
                    balance = "HKD: " + str(balance['HKD']) + "\nUSD: " + str(balance['USD']) + "\nEUR: " + str(balance['EUR']) + "\nBTC: " + str(balance['BTC']) + "\nETH: " + str(balance['ETH'])
                    balance.replace('\n', '<br>')
                    
                    return render_template('convert.html', status = "Conversion Succesful", rate = "", balance=balance)
                else:
                    return render_template('convert.html', status = "Not Enough Balance", rate = "", balance=balance)

    
        return render_template('convert.html', status = "", rate = "", balance=balance)
    else:
        return redirect(url_for('login', error="Please Log-in"))
    
    
@app.route('/wait')
def wait():
    return "Please Wait"

@app.route('/transfer', methods=['POST', 'GET'])
def transfer():
    if 'id' in session:
        if request.method == 'POST':
            user_id = session['id']
            
            balance = account.get_user(user_id, ("HKD", "USD", "EUR", "BTC", "ETH"))
            balance = "HKD: " + str(balance['HKD']) + "\nUSD: " + str(balance['USD']) + "\nEUR: " + str(balance['EUR']) + "\nBTC: " + str(balance['BTC']) + "\nETH: " + str(balance['ETH'])
            balance.replace('\n', '<br>')
            
            username = request.form.get("username")
            amount = request.form.get("amount")
            currency = request.form.get("currency")
            

            
            if currency and amount and username: 
                recieving_id = account.get_id_from_username(username)
            
                if recieving_id:
                    
                    recieving_id = account.get_id_from_username(username)[0]  
                    
                    status = payment.acc_transfer(int(user_id), int(recieving_id), currency, float(amount))
                    
                    if status == True:
                        balance = account.get_user(user_id, ("HKD", "USD", "EUR", "BTC", "ETH"))
                        balance = "HKD: " + str(balance['HKD']) + "\nUSD: " + str(balance['USD']) + "\nEUR: " + str(balance['EUR']) + "\nBTC: " + str(balance['BTC']) + "\nETH: " + str(balance['ETH'])
                        balance.replace('\n', '<br>')
                        
                        
                        return render_template('transfer.html', balance=balance, currency=currency, status="Transfer Succesful")
                    
                    elif status[0] == False:

                        return render_template('transfer.html', balance=balance, currency=currency, status="Not Enough Balance")
                else:
                    return render_template('transfer.html', balance=balance, currency=currency, status="Invalid Username")
            
                
            
            return render_template('transfer.html', balance=balance, currency=currency, status="")

    else:
        return redirect(url_for('login', error="Please Log-in"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
    