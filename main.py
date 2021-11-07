import nextcord
from nextcord.ext import commands
#import sqlite3
import json

"""
Bot discord pour avoir les disponibiltés des membres du serveur
Réalisé par Lucas
Version 1.3.3
"""

#creating sql file
# conn = sqlite3.connect('membresDATA.db')
# c = conn.cursor()


#creating sql db:
# try:
#     c.execute('''CREATE TABLE membresDATA
#              (id text PRIMARY KEY,dispo text,heures int)''')
# except:
#     pass



ADMIN_ROLES = ["Respo Job"]

DATA = {}


try:
    file = open("DATA.txt","r")
    dataTxt = file.read()
    DATA = json.loads(dataTxt)
    file.close()
    print("ok")
except:
    print("pas ok")
    pass

def getnames(guild,id):
    try:
        nickName = guild.get_member(int(id)).nick
        name = guild.get_member(int(id)).name
        if nickName == None:
            return name
        else:
            return nickName
    except:
        return id

class HorairesDispo(nextcord.ui.Select):
    def __init__(self,user,days):


        options = []
        for day in days:
            for trancheHoraire in ["matin","après-midi","soir"]:
                if trancheHoraire == "matin":
                    options.append(nextcord.SelectOption(label=day+" "+trancheHoraire, description="Tu es disponible"+ day+" "+trancheHoraire, emoji='🌅'))
                elif trancheHoraire == "après-midi":
                    options.append(nextcord.SelectOption(label=day+" "+trancheHoraire, description="Tu es disponible"+ day+" "+trancheHoraire, emoji='☀'))
                else:
                    options.append(nextcord.SelectOption(label=day+" "+trancheHoraire, description="Tu es disponible"+ day+" "+trancheHoraire, emoji='🌕'))




        super().__init__(placeholder='Choisis tes disponibilités...', min_values=1, max_values=len(days)*3, options=options)

    async def callback(self, interaction: nextcord.Interaction):

        ajout = ""

        if DATA[str(interaction.user.id)]["trancheHoraires"] == None:
            DATA[str(interaction.user.id)]["trancheHoraires"] = self.values
        else:

            for tranche in self.values:

                if not(tranche in DATA[str(interaction.user.id)]["trancheHoraires"]):
                    DATA[str(interaction.user.id)]["trancheHoraires"] += [tranche]
            ajout = " ajoutées"




        dictDispo = {"Lundi":[],"Mardi":[],"Mercredi":[],"Jeudi":[],"Vendredi":[],"Samedi":[],"Dimanche":[]}


        for i in self.values:
            dictDispo[i[:i.find(" ")]].append(i[i.find(" ")+1:])
        dispos = "\n".join(["- " + i + " ("+ ", ".join(dictDispo[i])+")" for i in dictDispo if len(dictDispo[i]) != 0])


        dictDispoDay = {"Lundi":[],"Mardi":[],"Mercredi":[],"Jeudi":[],"Vendredi":[],"Samedi":[],"Dimanche":[]}


        for i in DATA[str(interaction.user.id)]["trancheHoraires"]:
            dictDispoDay[i[:i.find(" ")]].append(i[i.find(" ")+1:])

        for i in dictDispoDay:
            if len(dictDispoDay[i]) == 0 and i in DATA[str(interaction.user.id)]["day"]:
                DATA[str(interaction.user.id)]["day"].remove(i)



        await interaction.response.send_message(f'**Récapitulatif de tes disponibilités{ajout}:**\n{dispos}\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_',ephemeral=True)


