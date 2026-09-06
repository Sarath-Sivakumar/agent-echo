# Echo

Echo is a multi-channel AI customer communication and voice-agent platform developed by Triarch Private Limited.

Echo is designed to interact with customers naturally across messaging and voice channels while keeping the communication layer independent from the underlying AI intelligence.

The long-term goal is to make Echo a plug-and-play, multi-tenant platform that can be deployed independently for different businesses while preserving strict isolation between tenants.

---

## Current Status

Echo currently supports end-to-end AI conversations through:

- Telegram text messages
- Telegram voice notes
- WhatsApp text messages
- WhatsApp voice notes
- Speech-to-Text
- LLM response generation
- Text-to-Speech
- Temporary audio resource management
- Telegram-compatible OGG/Opus voice responses
- WhatsApp-compatible OGG/Opus voice responses

Real-time telephone calling is currently under development.

---

# Architecture

Echo separates communication channels from conversation intelligence and voice processing.

```text
Customer
   │
   ├── Telegram
   ├── WhatsApp
   └── Phone Call
          │
          ▼
      Channel Layer
          │
          ▼
   Conversation Layer
          │
          ▼
      Echo Runtime
          │
          ▼
      AI Provider
```

Voice communication introduces an additional real-time pipeline:

```text
Telephony Provider
        │
        ▼
     WebSocket
        │
        ▼
   Voice Service
        │
        ▼
   Voice Session
        │
        ▼
   Voice Pipeline
        │
        ├── Audio Processing
        ├── Speech-to-Text
        ├── Conversation Runtime
        ├── Text-to-Speech
        └── Audio Encoding
        │
        ▼
Telephony Provider
        │
        ▼
      Caller
```

---

# Project Structure

```text
app/
│
├── channels/
│   │
│   ├── telegram/
│   │   ├── router.py
│   │   ├── webhook.py
│   │   ├── bot.py
│   │   └── models.py
│   │
│   ├── whatsapp/
│   │   ├── router.py
│   │   ├── webhook.py
│   │   ├── bot.py
│   │   ├── client.py
│   │   └── models.py
│   │
│   └── voice/
│       ├── __init__.py
│       ├── router.py
│       ├── webhook.py
│       ├── websocket.py
│       ├── service.py
│       ├── session.py
│       ├── models.py
│       │
│       └── transport/
│           ├── __init__.py
│           ├── base.py
│           └── twilio.py
│
├── conversation/
│   ├── manager.py
│   └── models.py
│
├── core/
│   │
│   ├── audio/
│   │   ├── converter.py
│   │   ├── codec.py
│   │   └── stream.py
│   │
│   ├── voice/
│   │   └── pipeline.py
│   │
│   ├── storage/
│   │
│   ├── runtime/
│   │
│   └── config/
│
└── main.py
```

Some voice-runtime components are currently being implemented and may still be incomplete.

---

# Telegram

Telegram was the first complete Echo communication channel.

The current Telegram pipeline supports both text and voice.

## Text Flow

```text
Telegram
   │
   ▼
Webhook
   │
   ▼
ConversationManager
   │
   ▼
EchoRuntime
   │
   ▼
LLM
   │
   ▼
Telegram Text Response
```

## Voice Flow

```text
Telegram Voice Note
        │
        ▼
Download OGG Audio
        │
        ▼
Speech-to-Text
        │
        ▼
ConversationManager
        │
        ▼
EchoRuntime
        │
        ▼
LLM
        │
        ▼
Text-to-Speech
        │
        ▼
WAV
        │
        ▼
OGG / Opus Conversion
        │
        ▼
Telegram Voice Note
```

Telegram voice-note communication is currently working end-to-end.

---

# WhatsApp

Echo integrates with the WhatsApp Cloud API.

The webhook supports Meta webhook verification and incoming WhatsApp events.

## Text Flow

```text
WhatsApp Message
      │
      ▼
Meta Webhook
      │
      ▼
ConversationManager
      │
      ▼
EchoRuntime
      │
      ▼
LLM
      │
      ▼
WhatsApp Response
```

Delivery, read and failed status callbacks are handled separately from incoming customer messages.

## Voice Flow

```text
WhatsApp Voice Note
        │
        ▼
Meta Media API
        │
        ▼
Download Audio
        │
        ▼
Speech-to-Text
        │
        ▼
ConversationManager
        │
        ▼
EchoRuntime
        │
        ▼
LLM
        │
        ▼
Text-to-Speech
        │
        ▼
WAV
        │
        ▼
OGG / Opus
        │
        ▼
WhatsApp Media Upload
        │
        ▼
WhatsApp Voice Response
```

WhatsApp voice-note communication is currently working end-to-end.

---

# Speech-to-Text

Echo has a shared voice layer rather than implementing STT separately for every communication channel.

