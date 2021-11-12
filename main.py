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

def weekToDay(week,day):
    startDate = week[:week.find("/")]
    lstWeekDay = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
    month = week[week.find("/")+1:week.find(" ")]
    return str(int(startDate)+lstWeekDay.index(day))+"/"+month

class ListeDateView(nextcord.ui.View):

    def __init__(self,text,view,other):
        super().__init__()
        datesTable = [["8/11 - 14/11","15/11 - 21/11","22/11 - 28/11"],
                      ["29/11 - 5/12","6/12 - 12/12","13/12 - 19/12"],
                      ["20/12 - 26/12","27/12 - 2/01","3/12 - 9/01"]]
        for x in range(3):
            for y in range(3):
                self.add_item(ListeDate(x, y,datesTable[x][y],view,text,other))


class ListeDate(nextcord.ui.Button['ListeDateView']):
    def __init__(self, x, y, lbl,viewNext,text,other):
        super().__init__(style=nextcord.ButtonStyle.primary, label=lbl, row=y)
        self.x = x
        self.y = y
        self.text = text
        self.viewNext = viewNext
        self.other = other

    async def callback(self, interaction: nextcord.Interaction):
        value = self.label



        if self.viewNext == None:
            userDM = await interaction.user.create_dm()

            dictDispo = {"Lundi":[],"Mardi":[],"Mercredi":[],"Jeudi":[],"Vendredi":[],"Samedi":[],"Dimanche":[]}

            if DATA[str(interaction.user.id)][value]["trancheHoraires"] != None:
                for i in DATA[str(interaction.user.id)][value]["trancheHoraires"]:
                    dictDispo[i[:i.find(" ")]].append(i[i.find(" ")+1:])

                dispos = "\n".join(["- " + i + " ("+ ", ".join(dictDispo[i])+")" for i in dictDispo if len(dictDispo[i]) != 0])
            else:
                dispos = "\n".join(["- " + i + "(non précisé)" for i in DATA[str(interaction.user.id)][value]["day"]])



            await userDM.send(f"Voici la liste de tes disponibilités (semaine: {value}):\n{dispos}")
        elif self.other != None:


            await interaction.response.send_message(self.text.replace("{week}",value), view=self.viewNext(value,self.other), ephemeral=True)

        else:
            await interaction.response.send_message(self.text.replace("{week}",value), view=self.viewNext(value), ephemeral=True)



class HorairesDispo(nextcord.ui.Select):
    def __init__(self,user,days,week):

        self.week = week
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


        if DATA[str(interaction.user.id)][self.week]["trancheHoraires"] == None:
            DATA[str(interaction.user.id)][self.week]["trancheHoraires"] = self.values
        else:

            for tranche in self.values:

                if not(tranche in DATA[str(interaction.user.id)][self.week]["trancheHoraires"]):
                    DATA[str(interaction.user.id)][self.week]["trancheHoraires"] += [tranche]
            ajout = " ajoutées"




        dictDispo = {"Lundi":[],"Mardi":[],"Mercredi":[],"Jeudi":[],"Vendredi":[],"Samedi":[],"Dimanche":[]}


        for i in self.values:
            dictDispo[i[:i.find(" ")]].append(i[i.find(" ")+1:])
        dispos = "\n".join(["- " + i + " ("+ ", ".join(dictDispo[i])+")" for i in dictDispo if len(dictDispo[i]) != 0])


        dictDispoDay = {"Lundi":[],"Mardi":[],"Mercredi":[],"Jeudi":[],"Vendredi":[],"Samedi":[],"Dimanche":[]}


        for i in DATA[str(interaction.user.id)][self.week]["trancheHoraires"]:
            dictDispoDay[i[:i.find(" ")]].append(i[i.find(" ")+1:])

        for i in dictDispoDay:
            if len(dictDispoDay[i]) == 0 and i in DATA[str(interaction.user.id)][self.week]["day"]:
                DATA[str(interaction.user.id)][self.week]["day"].remove(i)



        await interaction.response.send_message(f'**Récapitulatif de tes disponibilités{ajout} pour la semaine du {self.week}:**\n{dispos}\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_',ephemeral=True)