class HorairesDispoView(nextcord.ui.View):
    def __init__(self,user,days):
        super().__init__()
        self.add_item(HorairesDispo(user,days))





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


        ajout = ""

        if "Aucun" in self.values:
            DATA[str(interaction.user.id)] = {"day":["Aucun"],"trancheHoraires":None}
            listDispo = ["Aucun"]



            await interaction.response.send_message("Tu n'es pas disponible cette semaine.\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_",ephemeral=True)
        else:

            if str(interaction.user.id) in DATA:
                for day in self.values:
                    if not(day in DATA[str(interaction.user.id)]["day"]):
                        DATA[str(interaction.user.id)]["day"] += [day]
                ajout = " ajoutées"
            else:
                DATA[str(interaction.user.id)] = {"day":self.values,"trancheHoraires":None}



            dispos = "\n".join(["- " + i for i in self.values])
            await interaction.response.send_message(f'**Récapitulatif de tes disponibilités{ajout}:**\n{dispos}\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_\n\nSélectionne maintenant les moments dans la journée où tu es disponible',view= HorairesDispoView(interaction.user,self.values), ephemeral=True)
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



                dictDispo = {"Lundi":[],"Mardi":[],"Mercredi":[],"Jeudi":[],"Vendredi":[],"Samedi":[],"Dimanche":[]}

                if DATA[nickToID[self.values[0]]]["trancheHoraires"] != None:
                    for i in DATA[nickToID[self.values[0]]]["trancheHoraires"]:
                        dictDispo[i[:i.find(" ")]].append(i[i.find(" ")+1:])
                    dispos = "\n".join(["- " + i + " ("+ ", ".join(dictDispo[i])+")" for i in dictDispo if len(dictDispo[i]) != 0])
                else:
                    dispos = "\n".join(["- " + i + " (non précisé)" for i in DATA[nickToID[self.values[0]]]["day"]])



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
                if lst != None:
                    msg = " ("

                    for tranche in lst:
                        if tranche.find(value) > -1:
                            msg += tranche[len(value)+1:]+", "
                    msg = msg[:-2]+")"

                    return msg
                else:
                    return "(non précisé)"


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






class RemoveDispoSlot(nextcord.ui.Select):
    def __init__(self,user,values):



        listdispo = [tranche for tranche in DATA[str(user.id)]["trancheHoraires"] if tranche[:tranche.find(" ")] in values]

        options = [nextcord.SelectOption(label=id, description='Clique pour supprimer cette disponibilité', emoji='❌') for id in listdispo]


        super().__init__(placeholder='Choisis les jours...', min_values=1, max_values=len(listdispo), options=options)

    async def callback(self, interaction: nextcord.Interaction):

            removedSlots = []
            toRemove = []
            for slot in self.values:
                if slot in DATA[str(interaction.user.id)]["trancheHoraires"]:
                    DATA[str(interaction.user.id)]["trancheHoraires"].remove(slot)
                    removedSlots.append(slot)

            print(DATA[str(interaction.user.id)])
            for day in DATA[str(interaction.user.id)]["day"]:
                check = True

                for i in DATA[str(interaction.user.id)]["trancheHoraires"]:
                    if i.find(day) > -1:
                        check = False
                print(day,check)
                if check:
                    toRemove += [day]

            for i in toRemove:
                DATA[str(interaction.user.id)]["day"].remove(i)



            dispos = "\n".join(["- " + i for i in removedSlots])
            await interaction.response.send_message(f'**Récapitulatif des créneaux supprimés:**\n{dispos}\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_', ephemeral=True)




class RemoveDispoSlotView(nextcord.ui.View):
    def __init__(self,user,values):
        super().__init__()
        self.add_item(RemoveDispoSlot(user,values))




