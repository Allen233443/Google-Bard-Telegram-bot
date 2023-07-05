from telegram import ParseMode, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bardapi import Bard
import os
import keep_alive
# Set the Bard API key
os.environ["_BARD_API_KEY"] = "YOUR_BARD_API"

# Dictionary to store the last messages
last_messages = {}

# Maximum message length allowed by Telegram
MAX_MESSAGE_LENGTH = 4096

# Define a command handler for /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the chatbot! Please enter your query.")

# Define a message handler for text messages
def handle_message(update, context):
    # Show typing indicator while generating the response
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    # Get the user input
    user_input = update.message.text
    
    # Get the chat ID
    chat_id = update.effective_chat.id
    
    # Get the last message from the dictionary
    last_message = last_messages.get(chat_id)
    
    # Append the last user message and the last Bard response as context
    context_text = last_message['user'] + '\n' + last_message['bard'] if last_message else ''
    
    # Append the current user message to the context
    context_text += '\n' + user_input
    
    try:
        # Call the Bard API to get an answer
        response = Bard().get_answer(context_text)
    
        # Store the current user message and the Bard response in the dictionary
        last_messages[chat_id] = {
            'user': user_input,
            'bard': response['content']
        }
    
        # Split the response into parts if it exceeds the maximum message length
        response_parts = [response['content'][i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(response['content']), MAX_MESSAGE_LENGTH)]
    
        # Send the response parts as separate messages with text markup
        for part in response_parts:
            context.bot.send_message(chat_id=chat_id, text=part, parse_mode=ParseMode.HTML)

    except Exception as e:
        # Handle errors gracefully
        error_message = f"An error occurred: {str(e)}"
        context.bot.send_message(chat_id=chat_id, text=error_message)

# Define a command handler for /clear command
def clear(update, context):
    # Get the chat ID
    chat_id = update.effective_chat.id
    
    # Remove the last message for the user from the dictionary
    last_messages.pop(chat_id, None)
    
    context.bot.send_message(chat_id=chat_id, text="Last messages cleared.")
keep_alive.keep_alive()
# Error handler
def error(update, context):
    """Log Errors caused by Updates."""
    context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred. Please try again later.")

# Set up the Telegram bot
updater = Updater(token="YOUR_TELEGRAM_TOKEN", use_context=True)
dispatcher = updater.dispatcher

# Add handlers for /start command, /clear command, and text messages
start_handler = CommandHandler('start', start)
clear_handler = CommandHandler('clear', clear)
message_handler = MessageHandler(Filters.text & ~Filters.command, handle_message)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(clear_handler)
dispatcher.add_handler(message_handler)

# Add error handler
dispatcher.add_error_handler(error)

# Start the bot
updater.start_polling()
updater.idle()
