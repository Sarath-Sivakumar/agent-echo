from app.core.intelligence.context.models import Context
from app.core.intelligence.prompt.models import (
    Prompt,
    PromptMessage,
)
from app.prompts.system_prompt import SYSTEM_PROMPT

class PromptBuilder:

    async def build(
        self,
        context: Context,
    ) -> Prompt:

        messages: list[PromptMessage] = [
            PromptMessage(
                role="system",
                content=SYSTEM_PROMPT,
            )
        ]

        messages.extend(
            PromptMessage(
                role=history_message.role,
                content=history_message.content,
            )
            for history_message in context.history.messages
        )

        if (
            context.message
            and (
                not context.history.messages
                or context.history.messages[-1].content != context.message
            )
        ):
            messages.append(
                PromptMessage(
                    role="user",
                    content=context.message,
                )
            )

        return Prompt(messages=messages)