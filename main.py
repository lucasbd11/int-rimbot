import nextcord
from nextcord.ext import commands

"""
Bot discord pour avoir les disponibiltés des membres du serveur
Réalisé par Lucas
Version 1.0.0
"""

ADMIN_ROLES = ["Respo Job"]

DATA = {}


class Dispo(nextcord.ui.Select):
    def __init__(self):


        options = [
            nextcord.SelectOption(label='Lundi', description='Tu es disponible lundi', emoji='💰'),
            nextcord.SelectOption(label='Mardi', description='Tu es disponible mardi', emoji='💰'),
            nextcord.SelectOption(label='Mercredi', description='Tu es disponible mercredi', emoji='💰'),
            nextcord.SelectOption(label='Jeudi', description='Tu es disponible jeudi', emoji='💰'),
            nextcord.SelectOption(label='Vendredi', description='Tu es disponible vendredi', emoji='💰'),
            nextcord.SelectOption(label='Samedi', description='Tu es disponible samedi', emoji='💰'),
            nextcord.SelectOption(label='Dimanche', description='Tu es disponible dimanche', emoji='💰'),
            nextcord.SelectOption(label='Aucun', description="Tu n'es pas disponible cette semaine", emoji='❌')
        ]


        super().__init__(placeholder='Choisis tes disponibilités...', min_values=1, max_values=7, options=options)

    async def callback(self, interaction: nextcord.Interaction):


        if "Aucun" in self.values:
            DATA[str(interaction.user.id)] = ["Aucun"]
            await interaction.response.send_message("Tu n'es pas disponible cette semaine.\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_",ephemeral=True)
        else:
            DATA[str(interaction.user.id)] = self.values
            dispos = "\n".join(["- " + i for i in self.values])
            await interaction.response.send_message(f'**Récapitulatif de tes disponibilités:**\n{dispos}\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_',ephemeral=True)


class DispoView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dispo())


bot = commands.Bot(command_prefix='!')

class Check(nextcord.ui.Select):
    def __init__(self,guild):
        #user = bot.get_user(i).display_name()

        options = [nextcord.SelectOption(label=guild.get_member(int(i)).nick, description="Voir les disponibilités de " + guild.get_member(int(i)).nick, emoji='✅') for i in DATA]



        super().__init__(placeholder='Choisis la personne...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):


            if max([role in [i.name for i in interaction.user.roles] for role in ADMIN_ROLES]):

                nickList = [(interaction.user.guild.get_member(int(i)).nick,i) for i in DATA]

                nickToID = {}

                for nick,id in nickList:
                    nickToID[nick] = id


                dispos = "- "+"\n- ".join(DATA[nickToID[self.values[0]]])

                await interaction.response.send_message(f"**Voici la liste des disponibilités de {self.values[0]}**:\n{dispos}",ephemeral=True)
            else:
                await interaction.response.send_message("Tu n'as pas la permission de faire cela !",ephemeral=True)




class CheckView(nextcord.ui.View):
    def __init__(self,guild):
        super().__init__()
        self.add_item(Check(guild))


class CheckDay(nextcord.ui.Select):
    def __init__(self):


        options = [
            nextcord.SelectOption(label='Lundi', description='Voir les disponibilités lundi', emoji='✅'),
            nextcord.SelectOption(label='Mardi', description='Voir les disponibilités mardi', emoji='✅'),
            nextcord.SelectOption(label='Mercredi', description='Voir les disponibilités mercredi', emoji='✅'),
            nextcord.SelectOption(label='Jeudi', description='Voir les disponibilités jeudi', emoji='✅'),
            nextcord.SelectOption(label='Vendredi', description='Voir les disponibilités vendredi', emoji='✅'),
            nextcord.SelectOption(label='Samedi', description='Voir les disponibilités samedi', emoji='✅'),
            nextcord.SelectOption(label='Dimanche', description='Voir les disponibilités dimanche', emoji='✅')
        ]


        super().__init__(placeholder='Choisis la journée...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):

            if max([role in [i.name for i in interaction.user.roles] for role in ADMIN_ROLES]):
                membres = "\n".join(["- " + interaction.user.guild.get_member(int(id)).nick for id in DATA if self.values[0] in DATA[id]])
                await interaction.response.send_message(f'**Liste des personnes disponibles {self.values[0]}:**\n{membres}\n\n_Seuls les personnes qui ont répondu au questionnaie seront visibles_',ephemeral=True)
            else:
                await interaction.response.send_message("Tu n'as pas la permission de faire cela !",ephemeral=True)




class CheckDayView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(CheckDay())

intents = nextcord.Intents.all()


bot = commands.Bot(command_prefix = "!",intents=intents)




@bot.command(aliases = ["cd"])
async def checkDay(ctx):
    if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]):
        if DATA == {}:
            await ctx.send("Personne n'a encore répondu au questionnaire...")
        else:
            view = CheckDayView()
            #await ctx.message.delete()
            await ctx.send("Sélectionne le jour dont tu veux connaitre les disponibilités des personnes", view=view)


@bot.command(aliases = ["cu"])
async def checkUser(ctx):
    if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]):
        if DATA == {}:
            await ctx.send("Personne n'a encore répondu au questionnaire...")
        else:
            view = CheckView(ctx.guild)
            #await ctx.message.delete()
            await ctx.send("Sélectionne la personne dont tu veux connaitre les disponibilités\n_Seuls les personnes qui ont répondu au message sont visibles_", view=view)





@bot.command(aliases = ["it"])
async def interim(ctx):

    if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]):
        view = DispoView()
        await ctx.message.delete()
        await ctx.send("Sélectionne ci dessous la liste des jours, où tu es disponible cette semaine pour faire de l'intérim (si tu n'es pas disponible de la semaine clique sur 'aucun'", view=view)


bot.run("TOKEN")
