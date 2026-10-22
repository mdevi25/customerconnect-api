from fastapi import FastAPI

app = FastAPI(
    title="CustomerConnect API",
    description="Customer-facing service request API",
    version="0.1.0"
)

# Synthetic service catalog - no real customer data
SERVICES = [
    {
        "service_id": "TECH",
        "name": "Technical Support",
        "description": "Get help with a technical issue."
    },
    {
        "service_id": "BILLING",
        "name": "Billing Assistance",
        "description": "Ask a question about a bill."
    },
    {
        "service_id": "ACCOUNT",
        "name": "Account Services",
        "description": "Request assistance with your account."
    }
]


@app.get("/services")
def get_services():
    return SERVICES
