import asyncio

from app.conversation.manager import ConversationManager
from app.conversation.models import (
    ContentType,
    ConversationContent,
    ConversationInput,
)


async def main():

    manager = ConversationManager()

    response = await manager.handle_message(
        ConversationInput(
            conversation_id="1",
            channel="test",
            user_id="user",
            chat_id="chat",
            content=ConversationContent(
                type=ContentType.TEXT,
                text="Hello Echo",
            ),
        )
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())