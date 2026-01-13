from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from execution.run_audit import execute_audit
import os
import json

app = FastAPI(title="PPM Audit API", version="1.0")

# --- Debug logging for Validation Errors ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    print(f"\n❌ WEBHOOK REJECTED (422 Validation Error)")
    print(f"URL: {request.url}")
    print(f"Body: {body.decode()}")
    print(f"Error Details: {exc.errors()}\n")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body.decode()},
    )

class GHLPayload(BaseModel):
    contact_name: str = Field(..., description="Full name of the contact")
    contact_email: str = Field(..., description="Email address")
    business_name: str = Field(..., description="Business Name")
    website_url: str = Field(..., description="Website URL to audit")
    
    # Optional GHL specific fields
    contact_id: Optional[str] = None
    workflow_id: Optional[str] = None
    contact_phone: Optional[str] = None
    business_category: Optional[str] = None
    audit_source: Optional[str] = None
    audit_status: Optional[str] = None

def run_audit_task(payload: GHLPayload):
    try:
        print(f"\n✅ WEBHOOK ORCHESTRATOR: Starting audit for {payload.business_name}...")
        print(f"Payload Received: {payload.dict()}")
        
        report_path = execute_audit(
            business_name=payload.business_name,
            url=payload.website_url,
            email=payload.contact_email,
            contact_name=payload.contact_name
        )
        print(f"✅ AUDIT COMPLETE. Report at {report_path}\n")
        
    except Exception as e:
        print(f"❌ WEBHOOK ERROR: Audit failed for {payload.business_name}: {e}")

@app.post("/webhook")
async def receive_webhook(payload: GHLPayload, background_tasks: BackgroundTasks):
    """
    Receives Webhook from HighLevel.
    Returns 200 immediately and processes audit in background.
    """
    print(f"\n📨 WEBHOOK RECEIVED: Queuing audit for {payload.business_name}")
    background_tasks.add_task(run_audit_task, payload)
    return {"status": "queued", "message": f"Audit started for {payload.business_name}"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
