#!/usr/bin/env python3

from telegram import Update
from telegram.ext import Application, CommandHandler, filters, MessageHandler, ContextTypes
from typing import Final
import google.generativeai as palm
import requests
import json
import os

palm_key = os.environ['PALM_API_KEY']
TOKEN: Final = os.environ['TOKEN']
my_jokes_key = os.environ['JOKES_KEY']

BOT_USERNAME: Final = '@AlmightyKitten_bot'

def get_fact():
    api_url = 'https://api.api-ninjas.com/v1/facts'
    response = requests.get(api_url, headers={'X-Api-Key': my_jokes_key})
    if response.status_code == requests.codes.ok:
        json_data = json.loads(response.text)
        fact = json_data[0]['fact']
        return fact

def get_jokes():
  api_url = 'https://api.api-ninjas.com/v1/jokes'
  response = requests.get(api_url, headers={'X-Api-Key': my_jokes_key})
  if response.status_code == requests.codes.ok:
    json_data = json.loads(response.text)
    joke = json_data[0]['joke']
    return joke

def get_quotes():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

def convert_currency(from_currency='USD', to_currency='Eur', amount=1):
    api_url = f'https://api.api-ninjas.com/v1/convertcurrency?want={to_currency}&have={from_currency}&amount={amount}'

    headers = {'X-Api-Key': my_jokes_key}
    response = requests.get(api_url, headers=headers)

    if response.status_code == requests.codes.ok:
        data = response.json()
        converted_amount = data['new_amount']
        return converted_amount
    else:
        return None

def get_answer(query):
    palm.configure(api_key=palm_key)
    models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
    model = models[0].name
    prompt = "You're a chatbot that answers questions. Your name is Almighty Kitten. Act like a kitten when answering questions\n\n" + query

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        # The maximum length of the response
        max_output_tokens=800,
    )
    return completion.result

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f'Hi {update.effective_user.first_name}! Want to talk to me?'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '/inspire - Inspire you! \n/joke - Tells a joke! \n/define <word> - Defines a word! \n/fact - Tells a fact! \n/ask <question> - Asks a question! \n/currency <amount> <from_currency> <to_currency> - Converts currency!'
    )

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = get_jokes()
    await update.message.reply_text(joke)

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = get_quotes()
    await update.message.reply_text(quote)

async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fact = get_fact()
    await update.message.reply_text(fact)

async def convert_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = update.message.text.split(' ')[1]
    from_currency = update.message.text.split(' ')[2]
    to_currency = update.message.text.split(' ')[3]
    converted_amount = convert_currency(from_currency, to_currency, amount)
    if converted_amount is not None:
      await update.message.reply_text(f'{amount} {from_currency} = {converted_amount} {to_currency}')
    else:
      await update.message.reply_text('Sorry, I couldn\'t convert the currency.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = get_answer(new_text)
        else:
            return
    else:
        response: str = get_answer(text)
    print('Bot: ', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('joke', joke))
    app.add_handler(CommandHandler('quote', quote))
    app.add_handler(CommandHandler('fact', fact))
    app.add_handler(CommandHandler('convert_currency', convert_money))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)
