import yapper

bot = yapper.Bot()

@bot.command("test", "Test Command Until We Actually Code This")
def test(interaction):
    interaction.reply("Test Worked!")

bot.run()