class RemoveDispoDay(nextcord.ui.Select):
    def __init__(self):

        options = [
            nextcord.SelectOption(label='Lundi', description='Tu es disponible lundi', emoji='❌'),
            nextcord.SelectOption(label='Mardi', description='Tu es disponible mardi', emoji='❌'),
            nextcord.SelectOption(label='Mercredi', description='Tu es disponible mercredi', emoji='❌'),
            nextcord.SelectOption(label='Jeudi', description='Tu es disponible jeudi', emoji='❌'),
            nextcord.SelectOption(label='Vendredi', description='Tu es disponible vendredi', emoji='❌'),
            nextcord.SelectOption(label='Samedi', description='Tu es disponible samedi', emoji='❌'),
            nextcord.SelectOption(label='Dimanche', description='Tu es disponible dimanche', emoji='❌')
        ]


        super().__init__(placeholder='Choisis les jours...', min_values=1, max_values=7, options=options)

    async def callback(self, interaction: nextcord.Interaction):

            removedDays = []

            for day in self.values:
                if day in DATA[str(interaction.user.id)]["day"]:
                    removedDays.append(day)



            dispos = "\n".join(["- " + i for i in removedDays])

            if len(removedDays) == 0:
                await interaction.response.send_message('Aucune disponibilité trouvée pour ce/ces jour(s)', ephemeral=True)
            else:
                await interaction.response.send_message(f'**Récapitulatif des jours sélectionnés:**\n{dispos}\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_\n\nSélectionne maintenant les moments dans la journée où tu veux supprimer ta disponibilité',view= RemoveDispoSlotView(interaction.user,self.values), ephemeral=True)




class RemoveDispoDayView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(RemoveDispoDay())



@bot.command(aliases = ["cd"])
async def checkDay(ctx):
    if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]) or ctx.message.author.id == 514880859900215318:
        if DATA == {}:
            await ctx.send("Personne n'a encore répondu au questionnaire...")
        else:
            view = CheckDayView()
            #await ctx.message.delete()
            await ctx.send("Sélectionne le jour dont tu veux connaitre les disponibilités des personnes", view=view)


@bot.command(aliases = ["cu"])
async def checkUser(ctx):
    if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]) or ctx.message.author.id == 514880859900215318:
        if DATA == {}:
            await ctx.send("Personne n'a encore répondu au questionnaire...")
        else:
            view = CheckView(ctx.guild)
            await ctx.message.delete()
            await ctx.send("Sélectionne la personne dont tu veux connaitre les disponibilités\n_Seuls les personnes qui ont répondu au message sont visibles_", view=view)



@bot.command(aliases = ["it"])
async def interim(ctx):

    #if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]):
    view = DispoView()
    #await ctx.message.delete()
    await ctx.send("Sélectionne ci dessous la liste des jours, où tu es disponible cette semaine pour faire de l'intérim (si tu n'es pas disponible de la semaine clique sur 'aucun'", view=view)

@bot.command(aliases = ["itr"])
async def interimremove(ctx):

    #if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]):
    view = RemoveDispoDayView()
    #await ctx.message.delete()
    await ctx.send("Sélectionne ci dessous les jours dont tu veux supprimer des disponibilités (pour supprimer totalement un jour supprime tous les créneaux horaires de celui ci", view=view)



@bot.command(aliases = ["md"])
async def mesdispos(ctx,*param):
    message = ctx.message
    userDM = await message.author.create_dm()

    dictDispo = {"Lundi":[],"Mardi":[],"Mercredi":[],"Jeudi":[],"Vendredi":[],"Samedi":[],"Dimanche":[]}

    if DATA[str(ctx.author.id)]["trancheHoraires"] != None:
        for i in DATA[str(ctx.author.id)]["trancheHoraires"]:
            dictDispo[i[:i.find(" ")]].append(i[i.find(" ")+1:])

        dispos = "\n".join(["- " + i + " ("+ ", ".join(dictDispo[i])+")" for i in dictDispo if len(dictDispo[i]) != 0])
    else:
        dispos = "\n".join(["- " + i + "(non précisé)" for i in DATA[str(ctx.author.id)]["day"]])



    await userDM.send(f"Voici la liste de tes disponibilités:\n{dispos}")




@bot.command()
async def data(ctx):
    message = ctx.message
    if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]) or ctx.message.author.id == 514880859900215318:
        file = open("DataDispo.txt","w+")
        jsonData = json.dumps(DATA)

        file.write(jsonData)
        file.close()
        await message.channel.send(file=nextcord.File("DataDispo.txt"))




bot.run("TOKEN") 
