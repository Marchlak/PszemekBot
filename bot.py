import discord
from discord.ext import commands
from discord import app_commands
import bingo
from bingo import Bingo
import os


def run_discord_bot():
    bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())
    TOKEN='MTA4MjgzNTI3MjcxNjI3NTcyMg.G-_E0k.LLUCXAao-SOkg482sx9H1QRTN54rkLaBvXdjP0'
    last_open = {}

    @bot.event
    async def on_ready():
        print("Bot is Up and Ready!")
        try:
            synced = await bot.tree.sync()
            print (f"Synced {len (synced)} commands")
        except Exception as e:
            print(e)

    @bot.tree.command(name="help")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hey {interaction.user.mention}! to jest slashowa komenda")

    @bot.tree.command(name="create")
    @app_commands.describe(tittle="Tittle od the bingo", size="Size of bingo")
    async def create(interaction: discord.Interaction, tittle: str, size: int):
        new_bingo = Bingo(size,tittle,str(interaction.user.id))
        new_bingo.save_to_file()
        print(interaction.user.id)
        bingo.generate_image(new_bingo,size,str(interaction.user.id))
        await interaction.response.send_message(file=discord.File(os.path.join(str(interaction.user.id),"bingo.png")))

    @bot.tree.command(name="showall")
    async def showall(interaction: discord.Interaction):
        embed = discord.Embed(title="Twoje binga")
        files = os.listdir(str(interaction.user.id))
        for index,file in enumerate(files):
            if(str(file)!="bingo.png"):
                embed.add_field(name="",value=str(index)+ ". " + str(file)[:-5],inline=False)
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="open")
    @app_commands.describe(number="Bingo które chcesz edytować")
    async def open(interaction: discord.Interaction,number: int):
        if(find_next_json_file(str(interaction.user.id),number)is not None):
            last_open[interaction.user.id] = find_next_json_file(str(interaction.user.id),number)
            await interaction.response.send_message(find_next_json_file(str(interaction.user.id),number))
        else:
            await interaction.response.send_message("Nie ma bingo o takim numerze")

    @bot.tree.command(name="setcell")
    @app_commands.describe(row="Rząd",col="wiersz",cell="tekst w środku")
    async def setcell(interaction: discord.Interaction, row: int, col:int, cell:str):
        if interaction.user.id in last_open:
            temp_bingo= Bingo.load_from_file(str(last_open[interaction.user.id]),str(interaction.user.id))
            if(row-1>=0 and row-1<temp_bingo.get_size() and col-1>=0 and col-1<temp_bingo.get_size()):
                previous_word = temp_bingo.get_word(row-1,col-1)
                temp_bingo.set_word(row-1,col-1,cell)
                word = temp_bingo.get_word(row-1,col-1)
                if previous_word is None:
                    previous_word = "-"
                temp_bingo.save_to_file()
                await interaction.response.send_message(f"Hasło {previous_word} zostało zastąpione {word}")
            else:
                await interaction.response.send_message("Wiersz lub kolumna pozazakresem")
        else:
            await interaction.response.send_message("Żadne bingo nie jest otwarte")

    @bot.tree.command(name="show")
    async def show(interaction: discord.Interaction):
        if interaction.user.id in last_open:
            temp_bingo= Bingo.load_from_file(str(last_open[interaction.user.id]),str(interaction.user.id))
            bingo.generate_image(temp_bingo,temp_bingo.get_size(),str(interaction.user.id))
            print(str(interaction.user.id) + " " + str(last_open[interaction.user.id]))
            await interaction.response.send_message(file=discord.File(os.path.join(str(interaction.user.id),"bingo.png")))
        else:
            await interaction.response.send_message("Żadne bingo nie jest otwarte")


    bot.run(TOKEN)

def find_next_json_file(folder_path, num_files_to_skip):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    json_files.sort()
    if len(json_files) > num_files_to_skip:
        return json_files[num_files_to_skip]
    else:
        return None