class HorairesDispoView(nextcord.ui.View):
    def __init__(self,user,days,week):
        super().__init__()
        self.add_item(HorairesDispo(user,days,week))





class Dispo(nextcord.ui.Select):
    def __init__(self,week):
        self.week = week

        options = [
            nextcord.SelectOption(label='Lundi', description='Tu es disponible lundi '+weekToDay(week,"Lundi"), emoji='💰'),
            nextcord.SelectOption(label='Mardi', description='Tu es disponible mardi '+weekToDay(week,"Mardi"), emoji='💰'),
            nextcord.SelectOption(label='Mercredi', description='Tu es disponible mercredi '+weekToDay(week,"Mercredi"), emoji='💰'),
            nextcord.SelectOption(label='Jeudi', description='Tu es disponible jeudi '+weekToDay(week,"Jeudi"), emoji='💰'),
            nextcord.SelectOption(label='Vendredi', description='Tu es disponible vendredi '+weekToDay(week,"Vendredi"), emoji='💰'),
            nextcord.SelectOption(label='Samedi', description='Tu es disponible samedi '+weekToDay(week,"Samedi"), emoji='💰'),
            nextcord.SelectOption(label='Dimanche', description='Tu es disponible dimanche '+weekToDay(week,"Dimanche"), emoji='💰'),
            nextcord.SelectOption(label='Aucun', description="Tu n'es pas disponible cette semaine", emoji='❌')
        ]


        super().__init__(placeholder='Choisis tes disponibilités...', min_values=1, max_values=7, options=options)

    async def callback(self, interaction: nextcord.Interaction):


        ajout = ""

        if "Aucun" in self.values:
            if str(interaction.user.id) in DATA:
                DATA[str(interaction.user.id)][self.week] = {"day":["Aucun"],"trancheHoraires":None}
            else:
                DATA[str(interaction.user.id)] = {self.week:{"day":["Aucun"],"trancheHoraires":None}}


            listDispo = ["Aucun"]



            await interaction.response.send_message("Tu n'es pas disponible cette semaine.\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_",ephemeral=True)
        else:

            if str(interaction.user.id) in DATA and self.week in DATA[str(interaction.user.id)]:
                for day in self.values:
                    if not(day in DATA[str(interaction.user.id)][self.week]["day"]):
                        DATA[str(interaction.user.id)][self.week]["day"] += [day]
                ajout = " ajoutées"
            else:
                if str(interaction.user.id) in DATA:
                    DATA[str(interaction.user.id)][self.week] = {"day":self.values,"trancheHoraires":None}
                else:
                    DATA[str(interaction.user.id)] = {self.week:{"day":self.values,"trancheHoraires":None}}




            dispos = "\n".join(["- " + i for i in self.values])
            await interaction.response.send_message(f'**Récapitulatif de tes disponibilités{ajout}:**\n{dispos}\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_\n\nSélectionne maintenant les moments dans la journée où tu es disponible',view= HorairesDispoView(interaction.user, self.values, self.week), ephemeral=True)



class DispoView(nextcord.ui.View):
    def __init__(self,week):
        super().__init__()
        self.add_item(Dispo(week))




