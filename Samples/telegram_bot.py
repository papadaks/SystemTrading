import telepot 
import pprint

token = "5435932808:AAEX4vK-CE_fxZMO74uZ1mu3oQI4mnFpc_Q"
bot = telepot.Bot(token)

info = bot.getMe()
pprint.pprint(info)

resp = bot.getUpdates()
pprint.pprint(resp)

bot.sendMessage(chat_id=1697475589, text="Hi I am a Bot")

