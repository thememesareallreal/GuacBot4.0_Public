from cogs.extraclasses.perms import *
from cogs.extraclasses.read import *
from cogs.extraclasses.jason import *
import random, time, json, discord, torch
from discord.ext import commands, bridge

from cogs.extraclasses.model import NeuralNet
from cogs.extraclasses.nltk_utils import bag_of_words, tokenize
from cogs.extraclasses.jason import *

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('data/intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

botData = FetchBotData()
serverData = FetchServerData()

def charLimit(index, responsesList):
    reactionMessage = responsesList[index]
    if (len(reactionMessage) > 2000):
        substringList = []
        loops = (int) (len(reactionMessage) / 2000)
        x = 0
        for i in range(loops + 1):
            substringList.append(reactionMessage[x:x + 2000])
            x = x + 2000
        return substringList
    else:
        return [responsesList[index]]

def interaction(name, sentence):
    message = sentence
    sentence = tokenize(sentence)
    sentence.pop(sentence.index(name))
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return f"{random.choice(intent['responses'])}"
    else:
        if random.randint(1, 2) != 2:
            return
        else:
            responses = ["I do not understand...", "I don't get it?", "Huh?", f'Calling "{message}" on mobile?']
            return responses[random.randint(0,len(responses) - 1)]

class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('GuacBot speech active.')

    @commands.Cog.listener()
    async def on_message(self, message):
        botData = FetchBotData()
        serverData = FetchServerData()

        if message.author == self.bot.user:
            return
        if self.bot.user.mentioned_in(message) and not message.mention_everyone and message.reference is None:
            await message.channel.send("Use $help in a channel I can send messages in, use $invite to invite me to your own server, or use this link to join the support server: https://discord.gg/2kgZazXN68")
            return
        if random.randint(1, 3) != 3:
            return
        try:
            if not serverData[str(message.guild.id)]["Reactions"]["reactions"]:
                return
            if message.author.bot and not serverData[str(message.guild.id)]["Reactions"]["botreactions"]:
                return
            if message.guild.id in botData["Reactions"]["server_blacklist"] or message.author.id in serverData[str(message.guild.id)]["Reactions"]["blacklist"]:
                return
        except:
            pass
        if message.author.id in botData["Reactions"]["global_blacklist"]:
            return
        if "not now, guac" == message.content.lower() and message.author.id == 409445517509001216:
            botData["Reactions"]["wait_until"] = time.time() + 300.0
            UpdateBotData(botData)
            await message.channel.send("Sorry, I'll be back in five...")
            return
        if botData["Reactions"]["wait_until"] > time.time():
            return
        lowerMessage = message.content.lower()
        if "guacbot" in lowerMessage or "guac" in lowerMessage or "guacy" in lowerMessage or "guaccy" in lowerMessage or "guacity" in lowerMessage:
            name = lowerMessage.split("guac")[1]
            name = "guac" + name.split(" ")[0]
            name = tokenize(name)[0]
            await message.channel.send(interaction(name, lowerMessage))
            return
        
        triggersList = ReadTriggers()
        responsesList = ReadResponses()

        punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''
        unPuncMessage = message.content.lower()
        for char in unPuncMessage: 
            if char in punc:
                unPuncMessage = unPuncMessage.replace(char, " ") 
        for trigger in triggersList:
            if not isinstance(trigger, str):
                for subtrigger in trigger:
                    if Conditional(unPuncMessage, subtrigger):
                        reaction = charLimit(triggersList.index(trigger), responsesList)
                        for i in reaction:
                            if "\\n" in i:
                                i = i.replace("\\n", "\n")
                            await message.channel.send(str(i))
            else:
                if Conditional(unPuncMessage, trigger):
                    reaction = charLimit(triggersList.index(trigger), responsesList)
                    for i in reaction:
                        if "\\n" in i:
                            i = i.replace("\\n", "\n")
                        await message.channel.send(str(i))

        #Conditional(fullMessage, trigger)

        #Special
        if "i’m " in message.content.lower():
            if "I’m" in message.content:
                await message.channel.send('Hello "' + message.content.split("I’m ")[1] + '", I\'m GuacBot!')
            else:
                await message.channel.send('Hello "' + message.content.split("i’m ")[1] + '", I\'m GuacBot!')

        #Special
        if "i'm " in message.content.lower():
            if "I'm" in message.content:
                await message.channel.send('Hello "' + message.content.split("I'm ")[1] + '", I\'m GuacBot!')
            else:
                await message.channel.send('Hello "' + message.content.split("i'm ")[1] + '", I\'m GuacBot!')

        #Special
        if " im " in message.content.lower():
            if "Im" in message.content:
                await message.channel.send('Hello "' + message.content.split(" Im ")[1] + '", I\'m GuacBot!')
            else:
                await message.channel.send('Hello "' + message.content.split(" im ")[1] + '", I\'m GuacBot!')

        #Special
        if "i am " in message.content.lower():
            if "I am" in message.content:
                await message.channel.send('Hello "' + message.content.split("I am ")[1] + '", I\'m GuacBot!')
            else:
                await message.channel.send('Hello "' + message.content.split("i am ")[1] + '", I\'m GuacBot!')

        #Special
        if "lmao" == unPuncMessage or "lmfao" == unPuncMessage:
            await message.channel.send(message.content)

        #Special
        if "what" == message.content.lower():
            finishers = ["...the heck?",
            "...in the world?",
            "...in the goddamn?",
            "...the hell?",
            "...is going on here?",
            "...are you on about?",
            "...is the quadratic formula?"]
            i = len(finishers) - 1
            finisherChoice = random.randint(0, i)
            await message.channel.send(finishers[finisherChoice])
            
        #Special
        if "what?" == message.content.lower():
            finishers = ["I have no idea.",
            "Beats me.",
            "Time to get a watch... wait.",
            "Wouldn't you like to know?"]
            i = len(finishers) - 1
            finisherChoice = random.randint(0, i)
            await message.channel.send(finishers[finisherChoice])
                
        #Special
        if "love you" in message.content.lower():
            if "i love you" in message.content.lower():
                await message.channel.send("I love you too, full homo")
            else:
                await message.channel.send("I love you too, no homo")

        #Special
        if "spanish" in message.content.lower():
            if random.randint(1,3) == 1:
                await message.channel.send("Nobody expects The Spanish Inquisition!")

        #Special
        if "micolash" in message.content.lower() or "kos" in message.content.lower() or "bloodborne" in message.content.lower():
            quotes = ["Ahh, Kos, or some say Kosm... Do you hear our prayers?",
            "No, we shall not abandon the dream.",
            "No one can catch us! No one can stop us now! *cackling*",
            "Ah hah hah ha! Ooh! Majestic! A hunter is a hunter, even in a dream. But, alas, not too fast! The nightmare swirls and churns unending!",
            "As you once did for the vacuous Rom, grant us eyes, grant us eyes. Plant eyes on our brains, to cleanse our beastly idiocy.",
            "The grand lake of mud, hidden now, from sight.",
            "The cosmos, of course!",
            "Let us sit about, and speak feverishly. Chatting into the wee hours of...",
            "Now I'm waking up, I'll forget everything...",
            "AAAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHHH"]
            i = len(quotes) - 1
            quotechoice = random.randint(0, i)
            await message.channel.send(quotes[quotechoice])

        #Special
        if "shakespeare" in message.content.lower():
            quotes = ["To be, or not to be: that is the question: Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles, And by opposing end them. To die: to sleep...",
            "This above all: to thine own self be true, And it must follow, as the night the day, Thou canst not then be false to any man.",
            "Cowards die many times before their deaths; The valiant never taste of death but once.",
            "Men at some time are masters of their fates: The fault, dear Brutus, is not in our stars, But in ourselves, that we are underlings.",
            "What's in a name? That which we call a rose By any other word would smell as sweet...",
            "Good night, good night! Parting is such sweet sorrow, That I shall say good night till it be morrow.",
            "All the world's a stage, And all the men and women merely players: They have their exits and their entrances; And one man in his time plays many parts.",
            "The robbed that smiles, steals something from the thief.",
            "Uneasy lies the head that wears the crown.",
            "All that glitters is not gold."]
            i = len(quotes) - 1
            quotechoice = random.randint(0, i)
            await message.channel.send(quotes[quotechoice])

        #Special
        #if (len(unPuncMessage) < 100):
            #quotes = ["fuck", "shit", "damn", "crap", "cunt", "bitch", "ass"]
            #i = len(quotes) - 1
            #quotechoice = random.randint(0, i)
            #await message.channel.send(quotes[quotechoice])

    #~~~ End of if statements ~~~

def setup(bot):
    bot.add_cog(Reaction(bot))