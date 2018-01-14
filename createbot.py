"""Main file to tie markov chaining and groupme scraping together"""
import os
from lib.markov.model import model_markov
from lib.markov.generate import generate
from lib.scrape.groupme import scrape_history
from settings import TOKEN, GROUP_ID, USER_ID, USER_NAME, PATH, MSG_COUNT, MSG_LIMIT

def create_bot():
    scrape_history(TOKEN, GROUP_ID, USER_ID, USER_NAME, PATH, MSG_COUNT, MSG_LIMIT)
    model_markov(PATH, USER_NAME)
    generate()

create_bot()