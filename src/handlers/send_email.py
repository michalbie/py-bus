import os

order_id = os.environ.get("ORDER_ID", "brak")
customer = os.environ.get("CUSTOMER", "brak")

print(f"Sending email to {customer} about order {order_id}")
