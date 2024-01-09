import stripe
import os
import account
import webbrowser
import forex

stripe.api_key = os.environ.get('stripe_api_sk_test')

def add_value(id: int, amountreq: float, currency = "HKD"):
    
    if currency == "HKD" or "USD" or "EUR":
            
        payment = stripe.Charge.create(
            amount=int((amountreq*100)),
            currency=currency,
            source="tok_visa",
            description='Add Value to Your Wallet'   
        )
        
        if payment.paid == True:
            account.update_user_single(id, currency, amountreq)
            webbrowser.open(payment.receipt_url)
            return (True, payment.receipt_url)
        else:
            return (False, 100)
    else:
        return (False, 200)
    
    
def acc_transfer(sending_id:int, recieving_id:int, currency:str, amount:float):
    
    currency = currency.upper()
    
    if currency in account.currencies_supported:
        sender_bal = account.get_user(sending_id, (currency,))[currency]
        if sender_bal >= amount:
            account.update_user_single(sending_id, currency, (-amount)) 
            account.update_user_single(recieving_id, currency, amount)
            return True
            
        else:
            return (False, 101)
    else:
        return(False, 200)
    
def acc_transfer_exchange(sending_id:int, recieving_id:int, from_currency:str, to_currency:str, amount:float):
    amount_exchanged = exchange(sending_id, from_currency, to_currency, amount)
    
    if amount_exchanged[0] == True:
        acc_transfer(sending_id, recieving_id, to_currency, amount_exchanged[1])
        
def exchange(id:int, from_currency:str, to_currency:str, amount:float):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if from_currency and to_currency in account.currencies_supported:
        bal = account.get_user(id, (from_currency,))[from_currency]
        if bal >= amount:
            account.update_user_single(id, from_currency, (-amount))
            rate = forex.get_rate(from_currency)[to_currency.upper()]
            amount_to = rate * amount
            account.update_user_single(id, to_currency, amount_to)
            
            return(True, amount_to)
            
        else:
            return(False, 101)
        
    else:
        return(False, 200)
    
    
    
