# This is my submission for CS50x 2020's Final Project: A Discord bot that is running indefinitely.

import discord
import os
import asyncio
from random import choice
from discord.ext import commands
from keep_alive import keep_alive

# TOKEN is a secret variable to hide our token from other people
my_secret = os.environ["TOKEN"]

# apparently this is better than client = discord.Client()
bot = commands.Bot("$")


# based on the difficulty chosen, grabs a random word from the corresponding text file
def get_word(difficulty):
    words = []
    with open(f"words/{difficulty}.txt") as f:
        words = f.read().splitlines()
    word = choice(words).lower()
    return word


# this is how we register an event
# discord.py is an asynchronous library, meaning things are done with callbacks
# a callback is a function that is called when something else happens
# this event is called when the bot gets initialized
@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


# event for when a bot receives a message
@bot.event
async def on_message(message):

    # if the author of the message is the bot, dont do anything
    if message.author == bot.user:
        return

    # let's say all commands start with $
    if message.content.startswith("$hello"):
        name = message.author.display_name
        await message.channel.send(f"Hello {name}, I am the Monokuma Bot!")

    if message.content.startswith("$play"):
        channel = message.channel
        author = message.author
        intro = discord.Embed(
            description=
            "**Monokuma wants to play a game of Hangman!**\n\nHurry up and choose the poor man's fate and get on with the game.\n\nOh, did I say fate? I meant the word difficulty! (Easy, Medium, Hard)",
            color=0xFFFFFF)
        intro.set_thumbnail(
            url="https://i.ibb.co/N1jc06m/monokuma-giggling.png")
        difficulty = await channel.send(embed=intro)

        # Users choose a difficulty by selecting a reaction
        # we can use the emojis by referencing this unicode name format)
        easy = "\N{Regional Indicator Symbol Letter E}"
        medium = "\N{Regional Indicator Symbol Letter M}"
        hard = "\N{Regional Indicator Symbol Letter H}"

        # this is how we add reactions to the message above
        await difficulty.add_reaction(easy)
        await difficulty.add_reaction(medium)
        await difficulty.add_reaction(hard)

        # hangman word to be guessed as a string
        hangman_word = None
        # letters of the word to be guessed
        letters = []
        # the hangman blanks printed when a letter has yet to be guessed
        blanks = []
        # a list of already (incorrectly) guessed letters
        guessed = []
        # used to determine if the user wins
        points = 0
        # no. of attempts the user has to guess the word
        attempts = 6

        # image urls to be used for the hangman game
        # i used img.bb to host my images since set_image can only take http urls
        imgs = [
            "https://i.ibb.co/x62F5CC/1.png", "https://i.ibb.co/R3jqbCZ/2.png",
            "https://i.ibb.co/3FR97k8/3.png", "https://i.ibb.co/kGvnp8t/4.png",
            "https://i.ibb.co/Vmj6tnz/5.png", "https://i.ibb.co/tzyHNr6/6.png",
            "https://i.ibb.co/BjJhyky/7.png"
        ]
        try:
            # bot waits for a reaction from the user and also saves the reaction they sent
            # function to check if for who sent the reaction and if the reaction they sent is part of the options the bot sent
            reaction, user = await bot.wait_for(
                "reaction_add",
                timeout=20.0,
                check=lambda reaction, user: user == author and str(
                    reaction.emoji) in [easy, medium, hard])
            # if the user's reaction matches the pre-selecteed emojis, pass the difficulty into get_word
            if str(reaction.emoji) == easy:
                hangman_word = get_word("easy")
            if str(reaction.emoji) == medium:
                hangman_word = get_word("medium")
            if str(reaction.emoji) == hard:
                hangman_word = get_word("hard")

            for letter in hangman_word:
                letters.append(letter)
                blanks.append("_")

        except asyncio.TimeoutError:
            # if user takes too long, send a message
            await channel.send(
                "You took too long to choose, just tell me when you want to play. Monokuma hates waiting!"
            )
        if hangman_word is not None:
            while True:
                # string of the hangman word during the game
                hangman_string = ""
                for blank in blanks:
                    # if the character in blank is "_", we need to add a backslash to escape it, since it's apparently a special character
                    if blank == "_":
                        hangman_string += "\\" + blank + " "
                    else:
                        hangman_string += blank + " "

                # we create an embed that will display the current game status
                # author.display_name makes it so that we can see who's hangman game is being shown
                status = discord.Embed(
                    title=f"{author.display_name}'s Hangman Game",
                    description=hangman_string,
                    color=0xFFFFFF)
                status.set_thumbnail(
                    url="https://i.ibb.co/2PDW6pS/monokuma-sitting.png")
                status.set_footer(
                    text="Type a letter/word to guess. $quit to stop playing.\n"
                )

                # depending on the user's remaining attempts, add the corresponding hangman picture to the embed
                status.set_image(url=imgs[attempts])
                # if user loses, set a different monokuma thumbnail
                if attempts == 0:
                    status.set_thumbnail(
                        url="https://i.ibb.co/PTyrGYP/monokuma-evil-laugh.png")

                # show the already guessed letters
                guesses = ""
                for guess in guessed:
                    guesses += guess + " "
                if guesses != "":
                    # add the incorrect guesses to the embed
                    status.add_field(name="Incorrect Guesses",
                                     value=guesses,
                                     inline=True)
                # show the player's remaining attempts by adding a field to the embed created earlier
                status.add_field(name="Remaining Attempts",
                                 value=attempts,
                                 inline=True)

                await channel.send(embed=status)

                # check if the user has won or lost before letting them guess (so we can get an updated game status right before winning/losing)
                # if the user runs out of attempts, they lose
                if attempts == 0:
                    await channel.send(
                        "Oops, too bad. You lost the game AND failed to save a life. How could you?"
                    )
                    await channel.send(
                        f"The correct answer was: {hangman_word}")
                    break

                # If the user has correctly guessed a number of letters equal to the length of the word, they win
                if points == len(hangman_word):
                    await channel.send(f"The correct answer is: {hangman_word}"
                                       )
                    await channel.send(
                        "Congratulations on keeping him alive... heeheehee...")
                    # special case for migs
                    if str(author) == "migs#2586":
                        olivia = discord.Embed(
                            description=
                            f"Olivia Hye, as requested by {author.display_name}",
                            color=0xFFFFFF)
                        olivia.set_image(
                            url="https://i.ibb.co/5jxg7Sv/olivia.jpg")
                        await channel.send(embed=olivia)
                    break

                # we wait for any response from the user
                guess = await bot.wait_for(
                    "message",
                    check=lambda m: m.channel == channel and m.author == author
                )
                # if user types $quit, quit the game, else send whatever they sent
                if guess.content.startswith("$quit"):
                    await channel.send("Quitting the game? Boooo!")
                    break
                elif not guess.content.isalpha():
                    await channel.send("Use letters ONLY!")
                    continue
                else:
                    await channel.send(f"Your guess is **{guess.content}**.")

                # if the user types the exact word fully, they win
                if guess.content.startswith(hangman_word):
                    await channel.send(f"The correct answer is: {hangman_word}"
                                       )
                    await channel.send(
                        "Congratulations on keeping him alive... heeheehee...")
                    # special case for migs
                    if str(author) == "migs#2586":
                        olivia = discord.Embed(
                            description=
                            f"Olivia Hye, as requested by {author.display_name}",
                            color=0xFFFFFF)
                        olivia.set_image(
                            url="https://i.ibb.co/5jxg7Sv/olivia.jpg")
                        await channel.send(embed=olivia)
                    break

                is_correct = False
                for letter in enumerate(letters):
                    # checks if the guessed letter is equal to the current letter
                    # we use .content to grab the content of the message that the user sent
                    if guess.content == letter[1]:
                        # however, if the user already correctly guessed the letter that is already in that position, go on to the next letter in the word
                        if guess.content == blanks[letter[0]]:
                            is_correct = True
                            continue
                        else:
                            blanks[letter[0]] = guess.content
                            is_correct = True
                            points += 1

                # if the user makes an incorrect guess, add it to the list of incorrect guesses and subtract an attempt
                if not is_correct:
                    await channel.send("**Incorrect!**")
                    guessed.append(guess.content)
                    attempts -= 1

    if message.content.startswith("$help!"):
        channel = message.channel

        help = discord.Embed(
            description=
            "**Do you REALLY need help with a bot as simple as me? Fine, since I'm just that kind.**",
            color=0xFFFFFF)
        help.set_thumbnail(
            url="https://i.ibb.co/4JG4vQQ/monokuma-blush-full.png")
        help.add_field(name="$hello",
                       value="Says hello to me, the Monokuma Bot!",
                       inline=False)
        help.add_field(
            name="$play",
            value=
            "Starts a game of Hangman! Each user can have their own instance of a Hangman game.",
            inline=False)
        help.add_field(
            name="$help!",
            value=
            "I think you know what this does by now. It brings up a list of possible commands for the Monokuma Bot!",
            inline=False)
        await channel.send(embed=help)


# this keeps our bot running constantly
keep_alive()
# command to run the discord bot
bot.run(my_secret)