Incoming audio is represented using a common request model and processed through the configured Speech-to-Text provider.

The current implementation uses Groq for speech processing.

This allows:

```text
Telegram ──┐
           │
WhatsApp ──┼──► VoiceManager ──► STT
           │
Phone ─────┘
```

The telephone pipeline will eventually reuse the same underlying voice capabilities where appropriate.

---

# Text-to-Speech

Echo can generate spoken responses using its shared TTS layer.

Current flow:

```text
LLM Response
     │
     ▼
VoiceManager
     │
     ▼
TTS Provider
     │
     ▼
WAV Audio
```

The generated audio is then converted into the format required by the destination channel.

---

# Audio Conversion

Echo contains a shared audio conversion layer.

TTS currently produces WAV audio, while Telegram and WhatsApp voice notes require an appropriate OGG-based format.

The converter performs:

```text
WAV
 │
 ▼
OGG / Opus
```

Opus is preferred for voice communication.

This logic is shared rather than duplicated inside individual channel implementations.

---

# Temporary Resource Management

Downloaded voice messages and synthesized audio files are treated as temporary resources.

Examples include:

```text
temp/
├── voice/
└── tts/
```

The `TemporaryResourceManager` is responsible for creating and cleaning these resources.

This prevents temporary voice files from accumulating permanently on the server.

---

# Conversation Manager

`ConversationManager` provides a common entry point for conversations regardless of channel.

```text
Telegram ──────┐
               │
WhatsApp ──────┼──► ConversationManager
               │
Voice Call ────┘
```

It is responsible for coordinating:

```text
Input
  │
  ├── Text
  │
  └── Audio
        │
        ▼
       STT
        │
        ▼
   Echo Runtime
        │
        ▼
     Response
        │
        ├── Text
        │
        └── TTS
```

This keeps Telegram, WhatsApp and future channels from duplicating conversation logic.

---

# Echo Runtime

Echo Runtime currently provides the conversational AI layer.

The present system prompt identifies Echo as the AI help desk assistant of Triarch Private Limited.

Echo is currently designed to:

- communicate conversationally with customers;
- provide concise responses;
- answer in the language used by the customer;
- work well when responses are spoken aloud;
- avoid unnecessary formatting in spoken responses.

The current model provider can be changed independently from the communication channels.

---

# Real-Time Voice Calls

Telephone voice communication is the next major Echo capability.

The initial transport implementation is being developed against Twilio, but Echo's architecture is intentionally not tied to Twilio.

The intended architecture is:

```text
                    ┌── Twilio
                    │
Phone Network ──────┼── Exotel
                    │
                    ├── Airtel IQ
                    │
                    └── SIP / Future Provider
                            │
                            ▼
                     Voice Transport
                            │
                            ▼
                      Voice Service
                            │
                            ▼
                      Voice Pipeline
```

Twilio is therefore a transport implementation rather than part of Echo's core intelligence.

---

# Voice Webhook

Echo currently exposes a voice webhook:

```text
POST /voice/webhook
```

The endpoint can receive telephony-provider call information such as:

```text
From
To
CallSid
```

The initial Twilio integration returns TwiML to verify the telephony webhook flow.

---

# Media WebSocket

Real-time voice audio will enter Echo through:

```text
WS /voice/stream
```

WebSocket routes are not displayed in FastAPI Swagger/OpenAPI documentation.

The WebSocket layer is intentionally thin:

```text
WebSocket
    │
    ▼
VoiceService
```

It should be responsible only for transport communication rather than STT, TTS or AI reasoning.

---

# Voice Sessions

Each live phone conversation is represented by a `VoiceSession`.

A session can contain metadata such as:

```text
session_id
provider
stream_id
call_id
caller
callee
business_id
customer_id
status
created_at
connected_at
ended_at
```

This provides the foundation for:

- concurrent calls;
- call lifecycle tracking;
- customer identification;
- business isolation;
- analytics;
- future conversation memory.

---

# Multi-Tenant Architecture

Echo is intended to operate as a SaaS product for multiple businesses.

A fundamental requirement is strict tenant isolation.

For example:

```text
Echo Platform
     │
     ├──────────── Business A
     │                  │
     │                  ├── Customers
     │                  ├── Conversations
     │                  ├── Configuration
     │                  └── Memory
     │
     └──────────── Business B
                        │
                        ├── Customers
                        ├── Conversations
                        ├── Configuration
                        └── Memory
```

Business A and Business B must operate independently.

Data, failures, configuration and customer context belonging to one tenant must not leak into or interfere with another tenant.

Future deployment and persistence architecture must preserve this isolation.

---

# Customer-Centric Design

Echo is primarily a customer-facing system.

The platform should eventually be capable of:

