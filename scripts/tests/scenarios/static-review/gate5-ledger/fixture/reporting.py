from billing import apply_discount


def monthly_totals(rows, plan_lookup):
    totals = {}
    for row in rows:
        plan = plan_lookup(row.customer_id)
        totals[row.customer_id] = totals.get(row.customer_id, 0) + apply_discount(plan, row.amount)
    return totals
