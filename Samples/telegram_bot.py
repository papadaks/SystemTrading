import telepot 
import pprint

token = "5435932808:AAH2g1SV793wxWmVEzyFTShCpCxJrYV6GtE"
bot = telepot.Bot(token)

info = bot.getMe()
pprint.pprint(info)