class Check(nextcord.ui.Select):
    def __init__(self,week,guild):
        #user = bot.get_user(i).display_name()

        self.week = week
        print("guild:",guild)
        options = [nextcord.SelectOption(label=getnames(guild,i), description="Voir les disponibilités de " + getnames(guild,i), emoji='✅') for i in DATA if week in DATA[i]]

        if len(options) == 0:
            options = [nextcord.SelectOption(label="Personne", description="Personne n'a répondu pour cette semaine", emoji='❌')]

        super().__init__(placeholder='Choisis la personne...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):


            if max([role in [i.name for i in interaction.user.roles] for role in ADMIN_ROLES]) or interaction.user.id == 514880859900215318:

                nickList = [(getnames(interaction.user.guild,i),i) for i in DATA]

                nickToID = {}

                for nick,id in nickList:
                    nickToID[nick] = id


                #dispos = "- "+"\n- ".join(DATA[nickToID[self.values[0]]])



                dictDispo = {"Lundi":[],"Mardi":[],"Mercredi":[],"Jeudi":[],"Vendredi":[],"Samedi":[],"Dimanche":[]}

                if DATA[nickToID[self.values[0]]][self.week]["trancheHoraires"] != None:
                    for i in DATA[nickToID[self.values[0]]][self.week]["trancheHoraires"]:
                        dictDispo[i[:i.find(" ")]].append(i[i.find(" ")+1:])
                    dispos = "\n".join(["- " + i + " ("+ ", ".join(dictDispo[i])+")" for i in dictDispo if len(dictDispo[i]) != 0])
                else:
                    dispos = "\n".join(["- " + i + " (non précisé)" for i in DATA[nickToID[self.values[0]]][self.week]["day"]])



                await interaction.response.send_message(f"**Voici la liste des disponibilités de {self.values[0]}**:\n{dispos}",ephemeral=True)
            else:
                await interaction.response.send_message("Tu n'as pas la permission de faire cela !",ephemeral=True)




class CheckView(nextcord.ui.View):
    def __init__(self,week,guild):
        super().__init__()
        self.add_item(Check(week,guild))


class CheckDay(nextcord.ui.Select):
    def __init__(self,week):
        self.week = week

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


            if max([role in [i.name for i in interaction.user.roles] for role in ADMIN_ROLES]) or interaction.user.id == 514880859900215318:

                membres = "\n".join(["- " + getnames(interaction.user.guild,id) + formatday(DATA[id][self.week]["trancheHoraires"],self.values[0]) for id in DATA if self.values[0] in DATA[id][self.week]["day"]])


                date = self.values[0] +" "+ weekToDay(self.week, self.values[0])

                await interaction.response.send_message(f'**Liste des personnes disponibles {date}:**\n{membres}\n\n_Seuls les personnes qui ont répondu au questionnaie seront visibles_',ephemeral=True)
            else:
                await interaction.response.send_message("Tu n'as pas la permission de faire cela !",ephemeral=True)




class CheckDayView(nextcord.ui.View):
    def __init__(self,week):
        super().__init__()
        self.add_item(CheckDay(week))

intents = nextcord.Intents.all()


bot = commands.Bot(command_prefix = "!",intents=intents)






class RemoveDispoSlot(nextcord.ui.Select):
    def __init__(self,user,values,week):
        self.week = week


        listdispo = [tranche for tranche in DATA[str(user.id)][week]["trancheHoraires"] if tranche[:tranche.find(" ")] in values]

        options = [nextcord.SelectOption(label=id, description='Clique pour supprimer cette disponibilité', emoji='❌') for id in listdispo]


        super().__init__(placeholder='Choisis les jours...', min_values=1, max_values=len(listdispo), options=options)

    async def callback(self, interaction: nextcord.Interaction):

            removedSlots = []
            toRemove = []
            for slot in self.values:
                if slot in DATA[str(interaction.user.id)][self.week]["trancheHoraires"]:
                    DATA[str(interaction.user.id)][self.week]["trancheHoraires"].remove(slot)
                    removedSlots.append(slot)

            print(DATA[str(interaction.user.id)][self.week])
            for day in DATA[str(interaction.user.id)][self.week]["day"]:
                check = True

                for i in DATA[str(interaction.user.id)][self.week]["trancheHoraires"]:
                    if i.find(day) > -1:
                        check = False
                print(day,check)
                if check:
                    toRemove += [day]

            for i in toRemove:
                DATA[str(interaction.user.id)][self.week]["day"].remove(i)
##
            if len(DATA[str(interaction.user.id)][self.week]["day"]) == 0:
                DATA[str(interaction.user.id)][self.week]["day"] = ["Aucun"]

            dispos = "\n".join(["- " + i for i in removedSlots])
            await interaction.response.send_message(f'**Récapitulatif des créneaux supprimés (semaine {self.week}):**\n{dispos}\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_', ephemeral=True)




class RemoveDispoSlotView(nextcord.ui.View):
    def __init__(self,user,values,week):
        super().__init__()
        self.add_item(RemoveDispoSlot(user,values,week))




class RemoveDispoDay(nextcord.ui.Select):
    def __init__(self,week):
        self.week = week
        options = [
            nextcord.SelectOption(label='Lundi', description='Supprimer lundi '+weekToDay(week,"Lundi"), emoji='❌'),
            nextcord.SelectOption(label='Mardi', description='Supprimer mardi '+weekToDay(week,"Mardi"), emoji='❌'),
            nextcord.SelectOption(label='Mercredi', description='Supprimer mercredi '+weekToDay(week,"Mercredi"), emoji='❌'),
            nextcord.SelectOption(label='Jeudi', description='Supprimer jeudi '+weekToDay(week,"Jeudi"), emoji='❌'),
            nextcord.SelectOption(label='Vendredi', description='Supprimer vendredi '+weekToDay(week,"Vendredi"), emoji='❌'),
            nextcord.SelectOption(label='Samedi', description='Supprimer samedi '+weekToDay(week,"Samedi"), emoji='❌'),
            nextcord.SelectOption(label='Dimanche', description='Supprimer dimanche '+weekToDay(week,"Dimanche"), emoji='❌')
        ]


        super().__init__(placeholder='Choisis les jours...', min_values=1, max_values=7, options=options)

    async def callback(self, interaction: nextcord.Interaction):

            removedDays = []

            for day in self.values:
                if day in DATA[str(interaction.user.id)][self.week]["day"]:
                    removedDays.append(day)



            dispos = "\n".join(["- " + i for i in removedDays])

            if len(removedDays) == 0:
                await interaction.response.send_message('Aucune disponibilité trouvée pour ce/ces jour(s)', ephemeral=True)
            else:
                await interaction.response.send_message(f'**Récapitulatif des jours sélectionnés (semaine {self.week}):**\n{dispos}\n\n_Si tu as fais une erreur tu peux séléctionner à nouveau_\n\nSélectionne maintenant les moments dans la journée où tu veux supprimer ta disponibilité',view= RemoveDispoSlotView(interaction.user,self.values,self.week), ephemeral=True)




class RemoveDispoDayView(nextcord.ui.View):
    def __init__(self,week):
        super().__init__()
        self.add_item(RemoveDispoDay(week))



@bot.command(aliases = ["cd"])
async def checkDay(ctx):
    if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]) or ctx.message.author.id == 514880859900215318:


        view2nd = CheckDayView
        view = ListeDateView("Sélectionne le jour dont tu veux connaitre les disponibilités des personnes",view2nd,None)

        await ctx.send("Sélectionne la semaine en question:", view=view)


