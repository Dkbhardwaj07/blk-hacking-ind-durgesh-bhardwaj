import math
import time
import psutil
import threading
from fastapi import FastAPI
from datetime import datetime
from typing import List
from app.utils import parse_transaction, validate_transactions
from app.models import ValidatorRequest, ValidatorResponse, TransactionOutput
from app.models import ValidatorRequest

app = FastAPI()

@app.get("/")
def home():
    return {"message": "BlackRock Hackathon API running"}

@app.post("/blackrock/challenge/v1/transactions/parse")
def parse(transactions: List[dict]):

    result = []

    for tx in transactions:

        amount = float(tx["amount"])
        ceiling = float(math.ceil(amount / 100) * 100)
        remanent = float(ceiling - amount)

        result.append({
            "date": tx["date"],
            "amount": amount,
            "ceiling": ceiling,
            "remanent": remanent
        })

    return result



@app.post(
    "/blackrock/challenge/v1/transactions/validator",
    response_model=ValidatorResponse,response_model_exclude_none=True
)
def validate(request: ValidatorRequest):

    valid = []
    invalid = []
    seen = set()

    for tx in request.transactions:

        key = (tx.date, tx.amount)

        base_data = {
            "date": tx.date,
            "amount": float(tx.amount),
            "ceiling": float(tx.ceiling),
            "remanent": float(tx.remanent)
        }

        if tx.amount < 0:

            invalid.append(
                TransactionOutput(
                    **base_data,
                    message="Negative amounts are not allowed"
                )
            )

        elif key in seen:

            invalid.append(
                TransactionOutput(
                    **base_data,
                    message="Duplicate transaction"
                )
            )

        elif tx.amount > request.wage:

            invalid.append(
                TransactionOutput(
                    **base_data,
                    message="Amount exceeds wage limit"
                )
            )

        else:

            valid.append(
                TransactionOutput(**base_data)
            )

            seen.add(key)

    return ValidatorResponse(
        valid=valid,
        invalid=invalid
    )

@app.post(
    "/blackrock/challenge/v1/transactions/filter",
    response_model=dict,
    response_model_exclude_none=True
)
def filter_transactions(data: dict):

    k_periods = data.get("k", [])
    p_periods = data.get("p", [])
    transactions = data.get("transactions", [])

    valid = []
    invalid = []
    seen = set()

    for tx in transactions:

        try:

            # parse transaction fields
            tx_date = datetime.strptime(tx["date"], "%Y-%m-%d %H:%M:%S")

            amount = float(tx["amount"])
            ceiling = float(tx.get("ceiling", ((amount + 99) // 100) * 100))
            remanent = float(tx.get("remanent", ceiling - amount))

            key = (tx["date"], amount)

            if key in seen:
                invalid.append({
                    "date": tx["date"],
                    "amount": amount,
                    "ceiling": ceiling,
                    "remanent": remanent,
                    "message": "Duplicate transaction"
                })
                continue


            if amount < 0:
                invalid.append({
                    "date": tx["date"],
                    "amount": amount,
                    "ceiling": ceiling,
                    "remanent": remanent,
                    "message": "Negative amounts are not allowed"
                })
                continue

            in_k = False

            for period in k_periods:

                start = datetime.strptime(period["start"], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(period["end"], "%Y-%m-%d %H:%M:%S")

                if start <= tx_date <= end:
                    in_k = True
                    break

            if not in_k:

                invalid.append(
                    TransactionOutput(
                        date=tx["date"],
                        amount=float(amount),
                        ceiling=float(ceiling),
                        remanent=float(remanent),
                        message="Transaction outside allowed period"
                    )
                )

            else:

                valid.append(
                    TransactionOutput(
                        date=tx["date"],
                        amount=float(amount),
                        ceiling=float(ceiling),
                        remanent=float(remanent),
                        inKPeriod=True
                    )
                )

                seen.add(key)

        except Exception as e:

            invalid.append({
                **tx,
                "message": f"Invalid transaction format"
            })

    return {
        "valid": valid,
        "invalid": invalid
    }


start_time = time.time()

@app.get("/blackrock/challenge/v1/performance")
def performance():

    execution_time = time.time() - start_time

    process = psutil.Process()
    memory = process.memory_info().rss / (1024 * 1024)

    threads = threading.active_count()

    return {
        "time": f"{execution_time:.3f}s",
        "memory": f"{memory:.2f} MB",
        "threads": threads
    }
@app.post("/blackrock/challenge/v1/returns/nps")
def returns_nps(data: dict):

    transactions = data.get("transactions", [])
    periods = data.get("k", [])

    total_amount = 0.0
    total_ceiling = 0.0

    for tx in transactions:

        amount = float(tx["amount"])
        ceiling = float(math.ceil(amount / 100) * 100)

        total_amount += amount
        total_ceiling += ceiling

    savings = total_ceiling - total_amount

    savings_by_dates = []

    for period in periods:

        profit = round(savings * 0.0711, 2)

        savings_by_dates.append({
            "start": period["start"],
            "end": period["end"],
            "amount": float(savings),
            "profit": float(profit),
            "taxBenefit": 0.0
        })

    return {
        "totalTransactionAmount": float(total_amount),
        "totalCeiling": float(total_ceiling),
        "savingsByDates": savings_by_dates
    }


@app.post("/blackrock/challenge/v1/returns/index")
def returns_index(data: dict):

    age = int(data["age"])
    inflation = float(data["inflation"])

    transactions = data.get("transactions", [])
    periods = data.get("k", [])

    rate = 0.1449
    years = 60 - age

    total_amount = 0.0
    total_ceiling = 0.0

    for tx in transactions:

        amount = float(tx["amount"])
        ceiling = float(math.ceil(amount / 100) * 100)

        total_amount += amount
        total_ceiling += ceiling

    savings = total_ceiling - total_amount

    savings_by_dates = []

    for period in periods:

        future_value = savings * ((1 + rate) ** years)
        inflation_adjusted = future_value / ((1 + inflation/100) ** years)

        profit = inflation_adjusted - savings

        savings_by_dates.append({
            "start": period["start"],
            "end": period["end"],
            "amount": float(savings),
            "profit": round(float(profit), 2),
            "taxBenefit": 0.0
        })

    return {
        "totalTransactionAmount": float(total_amount),
        "totalCeiling": float(total_ceiling),
        "savingsByDates": savings_by_dates
    }