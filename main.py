from mysql.connector import connect
import os
from telebot import TeleBot, apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import pyshorteners
from telebot.util import user_link
from time import strftime

BITLY_TOKEN = os.getenv('BITLY_TOKEN')
TOKEN = os.getenv('TOKEN')

apihelper.ENABLE_MIDDLEWARE = True
bot = TeleBot(TOKEN)

def connection():
	kwargs = {
			'host':'containers-us-west-62.railway.app', 
			'user': 'root',
			'database': 'railway', 
			'password': 'J9ZP9AFJlVt47aP4gMnI',
			'port':5743
	}
	conn = connect(**kwargs)
	return conn
		
class DataBase:
	def update_query(self, query: str, *args):
		conn = connection()
		cur = conn.cursor()
		if not args:
			cur.execute(query)
		else:
			cur.execute(query, args)
		conn.commit()
		
	def found(self, user_id: int):
		conn = connection()
		cur = conn.cursor()
		cur.execute("SELECT user_id FROM users")
		users_id = [j for i in cur.fetchall() for j in i]
		if user_id in users_id:
			return True
		else:
			return False
			
def community(home=True):
	btn = InlineKeyboardMarkup(row_width=1)
	if home:
		btn.add(InlineKeyboardButton("👥 Community", url="t.me/Ethiopians_Project"), InlineKeayboardButton('🤖 Our Bots', callback='ubots'))
	else:
		btn.add(InlineKeyboardButton("« Back", callback_data='back'))
	return btn

hello_text = '''Hello %s!\n\nWelcome to bitly link shortener bot 😊\n send me any link i will make short for you using bitly.com\n.Join our community for more.
'''
db = DataBase()

@bot.middleware_handler(update_types=['message'])
def get_updates(instance, msg):
	if isinstance(msg, CallbackQuery):
		bot.answer_callback_query(call.id)			
@bot.message_handler(commands=['start'], chat_types=['private'])
def welcome_msg(message):
    user_info = message.from_user
    
    if not db.found(message.chat.id):
    	db.update_query("INSERT INTO users VALUES (%s, %s)", message.chat.id, stftime("%D"))
    	
    user = user_link(user_info)
    bot.send_message(message.chat.id, hello_text%user,reply_markup = community(), parse_mode='HTML')
  
@bot.message_handler(func = lambda msg: True)
def make_short(msg):
    link = msg.text
    shortener = pyshorteners.Shortener(api_key = BITLY_LINK)
    try:
    	link_shortener = shortener.bitly.short(link)
    except:
    	link_shortener = 'Error:\ndue to the link is in correct.'
    bot.reply_to(msg, link_shortener)

@bot.callback_query_handler(lambda call: True)
def all_callback(call):
	
	user = user_link(call.from_user)
	
	if call.data == 'ubots':
		with open("devs.txt", 'r') as file:
			bot.edit_message_text(file.read(), call.message.chat.id, call.message.message_id, reply_markup=community(False), parse_mode="HTML")
			file.close()
			
	elif call.data == 'back':
		bot.edit_message_text(hello_text%user, call.message.chat.id, call.message.message_id, reply_markup=community(), parse_mode='HTML')

if __name__ == '__main__':
	bot.infinity_polling()
