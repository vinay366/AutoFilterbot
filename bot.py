import os, math, logging, datetime, pytz, logging.config

from aiohttp import web
from pyrogram import Client, types
from database.users_chats_db import db
from database.ia_filterdb import Media
from typing import Union, Optional, AsyncGenerator
from utils import temp, __repo__, __license__, __copyright__, __version__
from info import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, UPTIME, WEB_SUPPORT, LOG_MSG

# Get logging configurations
logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

class Bot(Client):

    def __init__(self):
        super().__init__(
            name="Professor-Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=10,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats        
        
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.id = me.id
        self.name = me.first_name
        self.mention = me.mention
        self.username = me.username
        self.log_channel = LOG_CHANNEL
        self.uptime = UPTIME
        curr = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        date = curr.strftime('%d %B, %Y')
        tame = curr.strftime('%I:%M:%S %p')
        logger.info(LOG_MSG.format(me.first_name, date, tame, __repo__, __version__, __license__, __copyright__))
        
        try: 
            await self.send_message(LOG_CHANNEL, text=LOG_MSG.format(me.first_name, date, tame, __repo__, __version__, __license__, __copyright__), disable_web_page_preview=True)   
        except Exception as e: 
            logger.warning(f"Bot Isn't Able To Send Message To LOG_CHANNEL \n{e}")

        # ✅ Web Server Setup with Route
        if bool(WEB_SUPPORT) is True:
            app = web.Application(client_max_size=30000000)
            
            async def home(request):
                return web.Response(text="TCU_TCU Wow", content_type="text/plain")
            
            app.router.add_get("/", home)  # Route added
            
            runner = web.AppRunner(app)
            await runner.setup()
            await web.TCPSite(runner, "0.0.0.0", 8080).start()
            logger.info("Web Response Is Running......🕸️")
            
    async def stop(self, *args):
        await super().stop()
        logger.info(f"Bot Is Restarting ⟳...")

    async def iter_messages(self, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator["types.Message", None]]:                       
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1

Bot().run()
