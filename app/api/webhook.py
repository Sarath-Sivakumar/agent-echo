from fastapi import APIRouter, Request, Query
from fastapi.responses import PlainTextResponse

router = APIRouter()

VERIFY_TOKEN = "project-echo-secret"


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge)

    return PlainTextResponse(content="Verification failed", status_code=403)


@router.post("/webhook")
async def webhook(request: Request):
    body = await request.json()

    print(body)

    return {"status": "received"}