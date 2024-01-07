import sqlite3
import discord
import time
import logging
from operator import itemgetter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#from textblob import TextBlob

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

logger.info("Bot started...")
analyzer = SentimentIntensityAnalyzer()
version = "0.3"
banned_words = {}


with open('roles.txt') as f:
    role_name = f.read().strip()

with open('token.txt') as f:
    token = f.read()

print("Before: ", banned_words)
with open('banned.txt') as f:
    banned_words = f.read().strip()
print("After: ", banned_words)


keywords = []
with open('keywords.txt') as f:
    keywords = f.readlines()
    keywords = [x.strip() for x in keywords]

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    watching = discord.Activity(type=discord.ActivityType.watching, name="you! 🇨🇳")
    await client.change_presence(activity=watching)
    


    min_words = 5
    
    def check_min_length(message):
        if message.content.startswith('?'):
            return True
        
        words = message.content.split()
        if len(words) < min_words:
            return False
    
    
@client.event
async def on_message(message):
    server_id = message.guild.id
    
    
    
    if message.author == client.user:
        return
       
        
    if message.content.startswith('?version'):
        await message.channel.send(f'Version: {version}')
        
    if message.content.startswith('?ping'):
        await display_ping(message)         
        
    # Leaderboard command
    if message.content.startswith('?board'):
        await display_leaderboard(message)
        

        
    # def check_min_length(message):
    #     if len(message.content.split()) < min_words:
    #             return False
    #     else:
    #             return True
    # if not check_min_length(message):
    #     return     
        
    if any(keyword in message.content.lower() for keyword in keywords):
        # blob = TextBlob(message.content)
        # sentiment = blob.sentiment.polarity
        
        if any(banned_word in message.content.lower() for banned_word in banned_words):
  # send message and return 
            await message.channel.send(f'CCP Message for User: {message.author.mention}! We have detected Social Credit Score Manipulation.')
            return
        
        word_count = len(message.content.split())
        length_multiplier = word_count / 50
        score = analyzer.polarity_scores(message.content)
        sentiment = int(score['compound'] * 100)
        weighted_sent = sentiment * length_multiplier
        scaled_score = weighted_sent * 2
        if -0.1 < sentiment < 0.1:
            scaled_score = 0
        
        if scaled_score > 7:
            score = 30
            await message.channel.send(f'CCP Message for User: {message.author.mention}! China Appreciation Detected. {score} Credit Points have been added to your Government Profile :red_envelope: :flag_cn:')
        
        elif scaled_score > 5:
            score = 15
            await message.channel.send(f'CCP Message for User: {message.author.mention}! China Appreciation Detected. {score} Credit Points have been added to your Government Profile :red_envelope: :flag_cn:')
        elif scaled_score > 0.2:
            score = 2
            await message.channel.send(f'CCP Message for User: {message.author.mention}! China Appreciation Detected. {score} Credit Points have been added to your Government Profile :red_envelope: :flag_cn:')
        elif scaled_score < -7:
            score = -75
            await message.channel.send(f'CCP Message for User: {message.author.mention}! We have detected improper behaviour! You have been deducted {score} points! ')
        elif scaled_score < -4:
            score = -25
            await message.channel.send(f'CCP Message for User: {message.author.mention}! We have detected improper behaviour! You have been deducted {score} points! ')
        elif scaled_score < 0:
            score = -5
            await message.channel.send(f'CCP Message for User: {message.author.mention}! We have detected improper behaviour! You have been deducted {score} points! ')
        
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS scores (server_id INTEGER, user_id INTEGER, score INTEGER, PRIMARY KEY(server_id, user_id))')
        c.execute('SELECT score FROM scores WHERE server_id = ? AND user_id = ?', (server_id, message.author.id,))
        result = c.fetchone()
        if result is None:
            c.execute('INSERT INTO scores (server_id, user_id, score) VALUES (?, ?, ?)', (server_id, message.author.id, score))
            result = (score,)
        else:
            c.execute('UPDATE scores SET score = ? WHERE server_id = ? AND user_id = ?', (result[0] + score, server_id, message.author.id))
        conn.commit()
        conn.close()

    if message.content.startswith('?give'):
        
        # Check author permissions
        if role_name not in [role.name for role in message.author.roles]:
            return await message.channel.send(':raised_hand::octagonal_sign: This is a CCP command! :flag_cn: :raised_hand::octagonal_sign: ')
        else:
        # Check if user is mentioned
            user = message.mentions[0]
        amount = int(message.content.split()[-1])
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute("UPDATE scores SET score = score + ? WHERE server_id = ? AND user_id = ?", (amount, server_id, user.id,))
        conn.commit()
        conn.close()

        await message.channel.send(f"The CCP has awarded {user.mention} {amount} Social Credit Score!")
        
    if message.content.startswith('?take'):
        if role_name not in [role.name for role in message.author.roles]:
            return await message.channel.send(':raised_hand::octagonal_sign: This is a CCP command! :flag_cn: :raised_hand::octagonal_sign: ')
        user = message.mentions[0]
        amount = int(message.content.split()[-1])
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute("UPDATE scores SET score = score - ? WHERE server_id = ? AND user_id = ?", (amount, server_id, user.id))
        conn.commit()
        conn.close()
        await message.channel.send(f"The CCP has deducted {user.mention} {amount} Social Credit Score!")
        
    if message.content.startswith('?reset'):
        if role_name not in [role.name for role in message.author.roles]:
            return await message.channel.send(':raised_hand::octagonal_sign: This is a CCP command! :flag_cn: :raised_hand::octagonal_sign: ')
        user = message.mentions[0]
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute("UPDATE scores SET score = 0 WHERE server_id = ? AND user_id = ?",(server_id, user.id))
        conn.commit()
        conn.close()
        await message.channel.send(f"The CCP has reset {user.mention} Social Credit Score!")
        
    if message.content.startswith('?set'):
        if role_name not in [role.name for role in message.author.roles]:
            return await message.channel.send(':raised_hand::octagonal_sign: This is a CCP command! :flag_cn: :raised_hand::octagonal_sign: ')
        else:
            user = message.mentions[0]
        amount = int(message.content.split()[-1])
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute("UPDATE scores SET score = ? WHERE server_id = ? AND user_id = ?", (amount, server_id, user.id))
        await message.channel.send(f"The CCP has set {user.mention} Social Credit Score to {amount}!")
        conn.commit()
        conn.close()
        
    elif message.content.startswith('?score'):
        user = message.author
        if len(message.mentions) > 0:
            user = message.mentions[0]
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS scores (server_id INTEGER, user_id INTEGER, score INTEGER, PRIMARY KEY(server_id, user_id))')
        c.execute('SELECT score FROM scores WHERE server_id = ? AND user_id = ?', (server_id, user.id,))
        result = c.fetchone()
        if result is None:
            await message.channel.send(f':flag_cn: {user.mention} has not received a social credit score yet. :flag_cn:')
        else:
            await message.channel.send(f'{user.mention} has a social credit score of {int(result[0])}. :flag_cn:')

    if message.content.startswith('?help'):
        embed = discord.Embed(title='Social Credit Score Bot Help', description='Here are the available commands for the Social Credit Score Bot:', color=0xFF0000)
        embed.add_field(name='?score', value='Displays the social credit score of the user who sent the command. You can also mention another user to see their social credit score.', inline=False)
        embed.add_field(name='?help', value='Displays this help message.', inline=False)
        embed.add_field(name='?board', value='Displays the leaderboard of the users with the highest social credit scores.', inline=False)
        embed.add_field(name='?give', value='Gives a mentioned user a specified amount of social credit score. You must have the required role to use this command.', inline=False)
        embed.add_field(name='?take', value='Takes a mentioned user a specified amount of social credit score. You must have the required role to use this command.', inline=False)
        embed.add_field(name='?reset', value='Resets the social credit score of a mentioned user. You must have the required role to use this command.', inline=False)
        embed.add_field(name='?set', value='Sets the social credit score of a mentioned user to a specified amount. You must have the required role to use this command.', inline=False)
        embed.add_field(name='?ping', value='Displays the latency of the bot.', inline=False)
        embed.add_field(name='Version', value=(version), inline=True)
        await message.channel.send(embed=embed)

