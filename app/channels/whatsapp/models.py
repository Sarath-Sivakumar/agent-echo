from pydantic import BaseModel, ConfigDict, Field


class WhatsAppBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


class WhatsAppProfile(WhatsAppBaseModel):
    name: str


class WhatsAppContact(WhatsAppBaseModel):
    wa_id: str
    profile: WhatsAppProfile | None = None


class WhatsAppText(WhatsAppBaseModel):
    body: str


class WhatsAppAudio(WhatsAppBaseModel):
    id: str
    mime_type: str | None = None
    sha256: str | None = None
    voice: bool | None = None


class WhatsAppImage(WhatsAppBaseModel):
    id: str
    mime_type: str | None = None
    sha256: str | None = None


class WhatsAppDocument(WhatsAppBaseModel):
    id: str
    filename: str | None = None
    mime_type: str | None = None
    sha256: str | None = None


class WhatsAppMessage(WhatsAppBaseModel):
    id: str
    from_: str = Field(alias="from")

    timestamp: str
    type: str

    text: WhatsAppText | None = None
    audio: WhatsAppAudio | None = None
    image: WhatsAppImage | None = None
    document: WhatsAppDocument | None = None


class WhatsAppMetadata(WhatsAppBaseModel):
    display_phone_number: str
    phone_number_id: str


class WhatsAppErrorData(WhatsAppBaseModel):
    details: str | None = None


class WhatsAppStatusError(WhatsAppBaseModel):
    code: int
    title: str
    message: str
    error_data: WhatsAppErrorData | None = None


class WhatsAppStatus(WhatsAppBaseModel):
    id: str
    status: str
    timestamp: str
    recipient_id: str

    errors: list[WhatsAppStatusError] = []


class WhatsAppValue(WhatsAppBaseModel):
    messaging_product: str

    metadata: WhatsAppMetadata

    contacts: list[WhatsAppContact] = []

    messages: list[WhatsAppMessage] = []

    statuses: list[WhatsAppStatus] = []


class WhatsAppChange(WhatsAppBaseModel):
    field: str
    value: WhatsAppValue


class WhatsAppEntry(WhatsAppBaseModel):
    id: str
    changes: list[WhatsAppChange]


class WhatsAppWebhook(WhatsAppBaseModel):
    object: str
    entry: list[WhatsAppEntry]