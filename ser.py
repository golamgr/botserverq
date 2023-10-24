import requests
import os
import json
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    ConversationHandler, CallbackContext
)

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext




# Your Telnyx API key (replace with your actual API key)
# Define conversation states
TOKEN = 0
NAME = 1

NUMBER = 0
# Initialize user data
user_data = {}
waiting_for_photo = {}
# Initialize user credits
try:
    with open('user_credits.json', 'r') as f:
        user_credits = json.load(f)
except FileNotFoundError:
    user_credits = {}

# Admin user ID (replace with your actual admin user ID)
admin_user_id = 6077402681

def start(update: Update, context: CallbackContext):
    # Create two keyboard buttons
    name = KeyboardButton("🤖 Change Name")
    txt = KeyboardButton("👩‍💻 NUMBER")
    join = KeyboardButton("🔗Join")
    contact = KeyboardButton("👥Contact")
    balance = KeyboardButton("💰 Balance")

    # Create a ReplyKeyboardMarkup with the buttons arranged in two separate rows
    # Create a ReplyKeyboardMarkup with the buttons
    reply_markup = ReplyKeyboardMarkup([[name], [txt], [join, contact], [balance]], resize_keyboard=True)

    # Send a message with the keyboard
    update.message.reply_text("Please choose an Mode :", reply_markup=reply_markup)
    

def sms(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Please enter the Telegram Bot Api Token:")
    return TOKEN

def send_sms(update: Update, context: CallbackContext) -> int:
    token = update.message.text
    context.user_data['bot_token'] = token
    update.message.reply_text("Please enter New Name:")
    return NAME

def confirm_sms(update: Update, context: CallbackContext) -> int:
    name = update.message.text
    token = context.user_data['bot_token']

    # Check user's credit balance
    user_id = update.effective_user.id
    if user_id not in user_credits:
        user_credits[user_id] = 1  # Initialize with zero credits if not set

    if user_credits[user_id] < 1:
        update.message.reply_text("Sorry, you have insufficient credit.")
        return ConversationHandler.END

    # Create the message payload
    url = f'https://api.telegram.org/bot{token}/setMyName?name={name}'

    # Send the SMS using the Telnyx API
    response = requests.get(url)

    if response.status_code == 200:
        user_credits[user_id] -= 1  # Deduct one credit for a successful SMS
        update.message.reply_text(f'Successfully ✅! You have {user_credits[user_id]} credits remaining.', reply_markup=ReplyKeyboardRemove())
        save_user_credits()  # Save user credits to file
    else:
        update.message.reply_text(f'Failed. Status code: {response.status_code}', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def save_user_credits():
    with open('user_credits.json', 'w') as f:
        json.dump(user_credits, f)

def balance(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in user_credits:
        user_credits[user_id] = 0 # Initialize with zero credits if not set

    update.message.reply_text(f'Your current credit balance: {user_credits[user_id]}')

def add_credit(update: Update, context: CallbackContext) -> None:
    # Check if the user is an admin
    if update.effective_user.id != admin_user_id:
        update.message.reply_text("You are not authorized to add credit.")
        return

    try:
        user_id_to_add_credit = int(context.args[0])
        amount_to_add = int(context.args[1])

        # Add credit to the user
        if user_id_to_add_credit not in user_credits:
            user_credits[user_id_to_add_credit] = 0
        user_credits[user_id_to_add_credit] += amount_to_add

        update.message.reply_text(f'Added {amount_to_add} credits to user {user_id_to_add_credit}.')
    except (ValueError, IndexError):
        update.message.reply_text("Invalid format. Please use /addcredit <user_id> <amount>.")

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Changing canceled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
    


def join(update, context):
    update.message.reply_text("That is our official channel \n @cracked71")
    
def contact(update, context):
    update.message.reply_text("For contact \n @zxrock")



def number(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Please enter Number:")
    return NUMBER

def sendrequest(update: Update, context: CallbackContext) -> int:
    number = update.message.text
    # Check user's credit balance
    user_id = update.effective_user.id
    if user_id not in user_credits:
        user_credits[user_id] = 0  # Initialize with zero credits if not set

    if user_credits[user_id] < 1:
        update.message.reply_text("Sorry, you have insufficient credit.")
        return ConversationHandler.END

    # Create the message payload
    url = f'https://darkx.xyz/api/Main/info.php?number=0{number}'

    # Send the SMS using the Telnyx API
    response = requests.get(url)

    if response.status_code == 200:
        data = response.text
          # Deduct one credit for a successful SMS

        # Parse the JSON response
        try:
            response_data = json.loads(data)
            brand = response_data["data"]["brand"]
            dob = response_data["data"]["dob"]
            id_type = response_data["data"]["idName"]
            time = response_data["data"]["createdTime"]
            gender = response_data["data"]["gender"]
            id_id = response_data["data"]["idTypeValue"]
            customer_name = response_data["data"]["customerName"]
            msisdn = response_data["data"]["msisdn"]
            customer_type = response_data["data"]["customerType"]
            process_name = response_data["data"]["processName"]
      
            update.message.reply_text(f'Information Received\n'
                                      f'Brand : {brand}\n'
                                      f'D-O-B : {dob}\n'                    
                                      f'Customer Name: {customer_name}\n'
                                      f'MSISDN: {msisdn}\n'
                                      f'Gender: {gender}\n' 
                                      f'Create Time: {time}\n'                  
                                      f'Customer Type: {customer_type}\n'
                                      f'{id_type}: {id_id}\n'
                                      f'Process Name: {process_name}',
                                      reply_markup=ReplyKeyboardRemove())
            user_credits[user_id] -= 10
        except json.JSONDecodeError as e:
            update.message.reply_text("Failed to parse the response data.")
        except KeyError as e:
            update.message.reply_text("Some expected data is missing in the response.")
        
        # Save user credits to file
        save_user_credits()
    else:
        update.message.reply_text(f'Failed. Status code: {response.status_code}', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END



# Define the main function
def main():
    updater = Updater(token='6339860868:AAEfuxgKkVXo7lSfEJbOA_5u47WKOhFCIVk', use_context=True)
    dispatcher = updater.dispatcher

    # Define conversation handlers
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text("🤖 Change Name"), sms)],
        states={
            TOKEN: [MessageHandler(Filters.text, send_sms)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    numv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text("👩‍💻 NUMBER"), number)],
        states={
            NUMBER: [MessageHandler(Filters.text, sendrequest)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Define the /balance command handler
    dispatcher.add_handler(MessageHandler(Filters.text("💰 Balance"), balance))
    dispatcher.add_handler(MessageHandler(Filters.text("🔗Join"), join))

    dispatcher.add_handler(MessageHandler(Filters.text("👥Contact"), contact))
    dispatcher.add_handler(CommandHandler('start', start ))
    dispatcher.add_handler(CommandHandler('addcoin', add_credit, pass_args=True))

    # Add conversation handlers to the dispatcher
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(numv_handler)
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
