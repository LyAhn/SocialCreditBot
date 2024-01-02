import sqlite3
import discord
from textblob import TextBlob

version = "0.2"

############################Test stuff#################################
with open('token.txt') as f:
    token = f.read()

keywords = []
with open('keywords.txt') as f:
    keywords = f.readlines()
    keywords = [x.strip() for x in keywords]



######################################################################

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    watching = discord.Activity(type=discord.ActivityType.watching, name="you! 🇨🇳")
    await client.change_presence(activity=watching)
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if any(keyword in message.content.lower() for keyword in keywords):
        blob = TextBlob(message.content)
        sentiment = blob.sentiment.polarity
        
        score = 0
        
        if sentiment > 0.5:
            score = 25
            await message.channel.send(f'Positive social credit score for {message.author.mention}! You have been given {score}. :red_envelope: :flag_cn:')
        elif sentiment > 0:
            score = 10
            await message.channel.send(f'Positive social credit score for {message.author.mention}! You have been given {score}.')
        elif sentiment < -0.5:
            score = -25
            await message.channel.send(f'Negative social credit score for {message.author.mention}! You have been deducted {score} points! ')
        elif sentiment < 0:
            score = -10
            await message.channel.send(f'Negative social credit score for {message.author.mention}! You have been deducted {score} points! ')

        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS scores (user_id INTEGER PRIMARY KEY, score INTEGER)')
        c.execute('SELECT score FROM scores WHERE user_id = ?', (message.author.id,))
        result = c.fetchone()
        if result is None:
            c.execute('INSERT INTO scores (user_id, score) VALUES (?, ?)', (message.author.id, score))
            result = (score,)
        else:
            c.execute('UPDATE scores SET score = ? WHERE user_id = ?', (result[0] + score, message.author.id))
        conn.commit()
        conn.close()

    if message.content.startswith('?score'):
        user = message.author
        if len(message.mentions) > 0:
            user = message.mentions[0]
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS scores (user_id INTEGER PRIMARY KEY, score INTEGER)')
        c.execute('SELECT score FROM scores WHERE user_id = ?', (user.id,))
        result = c.fetchone()
        if result is None:
            await message.channel.send(f':flag_cn: {user.mention} has not received a social credit score yet. :flag_cn:')
        else:
            await message.channel.send(f'{user.mention} has a social credit score of {result[0]}. :flag_cn:')

    if message.content.startswith('?help'):
        embed = discord.Embed(title='Social Credit Score Bot Help', description='Here are the available commands for the Social Credit Score Bot:', color=0xFF0000)
        embed.add_field(name='?score', value='Displays the social credit score of the user who sent the command. You can also mention another user to see their social credit score.', inline=False)
        embed.add_field(name='?help', value='Displays this help message.', inline=False)
        await message.channel.send(embed=embed)

client.run(token)
