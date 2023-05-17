import os
import pandas as pd
from flask import Flask, request, render_template
import time
import re

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")

df1 = pd.read_csv("nutids_r.csv", encoding="UTF-8", sep=",", header=None, names=["wrong", "correct"])
df2 = pd.read_csv("EuroparlNutidsr_testset.csv", encoding="UTF-8", sep=";")
lines = [
    "Bæredygtig mode er et vigtigt emne i dagens samfund. Med øget fokus på miljøbevidsthed og et ønske om at mindske vores påvirkning af planeten, søger mange mennesker alternativer til traditionel modeindustri. Bæredygtig mode handler om at producere tøj på en måde, der tager hensyn til miljøet, arbejdsforholdene og dyrevelfærd.",
    "I dag er der flere bæredygtige modebrands, der tilbyder produkter fremstillet af genanvendte materialer, økologisk dyrkede fibre og fair trade-principper. Disse brands stræber efter at minimere deres CO2-aftryk og reducere affald ved at bruge genbrugte materialer og implementere cirkulære produktionsmetoder.",
    "Forbrugerne spiller også en vigtig rolle i bæredygtig mode. Mange mennesker vælger at købe brugt tøj, reparere og genbruge deres garderobe og være mere bevidste om deres forbrugsvaner. Der er også en stigende tendens til at vælge tidløse stykker af høj kvalitet frem for hurtig mode, der hurtigt går af mode.",
    "Bæredygtig mode er ikke kun en trend, men en nødvendighed i vores stræben efter at bevare planeten. Ved at støtte bæredygtige modebrands og træffe bevidste valg som forbrugere kan vi bidrage til at skabe en mere bæredygtig fremtid.",
    "En sund livsstil og motion er afgørende for vores fysiske og mentale velvære. I dagens moderne samfund, hvor mange mennesker fører en stillesiddende livsstil og er udsat for stress, er det vigtigt at finde tid til at prioritere motion og sundhed.",
    'Regelmæssig fysisk aktivitet har mange fordele. Det styrker vores hjerte og kredsløbssystem, forbedrer vores muskelstyrke og udholdenhed og hjælper med at opretholde en sund kropsvægt. Motion frigiver også endorfiner, som er kroppens naturlige "lykkehormoner", der kan hjælpe med at reducere stress og forbedre vores humør.',
    'Der er mange forskellige former for motion, som man kan vælge imellem. Nogle foretrækker at dyrke sport som løb, cykling eller svømning, mens andre foretrækker mere afslappende aktiviteter som yoga eller vandreture. Det vigtigste er at finde en form for motion, der passer til ens egen smag og behov.',
    'En sund livsstil handler ikke kun om motion, men også om at spise en balanceret kost og få tilstrækkelig hvile og søvn. Det er vigtigt at have sunde spisevaner og spise en varieret kost rig på frugt, grøntsager, fuldkorn og magert protein.',
    'Digitaliseringen har haft en betydelig indvirkning på vores samfund og har ændret måden, vi arbejder på. I dagens moderne arbejdsmarked er digitale færdigheder og teknologisk kompetence afgørende for succes.',
    'Digitaliseringen har gjort det muligt for os at arbejde mere effektivt og fleksibelt. Vi har adgang til avancerede værktøjer og teknologier, der hjælper os med at automatisere opgaver, kommunikere hurtigt og effektivt samt få adgang til information og ressourcer på et øjeblik.',
    'Samtidig har digitaliseringen også medført ændringer i jobmarkedet. Nogle traditionelle jobfunktioner er blevet automatiseret, hvilket har krævet, at arbejdstagere opgraderer deres færdigheder og tilpasser sig til nye jobroller. Evnen til at lære og tilpasse sig nye teknologier bliver stadig vigtigere i fremtidens arbejdsmarked.',
    'Samtidig åbner digitaliseringen også nye muligheder. Vi ser fremkomsten af nye job inden for teknologi og digitale industrier, som kræver specialiserede færdigheder som dataanalyse, kunstig intelligens og softwareudvikling. Disse job kan være både givende og lukrative for dem, der har den nødvendige ekspertise.',
    'Det er også vigtigt at nævne, at digitaliseringen har ændret måden, vi arbejder på. Fjernarbejde og digitale samarbejdsværktøjer er blevet mere udbredt, hvilket har gjort det muligt for mennesker at arbejde på tværs af geografiske grænser og have mere fleksibilitet i deres arbejdsliv.',
    'I fremtiden vil digitaliseringen sandsynligvis fortsætte med at påvirke vores arbejdsmarked. Det er afgørende, at vi fortsætter med at udvikle vores digitale færdigheder og være åbne for læring og tilpasning for at forblive relevante og konkurrencedygtige i det digitale tidsalder.',
    'I dagens samfund er spørgsmålet om skrald og innovation blevet stadig mere presserende. Med befolkningens vækst og øget forbrug står vi over for store udfordringer i forhold til håndtering og bortskaffelse af affald. Heldigvis er der også en stigende bevægelse mod innovative løsninger, der kan tackle disse problemer og skabe en mere bæredygtig fremtid.',
    'Skrald er blevet et globalt problem, der påvirker vores miljø og økosystemer negativt. Plastikforurening fylder vores have, floder og verdenshavene, og affaldsdeponier bidrager til luftforurening og jordforurening. Traditionelle metoder til affaldshåndtering, såsom deponering og forbrænding, er ikke længere holdbare på lang sigt. Derfor er der behov for innovativ tænkning og handling for at reducere, genbruge og genanvende affaldet.',
    'Inden for affaldsinnovation er der flere spændende fremskridt. Et eksempel er udviklingen af ​​biologisk nedbrydelige materialer og emballage. Disse materialer er designet til at nedbrydes naturligt og reducere den langsigtede belastning på miljøet. Der er også fokus på at udvikle mere effektive og bæredygtige genbrugs- og genanvendelsesmetoder. Avanceret teknologi som robotter og automatisering bruges til at sortere og genanvende affald mere præcist og effektivt.',
    'Desuden er der en stigende interesse for at fremme cirkulær økonomi, hvor affald bliver til ressourcer. Dette indebærer at skabe et system, hvor produkter og materialer genanvendes, repareres eller genbruges i stedet for at ende som affald. Virksomheder og iværksættere spiller en vigtig rolle i denne proces ved at udvikle innovative forretningsmodeller og produkter, der fremmer bæredygtighed og affaldsminimering.',
    'Et eksempel på affaldsinnovation er udviklingen af ​​genanvendelige emballageløsninger, der reducerer behovet for engangsplastik. Der er også initiativer til at omdanne organisk affald til biogas eller kompost, hvilket bidrager til både energiproduktion og jordforbedring. Desuden ser vi en stigning i genbrug af materialer som glas, papir og metal, hvilket sparer ressourcer og reducerer miljøpåvirkningen.',
    'Ud over teknologiske fremskridt er der også en bevægelse hen imod ændring af vores forbrugsvaner og adfærd. Mange mennesker bliver mere opmærksomme på deres affaldsaftryk og træffer bevidste valg for at reducere det.',
    'Esport er blevet en globalt anerkendt og voksende industri, der fusionerer konkurrence, teknologi og underholdning. Det har skabt en ny form for sportsverden, hvor professionelle spillere konkurrerer i videospil på internationalt niveau. Esport er ikke længere blot en hobby, men en legitim karrierevej for mange passionerede spillere.',
    'Esport er præget af en bred vifte af videospilsgenrer, herunder skydespil, strategispil, MOBA (Multiplayer Online Battle Arena) og mange flere. Spillene spilles ofte på pc, konsoller eller endda mobile enheder. Turneringer og konkurrencer arrangeres regelmæssigt både online og offline, hvor hold eller individuelle spillere kæmper om store præmiepenge og anerkendelse.',
    'En af de mest bemærkelsesværdige træk ved esport er dets globale appel og tiltrækning af millioner af seere og fans over hele verden. Store esportbegivenheder strømmes live på internettet og tiltrækker publikum i form af både fysiske tilskuere og online seere. Dette har skabt en enorm efterspørgsel efter esport-relateret indhold, herunder streaming, kommentering, analyser og esportsnyheder.',
    'Esport er ikke kun et fænomen blandt unge. Det tiltrækker et bredt spektrum af mennesker, uanset alder, køn eller baggrund. Det har også vist sig at have potentialet til at forene mennesker på tværs af kulturer og nationaliteter, da spillere fra forskellige lande konkurrerer og samarbejder i teams.',
    'Foruden den konkurrencemæssige side af esport er der også en stigende professionalisering af industrien som helhed. Der er esportsorganisationer og hold, der ansætter trænere, analytikere og supportpersonale for at optimere spillernes præstationer. Desuden har sponsorer og investorer vist interesse for esport og investerer i teams og begivenheder for at drage fordel af den voksende popularitet.',
    'Esport har også en indflydelse på den teknologiske udvikling. Det har bidraget til fremkomsten af ​​avanceret gamingudstyr, streamingplatforme, esports-specifikke software og endda virtuel virkelighed. Den teknologiske udvikling inden for esport påvirker også den bredere gamingindustri og inspirerer nye innovationer.',
    'I fremtiden forventes esport at fortsætte med at vokse og blive endnu mere mainstream. Det vil sandsynligvis være en integreret del af underholdningsindustrien, med flere tv-transmissioner, større sponsoraftaler og en bredere accept i samfundet. Esport vil fortsat være en dynamisk og spændende arena, hvor talenter kan blomstre, og hvor gamingkulturen kan trives.'
    'I hjertet af en travl by, hvor lyden af ​​biler, mennesker og byliv flettes sammen, findes en skjult oase af ro og skønhed. Det er en park, der strækker sig over store grønne områder, med træer, blomsterbede og velplejede stier. Parken er et fristed, hvor folk kan slippe væk fra hverdagens hektiske tempo og finde fred og fornyelse i naturen.',
    'Når man træder ind i parken, bliver man straks mødt af duften af ​​friske blomster og lyden af ​​fuglesang. Solens stråler filtreres gennem trækronerne og skaber et spil af lys og skygge på græsplænen. Børn leger og griner på legepladsen, mens familier slapper af på tæpper og nyder en picnic frokost.',
    'Gåture langs parkens stier er en sand fornøjelse. Det er som at træde ind i en anden verden, hvor stress og bekymringer forsvinder. Man kan beundre de farverige blomsterbede, hvor blomster af alle slags blomstrer i fuldt flor. Bier summer rundt, og sommerfugle danser elegant mellem blomsterne.',
    'Parkens sø er en attraktion i sig selv. Den er fyldt med liv, med ænder og svaner, der svømmer roligt i vandet. Der er små både til udlejning, så man kan sejle en tur og nyde den beroligende følelse af at være omgivet af vand og natur.',
    'I parkens hjerte finder man et hyggeligt caféområde. Her kan man sidde ved udendørs borde og nyde en kop varm kaffe eller en forfriskende iste. Folk chatter og griner, mens de nyder deres drikkevarer og snacks. Det er det perfekte sted at mødes med venner eller bare sidde alene og reflektere over livets små øjeblikke.',
    'Parken er også et populært sted for motion og aktiviteter. Løbere træner deres udholdenhed på stierne, yogaentusiaster finder et roligt hjørne til deres praksis, og sportsentusiaster samles på boldbanerne for at spille fodbold eller basketball. Parken er et levende sted, hvor folk kommer sammen for at dyrke deres lidenskaber og nyde godt af det sunde udendørsliv.',
    'Uanset om man er på udkig efter en stille stund alene, en sjov dag med familien eller bare en pause fra byens larm, er parken det perfekte sted at finde det. Den tilbyder en verden af ​​muligheder og skaber minder, der varer ved. Så næste gang du har brug for en pause, gå ind i parken, ånd dybt og lad naturens skønhed omfavne dig.'
]

