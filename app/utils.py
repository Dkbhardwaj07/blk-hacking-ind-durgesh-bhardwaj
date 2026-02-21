import math
from datetime import datetime

def calculate_ceiling(amount: float):
    return float(math.ceil(amount / 100) * 100)

def calculate_remanent(amount: float):
    ceiling = calculate_ceiling(amount)
    return float(ceiling - amount)

def parse_transaction(tx):
    ceiling = calculate_ceiling(tx["amount"])
    remanent = calculate_remanent(tx["amount"])
    
    return {
        "date": tx["date"],
        "amount": tx["amount"],
        "ceiling": ceiling,
        "remanent": remanent
    }

def validate_transactions(transactions):
    valid = []
    invalid = []
    
    seen = set()
    
    for tx in transactions:
        
        if tx["amount"] < 0:
            invalid.append({
                **tx,
                "message": "Negative amounts are not allowed"
            })
            continue
        
        key = (tx["date"], tx["amount"])
        
        if key in seen:
            invalid.append({
                **tx,
                "message": "Duplicate transaction"
            })
            continue
        
        seen.add(key)
        valid.append(tx)
    
    return valid, invalid