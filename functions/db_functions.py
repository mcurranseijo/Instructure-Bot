import aiomysql

class dbFunctions:
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db

    async def connect(self):
        pool = await aiomysql.create_pool(host=self.host, user=self.user, password=self.password, db=self.db)
        return pool

    async def get_canvas(self, user_id):
        pool = await self.connect()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT `ID`, `discord_id`, `api_key`, `canvas_url`, `public`, `reminders` FROM `API_Keys` WHERE discord_id = %s", (user_id,))
                api_key = await cursor.fetchone()
                return api_key

    async def insert_canvas(self, user_id, api_key, api_url):
        pool = await self.connect()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f"INSERT INTO `API_Keys`(`discord_id`, `api_key`, `canvas_url`) VALUES ('{user_id}','{api_key}','{api_url}')")
                await conn.commit()

    async def remove_canvas(self, user_id):
        pool = await self.connect()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM `API_Keys` WHERE discord_id = %s", (user_id,))
                await conn.commit()

    async def toggle_canvas(self, user_id, toggle):
        pool = await self.connect()
        if toggle == True:
            toggle = 1
        else:
            toggle = 0
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("UPDATE `API_Keys` SET `public` = %s WHERE discord_id = %s", (toggle, int(user_id)))
                await conn.commit()
                
    
    async def toggle_reminder(self, user_id, toggle):
        pool = await self.connect()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("UPDATE `API_Keys` SET `reminders` = %s WHERE discord_id = %s", (toggle, str(user_id)))
                await conn.commit()

    async def update_url(self, user_id, api_url):
        pool = await self.connect()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("UPDATE `API_Keys` SET `canvas_url` = %s WHERE discord_id = %s", (api_url, str(user_id)))
                await conn.commit()

    async def get_all(self):
        pool = await self.connect()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT `discord_id`, `api_key`, `canvas_url`, `reminders` FROM `API_Keys`")
                api_keys = await cursor.fetchall()
                return api_keys
