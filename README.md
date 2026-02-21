# BlackRock Hackathon 2026 – Financial Well-Being API

Developed by: Durgesh Bhardwaj

## Overview

This project implements a FastAPI backend to process investment transactions and calculate savings, validation, and returns as required by the BlackRock Hackathon challenge.

## Features

APIs implemented:

1. Parse Transactions
2. Validate Transactions
3. Filter Transactions
4. Calculate NPS Returns
5. Calculate Index Returns
6. Performance Metrics

## Tech Stack

- Python 3.10
- FastAPI
- Docker
- Uvicorn
- psutil

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 5477