@bot.command(aliases = ["cu"])
async def checkUser(ctx):
    if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]) or ctx.message.author.id == 514880859900215318:


        view2nd = CheckView

        view = ListeDateView("Sélectionne la personne dont tu veux connaitre les disponibilités pour la semaine du {week}\n_Seuls les personnes qui ont répondu au message sont visibles_",view2nd,ctx.guild)

        await ctx.send("Sélectionne la semaine en question:", view=view)



@bot.command(aliases = ["it"])
async def interim(ctx):


    view2nd = DispoView
    view = ListeDateView("Sélectionne ci dessous la liste des jours, où tu es disponible la semaine du {week} pour faire de l'intérim (si tu n'es pas disponible de la semaine clique sur 'aucun'", view2nd, None)

    await ctx.send("Sélectionne la semaine en question:", view=view)



@bot.command(aliases = ["itr"])
async def interimremove(ctx):

    view2nd = RemoveDispoDayView

    view = ListeDateView("Sélectionne ci dessous les jours de la semaine du {week}, dont tu veux supprimer des disponibilités (pour supprimer totalement un jour supprime tous les créneaux horaires de celui ci", view2nd, None)

    await ctx.send("Sélectionne la semaine en question:", view=view)




@bot.command(aliases = ["md"])
async def mesdispos(ctx,*param):
    message = ctx.message

    view = ListeDateView("Disponibilités envoyées", None, None)

    await ctx.send("Sélectionne la semaine en question:", view=view)








@bot.command()
async def data(ctx):
    message = ctx.message
    if max([role in [i.name for i in ctx.message.author.roles] for role in ADMIN_ROLES]) or ctx.message.author.id == 514880859900215318:
        file = open("DataDispo.txt","w+")
        jsonData = json.dumps(DATA)

        file.write(jsonData)
        file.close()
        await message.channel.send(file=nextcord.File("DataDispo.txt"))





bot.run("token")
