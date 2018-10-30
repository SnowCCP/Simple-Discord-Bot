import json
import asyncio


class Config:
    """Access to the .json config file."""
    __instance = None

    def __init__(self, name):
        self.name = name

        self.lock = asyncio.Lock()
        self.loop = asyncio.get_event_loop()
        self.load_from_file()

    def __new__(cls, name):
        if Config.__instance is None:
            Config.__instance = object.__new__(Config)
        return Config.__instance

    def load_from_file(self):
        try:
            with open(self.name, "r", encoding="utf-8") as file:
                self._data = json.load(file)
        except FileNotFoundError:
            self._data = dict()

    async def load(self):
        with await self.lock:
            await self.loop.run_in_executor(None, self.load_from_file())

    def _dump(self):
        with open(self.name, 'w', encoding="utf-8") as file:
            json.dump(self._data.copy(), file, sort_keys=True, indent=4, ensure_ascii=False)

    async def save(self):
        with await self.lock:
            await self.loop.run_in_executor(None, self._dump)

    def get_forbidden_prefix(self, guild: str):
        if "forbidden_prefix" not in self._data[guild]:
            return []
        return self._data[guild]["forbidden_prefix"]

    async def add_forbidden_prefix(self, guild: str, forbidden_prefix):
        if "forbidden_prefix" not in self._data[guild]:
            self._data[guild].update({"forbidden_prefix": []})
        self._data[guild]["forbidden_prefix"].append(forbidden_prefix)
        await self.save()

    async def delete_forbidden_prefix(self, guild: str, forbidden_prefix):
        if "forbidden_prefix" not in self._data[guild]:
            self._data[guild].update({"forbidden_prefix": []})
        self._data[guild]["forbidden_prefix"].append(forbidden_prefix)
        await self.save()

    async def add_guild(self, guild: str):
        if guild not in self._data:
            self._data.update({guild: dict()})
        await self.save()
