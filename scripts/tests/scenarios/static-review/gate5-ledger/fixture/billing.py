import os
import requests
from db import POOL


def charge_customer(customer_id, amount_cents):
    conn = POOL.getconn()
    row = conn.execute("SELECT plan, balance FROM customers WHERE id=?", (customer_id,)).fetchone()
    plan, balance = row
    if plan == "enterprise":
        discount = 0.15
    elif plan == "pro":
        discount = 0.05
    else:
        discount = 0.0
    final = int(amount_cents * (1 - discount))
    if balance < final:
        raise ValueError("insufficient balance")
    conn.execute("UPDATE customers SET balance=? WHERE id=?", (balance - final, customer_id))
    requests.post(
        "https://hooks.internal/billing",
        json={"customer": customer_id, "charged": final},
        headers={"Authorization": os.environ["BILLING_TOKEN"]},
    )
    POOL.putconn(conn)
    return final


def apply_discount(plan, amount_cents):
    rates = {"enterprise": 0.15, "pro": 0.05}
    return int(amount_cents * (1 - rates.get(plan, 0.0)))


class InvoiceFormatter:
    def __init__(self, locale):
        self._locale = locale

    def render(self, invoice):
        return f"[{self._locale}] {invoice.number}: {invoice.total / 100:.2f}"
