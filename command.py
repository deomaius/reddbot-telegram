-*- coding: utf-8 -*-

import json
import codecs
import requests
from bs4 import BeautifulSoup, SoupStrainer
import re
import subprocess
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater
from html import escape

updater = Updater(token='BOT_TOKEN')
dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

def commands(bot, update):
	user = update.message.from_user.username 
	bot.send_message(chat_id=update.message.chat_id, text="Initiating commands /tip & /withdraw have a specfic format,\n use them like so:" + "\n \n Parameters: \n <user> = target user to tip \n <amount> = amount of reddcoin to utilise \n <address> = reddcoin address to withdraw to \n \n Tipping format: \n /tip <user> <amount> \n \n Withdrawing format: \n /withdraw <address> <amount>")

def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="The following commands are at your disposal: /hi , /commands , /deposit , /tip , /withdraw , /price , /marketcap or /balance")

def deposit(bot, update):
	user = update.message.from_user.username
	if user is None:
		bot.send_message(chat_id=update.message.chat_id, text="Please set a telegram username in your profile settings!")
	else:
		address = "/usr/local/bin/reddcoind"
		result = subprocess.run([address,"getaccountaddress",user],stdout=subprocess.PIPE)
		clean = (result.stdout.strip()).decode("utf-8")
		bot.send_message(chat_id=update.message.chat_id, text="@{0} your depositing address is: {1}".format(user,clean))

def tip(bot,update):
	user = update.message.from_user.username
	target = update.message.text[5:]
	amount =  target.split(" ")[1]
	target =  target.split(" ")[0]
	if user is None:
		bot.send_message(chat_id=update.message.chat_id, text="Please set a telegram username in your profile settings!")
	else:
		machine = "@Reddcoin_bot"
		if target == machine:
			bot.send_message(chat_id=update.message.chat_id, text="HODL.")
		elif "@" in target:
			target = target[1:]
			user = update.message.from_user.username 
			core = "/usr/local/bin/reddcoind"
			result = subprocess.run([core,"getbalance",user],stdout=subprocess.PIPE)
			balance = float((result.stdout.strip()).decode("utf-8"))
			amount = float(amount)
			if balance < amount:
				bot.send_message(chat_id=update.message.chat_id, text="@{0} you have insufficent funds.".format(user))
			elif target == user:
				bot.send_message(chat_id=update.message.chat_id, text="You can't tip yourself silly.")
			else:
				balance = str(balance)
				amount = str(amount) 
				tx = subprocess.run([core,"move",user,target,amount],stdout=subprocess.PIPE)
				bot.send_message(chat_id=update.message.chat_id, text="@{0} tipped @{1} of {2} RDD".format(user, target, amount))
		else: 
			bot.send_message(chat_id=update.message.chat_id, text="Error that user is not applicable.")

def balance(bot,update):
	quote_page = requests.get('https://www.worldcoinindex.com/coin/reddcoin')
	strainer = SoupStrainer('div', attrs={'class': 'row mob-coin-table'})
	soup = BeautifulSoup(quote_page.content, 'html.parser', parse_only=strainer)
	name_box = soup.find('div', attrs={'class':'col-md-6 col-xs-6 coinprice'})
	name = name_box.text.replace("\n","")
	price = re.sub(r'\n\s*\n', r'\n\n', name.strip(), flags=re.M)
	price = re.sub("[^0-9^.]", "", price)
	price = float(price)
	user = update.message.from_user.username
	if user is None:
		bot.send_message(chat_id=update.message.chat_id, text="Please set a telegram username in your profile settings!")
	else:
		core = "/usr/local/bin/reddcoind"
		result = subprocess.run([core,"getbalance",user],stdout=subprocess.PIPE)
		clean = (result.stdout.strip()).decode("utf-8")
		balance  = float(clean)
		fiat_balance = balance * price
		fiat_balance = str(round(fiat_balance,3))
		balance =  str(round(balance,3))
		bot.send_message(chat_id=update.message.chat_id, text="@{0} your current balance is: {1} RDD ≈  ${2}".format(user,balance,fiat_balance))