- answering customer questions;
- providing business information;
- guiding customers;
- handling customer enquiries;
- collecting required information;
- routing customers appropriately;
- assisting with appointments or meetings;
- maintaining conversation continuity;
- interacting naturally through voice.

Deep autonomous planning is not currently a requirement for Echo V1.

---

# Intelligence Strategy

Echo's communication infrastructure and intelligence are intentionally separate.

The immediate objective is to build an excellent customer communication and voice platform.

Advanced agentic intelligence does not need to be independently recreated inside Echo.

Future Triarch intelligence systems may provide more sophisticated planning, tool use and reasoning capabilities through a separate integration layer.

Therefore:

```text
Echo
│
├── Communication
├── Voice Runtime
├── Customer Sessions
├── Business Context
└── Intelligence Interface
            │
            ▼
      Replaceable Intelligence
```

This allows Echo to evolve without tightly coupling its communication infrastructure to one AI architecture.

---

# Current Development Roadmap

## Completed

- [x] FastAPI backend
- [x] Echo conversational runtime
- [x] LLM integration
- [x] Telegram webhook
- [x] Telegram text conversations
- [x] Telegram voice input
- [x] Telegram voice responses
- [x] WhatsApp webhook verification
- [x] WhatsApp Cloud API integration
- [x] WhatsApp text conversations
- [x] WhatsApp media download
- [x] WhatsApp voice input
- [x] WhatsApp media upload
- [x] WhatsApp voice responses
- [x] Shared STT layer
- [x] Shared TTS layer
- [x] WAV → OGG/Opus conversion
- [x] Temporary resource management
- [x] Voice channel architecture
- [x] Initial telephony webhook
- [x] Voice WebSocket foundation
- [x] Voice session model

## In Progress

- [ ] VoiceService event processing
- [ ] Media Stream parsing
- [ ] Real-time audio ingestion
- [ ] VoicePipeline
- [ ] Telephony audio decoding
- [ ] Telephony audio encoding
- [ ] Real-time STT
- [ ] Real-time TTS
- [ ] End-to-end telephone conversation

## Next

After the voice-call pipeline is complete:

- [ ] Proper conversation/session persistence
- [ ] Customer memory
- [ ] Tenant-aware memory isolation
- [ ] Business configuration
- [ ] Customer identity/context
- [ ] Production telephony provider integration

---

# Development

Start Echo locally:

```bash
uvicorn app.main:app --port 1244 --reload
```

Echo will run at:

```text
http://127.0.0.1:1244
```

FastAPI documentation:

```text
http://127.0.0.1:1244/docs
```

---

# Development Tunnel

During local development, ngrok is used to expose Echo to external webhook providers.

Example:

```bash
ngrok http 1244
```

The resulting HTTPS endpoint can be used for Telegram, WhatsApp and telephony webhooks.

Example:

```text
https://<ngrok-domain>/telegram/webhook

https://<ngrok-domain>/whatsapp/webhook

https://<ngrok-domain>/voice/webhook
```

The voice Media Stream uses the corresponding WebSocket endpoint:

```text
wss://<ngrok-domain>/voice/stream
```

---

# Configuration

Secrets and provider credentials must not be committed to Git.

Typical configuration includes:

```text
Telegram Bot Token
WhatsApp Access Token
WhatsApp Phone Number ID
WhatsApp Verify Token
WhatsApp Graph API
Groq API Key
Telephony Provider Credentials
```

Store secrets through environment configuration and keep `.env` files outside version control.

---

# Design Principles

Echo follows several core architectural rules:

1. Communication channels should remain independent from AI intelligence.
2. Channel-specific logic should remain inside the channel layer.
3. Shared STT, TTS and audio processing should not be duplicated between channels.
4. Telephony providers should be replaceable transports.
5. Voice sessions should remain provider-agnostic wherever possible.
6. Customer conversations should eventually have persistent session and memory boundaries.
7. Businesses must be strictly isolated from one another.
8. Failure in one tenant must not affect another tenant.
9. Echo should remain configurable for businesses with very different operating models.
10. Advanced agentic intelligence can be integrated later without redesigning Echo's communication infrastructure.

---

# Project Vision

Echo is not intended to be merely a Telegram bot, WhatsApp bot, or Twilio application.

Those systems are communication transports.

Echo is intended to become a reusable AI customer communication platform:

```text
             ECHO
               │
     ┌─────────┼──────────┐
     │         │          │
 Telegram   WhatsApp    Voice
                         │
                    Telephony
                         │
             ┌───────────┼───────────┐
             │           │           │
           Twilio      Exotel       SIP
```

Businesses should be able to connect their communication channels, business configuration and customer context while Echo provides the common conversational infrastructure behind them.

The immediate objective is simple:

> A customer contacts a business. Echo answers naturally, understands what the customer needs, and helps them reach the right outcome.
