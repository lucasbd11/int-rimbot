import nextcord
from nextcord.ext import commands
import sqlite3
import json

"""
Bot discord pour avoir les disponibiltés des membres du serveur
Réalisé par Lucas
Version 1.2.0
"""

#creating sql file
conn = sqlite3.connect('membresDATA.db')
c = conn.cursor()


#creating sql db:
try:
    c.execute('''CREATE TABLE membresDATA
             (id text PRIMARY KEY,dispo text,heures int)''')
except:
    pass



ADMIN_ROLES = ["Respo Job"]

DATA = {}


def getnames(guild,id):
    nickName = guild.get_member(int(id)).nick
    name = guild.get_member(int(id)).name
    if nickName == None:
        return name
    else:
        return nickName

class HorairesDispo(nextcord.ui.Select):
    def __init__(self,user):


        options = []
        for day in DATA[str(user.id)]["day"]:
            for trancheHoraire in ["matin","après-midi","soir"]:
                if trancheHoraire == "matin":
                    options.append(nextcord.SelectOption(label=day+" "+trancheHoraire, description="Tu es disponible"+ day+" "+trancheHoraire, emoji='🌅'))
                elif trancheHoraire == "après-midi":
                    options.append(nextcord.SelectOption(label=day+" "+trancheHoraire, description="Tu es disponible"+ day+" "+trancheHoraire, emoji='☀'))
                else:
                    options.append(nextcord.SelectOption(label=day+" "+trancheHoraire, description="Tu es disponible"+ day+" "+trancheHoraire, emoji='🌕'))




        super().__init__(placeholder='Choisis tes disponibilités...', min_values=1, max_values=len(DATA[str(user.id)]["day"])*3, options=options)

    async def callback(self, interaction: nextcord.Interaction):



        DATA[str(interaction.user.id)]["trancheHoraires"] = self.values

        dictDispo = {"Lundi":[],"Mardi":[],"Mercredi":[],"Jeudi":[],"Vendredi":[],"Dimanche":[]}


        for i in self.values:
            dictDispo[i[:i.find(" ")]].append(i[i.find(" ")+1:])



        dispos = "\n".join(["- " + i + " ("+ ", ".join(dictDispo[i])+")" for i in dictDispo if len(dictDispo[i]) != 0])
        await interaction.response.send_message(f'**Récapitulatif de tes disponibilités:**\n{dispos}\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_',ephemeral=True)


class HorairesDispoView(nextcord.ui.View):
    def __init__(self,user):
        super().__init__()
        self.add_item(HorairesDispo(user))





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
            DATA[str(interaction.user.id)] = {"day":["Aucun"],"trancheHoraires":None}
            listDispo = ["Aucun"]



            await interaction.response.send_message("Tu n'es pas disponible cette semaine.\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_",ephemeral=True)
        else:
            DATA[str(interaction.user.id)] = {"day":self.values,"trancheHoraires":None}



            dispos = "\n".join(["- " + i for i in self.values])
            await interaction.response.send_message(f'**Récapitulatif de tes disponibilités:**\n{dispos}\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_\n\nSélectionne maintenant les moments dans la journée où tu es disponible',view= HorairesDispoView(interaction.user), ephemeral=True)
            #listDispo = self.values

        # try:
        #     c.execute("INSERT INTO membresDATA VALUES ('{0}','{1}','{2}')",format(str(interaction.user.id),json.dumps(listDispo),"0"))
        #     conn.commit()
        # except:
        #     c.execute("UPDATE membresDATA SET dispo = '{0}' WHERE id = '{1}';".format(json.dumps(listDispo),str(interaction.user.id)))
        #     conn.commit()



class DispoView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dispo())




class Check(nextcord.ui.Select):
    def __init__(self,guild):
        #user = bot.get_user(i).display_name()

        options = [nextcord.SelectOption(label=getnames(guild,i), description="Voir les disponibilités de " + getnames(guild,i), emoji='✅') for i in DATA]



        super().__init__(placeholder='Choisis la personne...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):


            if max([role in [i.name for i in interaction.user.roles] for role in ADMIN_ROLES]):

                nickList = [(getnames(interaction.user.guild,i),i) for i in DATA]

                nickToID = {}

                for nick,id in nickList:
                    nickToID[nick] = id


                #dispos = "- "+"\n- ".join(DATA[nickToID[self.values[0]]])



                dictDispo = {"Lundi":[],"Mardi":[],"Mercredi":[],"Jeudi":[],"Vendredi":[],"Dimanche":[]}

                for i in DATA[nickToID[self.values[0]]]["trancheHoraires"]:
                    dictDispo[i[:i.find(" ")]].append(i[i.find(" ")+1:])

                dispos = "\n".join(["- " + i + " ("+ ", ".join(dictDispo[i])+")" for i in dictDispo if len(dictDispo[i]) != 0])

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


            def formatday(lst,value):

                msg = " ("

                for tranche in lst:
                    if tranche.find(value) > -1:
                        msg += tranche[len(value)+1:]+", "
                msg = msg[:-2]+")"

                return msg


            if max([role in [i.name for i in interaction.user.roles] for role in ADMIN_ROLES]):

                membres = "\n".join(["- " + getnames(interaction.user.guild,id) + formatday(DATA[id]["trancheHoraires"],self.values[0]) for id in DATA if self.values[0] in DATA[id]["day"]])




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
            await ctx.message.delete()
            await ctx.send("Sélectionne la personne dont tu veux connaitre les disponibilités\n_Seuls les personnes qui ont répondu au message sont visibles_", view=view)



@bot.command(aliases = ["it"])
async def interim(ctx):

    if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]):
        view = DispoView()
        await ctx.message.delete()
        await ctx.send("Sélectionne ci dessous la liste des jours, où tu es disponible cette semaine pour faire de l'intérim (si tu n'es pas disponible de la semaine clique sur 'aucun'", view=view)


bot.run("TOKEN")
