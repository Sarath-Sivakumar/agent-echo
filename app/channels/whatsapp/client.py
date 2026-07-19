from pathlib import Path

import httpx

from app.core.config.config import (
    WHATSAPP_ACCESS_TOKEN,
    WHATSAPP_GRAPH_API,
    WHATSAPP_PHONE_NUMBER_ID,
)


class WhatsAppClient:

    def __init__(self):

        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            },
            timeout=60,
        )

    async def send_text(
        self,
        to: str,
        text: str,
    ) -> None:

        response = await self.client.post(
            f"{WHATSAPP_GRAPH_API}/{WHATSAPP_PHONE_NUMBER_ID}/messages",
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "body": text,
                },
            },
        )

        self._raise_for_status(response)

    async def send_voice(
        self,
        to: str,
        media_id: str,
    ) -> None:

        response = await self.client.post(
            f"{WHATSAPP_GRAPH_API}/{WHATSAPP_PHONE_NUMBER_ID}/messages",
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "audio",
                "audio": {
                    "id": media_id,
                },
            },
        )

        self._raise_for_status(response)

    async def get_media_url(
        self,
        media_id: str,
    ) -> str:

        response = await self.client.get(
            f"{WHATSAPP_GRAPH_API}/{media_id}",
        )

        self._raise_for_status(response)

        return response.json()["url"]

    async def download_media(
        self,
        media_url: str,
        destination: Path,
    ) -> None:

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        response = await self.client.get(
            media_url,
        )

        self._raise_for_status(response)

        destination.write_bytes(
            response.content,
        )

    async def upload_media(
        self,
        file: Path,
        mime_type: str,
    ) -> str:

        print("\n========== Uploading Media ==========")
        print("File      :", file)
        print("Exists    :", file.exists())
        print("Size      :", file.stat().st_size)
        print("Mime Type :", mime_type)
        print("=====================================\n")

        with open(file, "rb") as audio:

            response = await self.client.post(
                f"{WHATSAPP_GRAPH_API}/{WHATSAPP_PHONE_NUMBER_ID}/media",
                data={
                    "messaging_product": "whatsapp",
                },
                files={
                    "file": (
                        file.name,
                        audio,
                        mime_type,
                    ),
                },
            )

        self._raise_for_status(response)

        media_id = response.json()["id"]

        print("Media uploaded successfully.")
        print("Media ID:", media_id)

        return media_id

    @staticmethod
    def _raise_for_status(
        response: httpx.Response,
    ) -> None:

        if response.is_error:

            print("\n========== WhatsApp Graph API Error ==========")
            print("Status :", response.status_code)
            print("URL    :", response.request.url)

            try:
                print("Body   :", response.json())
            except Exception:
                print("Body   :", response.text)

            print("==============================================\n")

        response.raise_for_status()

    async def close(self):

        await self.client.aclose()