df = pd.concat([df1, df2], ignore_index=True)
wrong_text_not_splitted = list(df["wrong"].values) + lines
correct_text_not_splitted = list(df["correct"].values) + lines

wrong_text = []
correct_text = []

for text in wrong_text_not_splitted:
    sentences = re.split(r'(?<=[a-zA-Z])\.', text)
    wrong_text += [sentence.strip() for sentence in sentences if sentence.strip()]

for text in correct_text_not_splitted:
    sentences = re.split(r'(?<=[a-zA-Z])\.', text)
    correct_text += [sentence.strip() for sentence in sentences if sentence.strip()]

wrong_text = [x for x in wrong_text if len(x) > 0]
correct_text = [x for x in correct_text if len(x) > 0]

print(len(wrong_text), len(correct_text))

for i in range(len(wrong_text_not_splitted)):
    wrong_text.append

app = Flask(__name__)
app.secret_key = 'super secret key'
start_time = time.time()
prev_text = None

df = pd.read_csv('nutids-r-reviewed.csv', sep="|")

wrong_reviewed = list(df["wrong"].values)
correct_reviewed = list(df["correct"].values)

def update_progress(wrong, correct):
    print("Updating...")
    df = pd.DataFrame(zip(wrong, correct), columns=["wrong", "correct"])
    df.to_csv('nutids-r-reviewed.csv', index=False, sep="|")

text_index = 326

def get_text():
    global text_index
    print("Review index now at: " + str(text_index))
    text_index += 1
    #if wrong_text[text_index] == correct_text[text_index]: 
    #    return get_text()
    return wrong_text[text_index], correct_text[text_index]

@app.route('/', methods=['GET', 'POST'])
def index():
    global wrong_text, correct_text, prev_text

    if request.method == 'POST':
        wrong_reviewed.append(request.form['wrong_text'])
        correct_reviewed.append(request.form['correct_text'])
        update_progress(wrong_reviewed, correct_reviewed)

    wrong, correct = get_text()

    return render_template('index.html', text1=wrong.strip().capitalize(), text2=correct.strip().capitalize())

if __name__ == '__main__':
    app.run()

