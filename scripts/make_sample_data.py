"""Generate a small synthetic company dataset. Every value is fake.

Run from the repo root:  python scripts/make_sample_data.py
Emails use example.com, phones use the reserved 555-01xx range, and fake SSNs start
with 9, which is never a valid real SSN prefix.
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "sample"
random.seed(2026)

FIRST = ["Ada", "Ben", "Chloe", "Dev", "Esi", "Femi", "Grace", "Hugo", "Ife", "Jon", "Kara", "Leo"]
LAST = ["Adams", "Brooks", "Chen", "Diaz", "Eze", "Foster", "Gray", "Hill", "Ito", "Jones", "Khan", "Lopez"]
REGIONS = ["Southeast", "Northeast", "Midwest", "West"]
CATEGORIES = ["Hardware", "Software", "Services"]
STATUSES = ["shipped", "pending", "returned", "cancelled"]
DEPARTMENTS = ["Sales", "Finance", "Engineering", "Operations"]


def rand_date(start: date, days: int) -> str:
    return (start + timedelta(days=random.randint(0, days))).isoformat()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    products = pd.DataFrame(
        {
            "product_id": [f"P{i:03d}" for i in range(1, 21)],
            "product_name": [f"Product {i}" for i in range(1, 21)],
            "category": [random.choice(CATEGORIES) for _ in range(20)],
            "list_price": [round(random.uniform(9, 400), 2) for _ in range(20)],
        }
    )

    customers = []
    for i in range(1, 201):
        first, last = random.choice(FIRST), random.choice(LAST)
        customers.append(
            {
                "customer_id": f"C{i:04d}",
                "first_name": first,
                "last_name": last,
                "email": f"{first.lower()}.{last.lower()}{i}@example.com",
                "phone": f"404-555-01{random.randint(0, 99):02d}",
                "region": random.choice(REGIONS),
                "signup_date": rand_date(date(2023, 1, 1), 900),
            }
        )
    customers = pd.DataFrame(customers)

    orders = []
    for i in range(1, 801):
        orders.append(
            {
                "order_id": f"O{i:05d}",
                "customer_id": f"C{random.randint(1, 200):04d}",
                "product_id": f"P{random.randint(1, 20):03d}",
                "order_date": rand_date(date(2024, 1, 1), 600),
                "quantity": random.randint(1, 8),
                "status": random.choices(STATUSES, weights=[70, 15, 8, 7])[0],
            }
        )
    orders = pd.DataFrame(orders)

    employees = []
    for i in range(1, 41):
        employees.append(
            {
                "employee_id": f"E{i:03d}",
                "full_name": f"{random.choice(FIRST)} {random.choice(LAST)}",
                "department": random.choice(DEPARTMENTS),
                "hire_date": rand_date(date(2018, 1, 1), 2000),
                "salary": random.randint(52, 190) * 1000,
                "ssn": f"9{random.randint(10, 99)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}",
                "manager_id": f"E{random.randint(1, 5):03d}",
            }
        )
    employees = pd.DataFrame(employees)

    for name, df in {
        "products": products,
        "customers": customers,
        "orders": orders,
        "employees": employees,
    }.items():
        df.to_csv(OUT / f"{name}.csv", index=False)
        print(f"wrote {name}.csv ({len(df)} rows)")


if __name__ == "__main__":
    main()
