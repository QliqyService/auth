from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field

from app.services.broker import BrokerClient


class RPCFunctions(StrEnum):
    SEND_MESSAGE_TO_SMTP = "send_message_to_smtp"


class RequestMessageSchema(BaseModel):
    recipients: list[EmailStr] = Field(..., title="Recipient Email", description="Recipient email address")
    subject: str = Field(..., title="Subject", description="Message subject")
    html_message: str = Field(..., title="HTML Message", description="HTML message body")


class MailerClient:
    _broker: BrokerClient
    _routing_key: str
    _mailer_prefix: str

    def __init__(
        self,
        broker: BrokerClient,
        mailer_prefix: str,
    ):
        self._broker = broker
        self._mailer_prefix = mailer_prefix

    async def push_message(
        self,
        recipients: list[str],
        subject: str,
        html_message: str,
    ) -> None:
        # 1. Prepare message
        message = RequestMessageSchema(
            recipients=recipients,
            subject=subject,
            html_message=html_message,
        )

        # 2. Prepare queue name
        queue_name = f"{self._mailer_prefix}{RPCFunctions.SEND_MESSAGE_TO_SMTP}"

        # 3. Publish message
        await self._broker.publish(
            queue=queue_name,
            message=message.model_dump(mode="json"),
        )
