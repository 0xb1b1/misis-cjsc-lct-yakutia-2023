#!/usr/bin/env python3

"""Opens aiogram listener, ..."""

# region Regular dependencies
import os
import logging
import asyncio
from datetime import datetime, UTC
from typing import Union
from aiogram import Bot, Dispatcher
from aiogram import executor, types
from aiogram.types.message import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentType
# endregion

# region Local dependencies
from cjsc_telegram_bot import config

from cjsc_telegram_bot.utils.query_ml import query_ml, \
    get_user_prefs

from cjsc_telegram_bot.http.schemas.message import \
    MessageSchema, MessagePlatform, MessageRequestType
# endregion

# region Bot initialization
# Initialize bot and dispatcher
bot = Bot(token=config.TELEGRAM_API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
# endregion


async def answer(message: types.Message) -> None:
    response_msg = query_ml(
        MessageSchema(
            platform=MessagePlatform.TG,
            user_id=str(message.from_user.id),
            timestamp=datetime.now(UTC),
            request_text=message.text,
            response_text=None,
        )
    )

    await message.answer(response_msg.response_text)


def run():
    dp.register_message_handler(answer, content_types=ContentType.TEXT)

    executor.start_polling(dp, skip_updates=True)
