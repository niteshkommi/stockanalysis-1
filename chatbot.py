from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
bot=ChatBot(name='chat',logic_adapters=['chatterbot.logic.TimeLogicAdapter',
                                 'chatterbot.logic.BestMatch','chatterbot.logic.SpecificResponseAdapter'])
trainer=ChatterBotCorpusTrainer(bot)
trainer.train(
    "chatterbot.corpus.english.greetings",
    "chatterbot.corpus.english.conversations",
    "chatterbot.corpus.english.money"
)
print('Bot: hi,and welcome! ask me something')
while True:
    inp=input('\nYou :')
    if inp=='done':
        break
    else:
        resp=bot.get_response(inp)
        print('\nBot :',resp)