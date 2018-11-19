import re
import uuid
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime
from math import ceil


class Guide:
    __instance = None

    @staticmethod
    def get_instance():
        if Guide.__instance is None:
            Guide()
        return Guide.__instance

    def __init__(self):
        if Guide.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Guide.__instance = self
            self.events = []
            self.scr = Scraper()
            self.scrape_events()

    def add_event(self, event):
        self.events.append(event)

    def scrape_events(self):
        self.events = self.scr.get_events()
        print(f"Añadidos {len(self.events)} eventos a la guía")

    def get_next_events(self, num, sport=None):
        return self.events[:num]

    def get_all_events(self):
        return self.events

    def get_event_by_uuid(self, event_id):
        for event in self.events:
            # print(event.uuid, event_id)
            if event.uuid == event_id:
                return event
        return None

    def get_by_sport(self, sport):
        filtered_events = []
        for event in self.events:
            if event.sport == sport:
                filtered_events.append(event)
        return filtered_events

    def get_links_by_uuid(self, event_id):
        for event in self.events:
            if event.uuid == event_id:
                for channel in event.channels:
                    channel.scrape_link()
                return event
        return None

    def debug_print_all(self):
        for i, event in enumerate(self.events):
            print(f"Event {i}:\nName: {event.name}\nDate: {event.date}\nSport: {event.sport}\nCompetition: {event.competition}\nChannels: {event.channels}\nUuid: {event.uuid}\n\n")


class Event:
    def __init__(self, name, date, sport, competition, channels):
        self.name = name
        self.date = date
        self.sport = sport
        self.competition = competition
        self.channels = channels
        self.uuid = str(uuid.uuid4())


class Channel:
    def __init__(self, number, language, link=None):
        self.number = number
        self.language = language
        self.link = link
        self.scr = Scraper()

    def scrape_link(self):
        self.link = self.scr.get_channel_link(self.number)


class MessageListener:
    __instance = None

    @staticmethod
    def get_instance():
        if MessageListener.__instance is None:
            MessageListener()
        return MessageListener.__instance

    def __init__(self):
        if MessageListener.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            MessageListener.__instance = self
            self.__data = dict()
            self.guide = Guide.get_instance()
            self.events_per_page = 5
            self.emojis = {"1": "1⃣", "2": "2⃣", "3": "3⃣", "4": "4⃣", "5": "5⃣", "6": "6⃣", "7": "7⃣", "8": "8⃣",
                           "9": "9⃣",
                           "right": "▶", "left": "◀", "delete": "❌"}
            self.emojis_number = {"1": "1⃣", "2": "2⃣", "3": "3⃣", "4": "4⃣", "5": "5⃣"}

    def add_guild(self, guild: str):
        if guild not in self.__data:
            self.__data.update({guild: dict()})

    def add_events(self, guild, message_id, events):
        self.add_guild(guild)
        self.__data[guild].update({message_id: dict()})
        self.__data[guild][message_id].update({"page": 1})
        print(f"Añadiendo {len(events)} eventos al listener")
        for i, event in enumerate(events):
            self.__data[guild][message_id].update({str(i+1): event.uuid})
        return self.get_events(guild, message_id)

    def is_message_on_listener(self, guild, message_id):
        if message_id in self.__data[guild]:
            return True
        return False

    def get_events(self, guild, message_id):
        events = []
        for i in range(self.events_per_page):
            if self.get_uuid_event(guild, message_id, i+1) is not None:
                events.append(self.guide.get_event_by_uuid(self.get_uuid_event(guild, message_id, i+1)))
        return events

    def get_uuid_event(self, guild, message_id, num):
        real_num = (self.events_per_page * (self.__data[guild][message_id].get("page")-1)) + num
        if str(real_num) in self.__data[guild][message_id]:
            return self.__data[guild][message_id].get(str(real_num))
        return None

    def get_page(self, guild, message_id):
        page = self.__data[guild][message_id].get("page")
        page_total = ceil((self.__data[guild][message_id].__len__() - 1) / self.events_per_page)
        return page, page_total

    def has_next_page(self, guild, message_id):
        if self.__data[guild][message_id].get("page")*self.events_per_page < self.__data[guild][message_id].__len__():
            self.__data[guild][message_id]["page"] = self.__data[guild][message_id].get("page") + 1
            return True
        return False

    def has_previous_page(self, guild, message_id):
        if self.__data[guild][message_id].get("page") > 1:
            self.__data[guild][message_id]["page"] = self.__data[guild][message_id].get("page")-1
            return True
        return False

    def delete_message(self, guild, message_id):
        self.__data[guild].pop(message_id)

    def update_message_id(self, guild, message_id_new, message_id_old):
        self.__data[guild][message_id_new] = self.__data[guild].pop(message_id_old)


class Scraper:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if Scraper.__instance is None:
            Scraper.__instance = object.__new__(Scraper)
        return Scraper.__instance

    url = "http://arenavision.us/guide"
    url_channel = "http://cdn5.arenavision.link/"
    pattern_ace = "^.+?>\s*(.+?)\s*<.+?\">\s*(.+?)\s.+?\">\s*(.+?)\s*<.+?\">\s*(.+?)<.+?\">\s*(.+?)<\s*.+?\">\s*(.+?)</td>"
    pattern_ch = "\s*(.+?)\s*\[(.+?)\]"

    def get_events(self):
        req = Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})
        website = urlopen(req).read()

        soup = BeautifulSoup(website, "html.parser")
        soup = soup.find_all('table', attrs={"class": "auto-style1"})
        soup = soup[0].prettify().replace("\n", "").split("<tr>")[2:-2]

        events = []

        for entry in soup:
            m = re.match(self.pattern_ace, entry)
            if m:
                date = datetime.strptime(m.group(1) + " " + m.group(2), "%d/%m/%Y %H:%M")
                sport = m.group(3)
                competition = m.group(4)
                name = m.group(5)
                channels = self.get_channels(m.group(6))

                event = Event(name, date, sport, competition, channels)
                events.append(event)

        return events

    def get_channels(self, soup):
        channels = []
        soup = soup.split("<br/>")

        for entry in soup:
            m = re.match(self.pattern_ch, entry)
            if m:
                entries = m.group(1).split("-")
                for channel in entries:
                    channels.append(Channel("{:02}".format(int(channel)), m.group(2)))

        return channels

    def get_channel_link(self, channel):
        req = Request(self.url_channel + channel, headers={'User-Agent': 'Mozilla/5.0'})
        website = urlopen(req).read()

        soup = BeautifulSoup(website, "html.parser")
        soup = soup.find('p', attrs={"class": "auto-style1"}).find_all("a")

        return soup[0].get('href')