## PING COMMAND ##
async def display_ping(message):
            await message.channel.send(f'Pong! {round(client.latency * 1000)}ms')

## LEADERBOARD CODE ##        
    # Define leaderboard function
async def display_leaderboard(message):
  # Connect to database
  conn = sqlite3.connect('scores.db')  
  c = conn.cursor()
    # Get current server id
  server_id = message.guild.id
  # Query all scores
  c.execute("SELECT user_id, score FROM scores WHERE server_id = ? ORDER BY score DESC", (server_id,))
  # Fetch results 
  results = c.fetchall()
  # Create embed message
  embed = discord.Embed(title="Social Credit Leaderboard")
  # Add fields for each result
  for pos, result in enumerate(results[:10]):
    user_id = result[0]
    score = result[1]
    user = client.get_user(user_id)
    color = 0xFF0000 #if pos <3 else 0x00FF00
    emoji = "🥇" if pos==0 else "🥈" if pos==1 else "🥉" if pos==2 else ""
    embed.add_field(name=f"#{pos+1} {emoji}", value=f"{user} : {score:>10.0f}")
    embed.color = color

  # Send embed message
  await message.channel.send(embed=embed)

# Close connection
  conn.close()
  
  ## END OF LEADERBOARD CODE ##


client.run(token)