def price(bot,update):
	quote_page = requests.get('https://www.worldcoinindex.com/coin/reddcoin')
	strainer = SoupStrainer('div', attrs={'class': 'row mob-coin-table'})
	soup = BeautifulSoup(quote_page.content, 'html.parser', parse_only=strainer)
	name_box = soup.find('div', attrs={'class':'col-md-6 col-xs-6 coinprice'})
	name = name_box.text.replace("\n","")
	price = re.sub(r'\n\s*\n', r'\n\n', name.strip(), flags=re.M)
	fiat = soup.find('span', attrs={'class': ''})
	kkz = fiat.text.replace("\n","")
	percent = re.sub(r'\n\s*\n', r'\n\n', kkz.strip(), flags=re.M)
	quote_page = requests.get('https://bittrex.com/api/v1.1/public/getticker?market=btc-rdd')
	soup = BeautifulSoup(quote_page.content, 'html.parser').text
	btc = soup[80:]
	sats = btc[:-2]
	bot.send_message(chat_id=update.message.chat_id, text="Reddcoin is valued at {0} Δ {1} ≈ {2}".format(price,percent,sats) + " ฿")

def withdraw(bot,update):
	user = update.message.from_user.username
	if user is None:
		bot.send_message(chat_id=update.message.chat_id, text="Please set a telegram username in your profile settings!")
	else:
		target = update.message.text[9:]
		address = target[:35]
		address = ''.join(str(e) for e in address)
		target = target.replace(target[:35], '')
		amount = float(target)
		core = "/usr/local/bin/reddcoind"
		result = subprocess.run([core,"getbalance",user],stdout=subprocess.PIPE)
		clean = (result.stdout.strip()).decode("utf-8")
		balance = float(clean)
		if balance < amount:
			bot.send_message(chat_id=update.message.chat_id, text="@{0} you have insufficent funds.".format(user))
		else:
			amount = str(amount)
			tx = subprocess.run([core,"sendfrom",user,address,amount],stdout=subprocess.PIPE)
			bot.send_message(chat_id=update.message.chat_id, text="@{0} has successfully withdrew to address: {1} of {2} RDD" .format(user,address,amount))

def hi(bot,update):
	user = update.message.from_user.username
	bot.send_message(chat_id=update.message.chat_id, text="Hello @{0}, how are you doing today?".format(user))

def moon(bot,update):
  bot.send_message(chat_id=update.message.chat_id, text="Moon mission inbound!")

def marketcap(bot,update):
	quote_page = requests.get('https://www.worldcoinindex.com/coin/reddcoin')
	strainer = SoupStrainer('div', attrs={'class': 'row mob-coin-table'})
	soup = BeautifulSoup(quote_page.content, 'html.parser', parse_only=strainer)
	name_box = soup.find('div', attrs={'class':'col-md-6 col-xs-6 coin-marketcap'})
	name = name_box.text.replace("\n","")
	mc = re.sub(r'\n\s*\n', r'\n\n', name.strip(), flags=re.M)
	bot.send_message(chat_id=update.message.chat_id, text="The current market cap of Reddcoin is valued at {0}".format(mc))

from telegram.ext import CommandHandler

commands_handler = CommandHandler('commands', commands)
dispatcher.add_handler(commands_handler)

moon_handler = CommandHandler('moon', moon)
dispatcher.add_handler(moon_handler)

hi_handler = CommandHandler('hi', hi)
dispatcher.add_handler(hi_handler)

withdraw_handler = CommandHandler('withdraw', withdraw)
dispatcher.add_handler(withdraw_handler)

marketcap_handler = CommandHandler('marketcap', marketcap)
dispatcher.add_handler(marketcap_handler)

deposit_handler = CommandHandler('deposit', deposit)
dispatcher.add_handler(deposit_handler)

price_handler = CommandHandler('price', price)
dispatcher.add_handler(price_handler)

tip_handler = CommandHandler('tip', tip)
dispatcher.add_handler(tip_handler)

balance_handler = CommandHandler('balance', balance)
dispatcher.add_handler(balance_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

updater.start_polling()

