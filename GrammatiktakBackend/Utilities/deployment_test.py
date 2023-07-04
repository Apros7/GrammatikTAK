from Utilities.utils import check_if_index_is_correct
import numpy as np
import time

def test_deployment(correct_input, manual_check=False, start_at=0):

    print("This script checks for errors when using the corrector. \n This will not check for frontend errors.")

    messages = [
        "hej jeg hedder lucas. hej jeg hedder  lucas. hej jeg hedder      lucas.",
        "imorgen skal jeg i skole i morgen",
        "imorgen kan jeg aller bedst lide bananer ala carte",
        "jeg jeg har har et et sødt sødt hund hund",
        "Hvordan har du det? Det går godt her.",
        "Hey. Jeg håber, at du nyder weekenden :smile:. Jeg har endelig fået lavet et fix til edit detection til web-anno. Jeg har lavet en PR med det. Hvis du vil approve og restarte serveren, så skal jeg nok nå så mange reviews, som jeg kan i løbet af i dag og i morgen.",
        "den hus er rigtig stor. Rigtig mange glæde sig til at ser og inviterer familie og venner.",
        "Dertil er der også dobbeltblinding hvor hverken patienten eller personalet ved om den behandling de får/giver er den faktiske behandling eller blot placebo. Jeg ved godt at jeg burde vide det.",
        "Her bruges billedsprog til at sammenligne det lyriske jeg med træerne. Det lyriske jeg spejler sig altså i træerne, idet han forestiller sig sine hænder som grene. Forestillingen om, at træerne næsten ikke kan nå hinanden med deres grene, kan altså overføres på det lyriske jeg. Måske har det lyriske jeg selv svært ved at nå nogen. Måske føler det lyriske jeg, at han ikke kan nå kærligheden. Måske føler det lyriske jeg, at han glider væk fra en elsket. Netop denne ide, hvor naturen bruges som en analogi til mennesket selv, fremsættes i den danske litteraturhistoriker Erik Skyum-Nielsens artikel ”Nu er det tid til naturdigte”. Her forklarer han, at ”så snart en digter beskrev og besang naturen, kom digtet også altid til at handle om digteren selv. I den forstand fungerer naturen uundgåeligt som menneskets spejl.” Netop pga. Erik Skyum-Nielsens baggrund som lektor på institut for Nordiske Studier og Sprogvidenskab på Københavns Universitet kan denne betragtning ses som troværdig. Naturen i digte er altså en måde, hvorpå digteren indirekte kan reflektere og skrive om sig selv.",
        "Jeg kigger op og ser solens første svage stråler, som titter frem mellem bøgetræerne og varmer den kolde jord. De første spæde og grønne blade pynter på bøgetræernes ellers nøgne grene. Skoven er som et eventyr, hvor fuglene synger med på forårets melodi. Solens stråler varmer mine kinder, og jeg mærker, hvordan lyset og den positive energi gennemstrømmer min krop. Det er som om, at vinterens mørke og kulde forlader mig med et dybt suk. Mine tanker ledes hen på naturens store betydning for ikke blot mig, men for mange mennesker her på jorden. Specielt i digte kan man finde mange afskygninger af naturens rolle i livet hos mennesker. Der findes netop mange digtere, som i tidens løb har skrevet og reflekteret over naturen. Nogen kan spejle sig eller finde en del af sig selv i naturen. Andre finder måske en ensomhed i naturens store pragt. Det får mig til at undres, for hvorfor opstilles naturen som motiv i mange digte? Hvilken betydning har naturen for mennesket, og hvordan kommer dette til udtryk i digte?",
        "Det er som om, at vinterens mørke og kulde forlader mig med et dybt suk.",
        "min and spiser massere af rødbedesaft og den løbe popcorn",
        "Super sejt, Simon Gaarde💪💪💪. Vi ved du kæmper til tårerne triller og hvor meget du giver afkald på, for at nå dine mål i vandet - du skal være SÅ stolt🇩🇰🇩🇰🇩🇰. Jeg kan godt lide danske gulerødder 💪💪🚀",
        "Træner teamet Mathilde Pugholm Hvid, Nichlas Fonnesbech & Bastian Løve Høegh - Jeg tror ikke helt I ved, hvor KÆMPE en forskel I gør - TUSIND TAK🙏🙏.",
        "Jeg håber ikke, at du skulle vente så lang tid på, at den blev færdig.",
        "idag har jeg fødseldag. Jeg har fødselsdag idag",
        "9 mennesker boede på en gammel ø.. De havde en god ven",
        "jeg jeg har en stor hus. jeg går på silkeborg silkeborg gymnasium. Jeg har et stor hus. Jeg har en stort hund.",
        "jeg jeg har en met til skole",
        " håber du har en god dag på silkeborg gymnasium. Har du en god dag? Har en god dag. Har du haft en god dag? Har du spist en banan? Håber du hygger.",
        "Hej jeg hedder lucas. Jeg havde engang en hund. Den har jeg ikke mere. Den er nu i Silkeborg. Jeg går på Silkeborg Gymnasium.",
        "jeg heder lucas. jeg har fødseldag idag  ",
        "jeg kører 30 km/t",
        "håber du har en god  dag på silkeborg silkeborg gymnasium",
        "jeg jeg ser en action film fra fra blockbuster. Så så jeg en film. Lars Lars har det godt. Jeg er fra fra fra silkeborg. Jeg har skole imorgen. Jeg er er er er er",
        "Jeg skal på arbejde d. 9. august 2022.",
        "Jeg har et rigtig rigtig hurtig ven",
        "Jeg kan ikke lærer og cykler det hele på en dag. Jeg lære dansk i skolen",
        "En anden form for bias er confirmation bias, hvor man som forsker vægte undersøgelser som understøtte ens hypotse end undersøgelser som vil modsige ens hypotese. Det omfatter også, at hvis man har en vis forventning af et bestemt præparat virkning, at man i så fald også vil fortolke ens data på en måde som understøtter ens forventning. Confirmation bias kan også påvirke ens testpersoner, hvis man ikke er opmærksom på dette. Fx hvis man giver en testperson et præparat som testpersonen forventer har en effekt, vil dette kunne påvirke testpersonens opfattelse af stoffets virkning, på en måde som igen understøtter ens forventning. I det sidstnævnte eksempel er det placeboeffekten som vil kunne give patienten en fornemmelse af at præparatet virker selvom det ikke nødvendigvis er tilfældet. For at modvirker confirmation bias kan man foretage sig af blinding i tre forskellige grader. Ved almindelig blinding ved selve deltagerne i studiet ikke om de modtager den aktuelle behandling eller om de ikke gør, fx ved at give en kalkpille eller lign. Dette er med til at modvirke patientens egne forventninger til behandlingen. Dertil er der også dobbeltblinding hvor hverken patienten eller personalet ved om den behandling de får/giver er den faktiske behandling eller blot placebo. Dette er med til at modvirke at personalets forventning til behandlingen videregives ubevidst under kommunikation. Til sidst kan man også tripelblinde, der lægges til de to tidligere med at dem som behandlinger og analyser data fra studiet ikke ved hvilken gruppe som har modtaget den faktiske behandling. Disse tre former for blinding bidrager til at mindske mængden af confirmation bias mest muligt.",
        "min and spiser massere af rødbedesaft og den løbe popcorn",
        "Jeg bor i det hus, som den anden pige  allerede har boet i.",
        "Jeg kan ikke lærer og cyklede det hele på en dag. Jeg lære dansk i skolen",
        "Så er vi tilbage på 0 på annotate. Jeg har sendt billeder af statistics. Jeg har også lavet en PE med nogle fixes, flere static filtre og evnen til at specificere om en person faller på videoen, sover og hvorvidt patienten har dyne på. Jeg kan vise mere i morgen. Er du på kontoret i morgen?",
    ]

    ## TO TEST MANUALLY IN WEBPAGE:
    message_web = [
        "hey Christian<br>tak for Det. Jeg er desværre I skole til, kl 18, så det har Lucas ikke mulighed for.<br>Jeg håber, at i får en dejlig aften :smile:.",
        "hey Christian<br>håber du har en god dag på silkeborg silkeborg gymnasium"
    ]

    average_time_per_word = []

    for i in range(start_at, len(messages)-1):
        start_time = time.time()
        message = messages[i]
        print(f"Correcting this message nr. {i}: ", f"\"{message}\"")
        errors = correct_input(message)
        average_time_per_word.append((time.time() - start_time)/len(message.split()))
        if manual_check:
            print("MESSAGE: ", message)
            print("Errors: ", *errors, sep="\n")
            input_statement = input("Enter to continue, q to quit")
            if input_statement == "q":
                raise KeyboardInterrupt
        if not check_if_index_is_correct(errors, message, info=False):
            print("MESSAGE: ", message)
            print("Errors: ", *errors, sep="\n")
            check_if_index_is_correct(errors, message)
            raise IndexError(f"Index is not correct for message {message}")
        for j in range(len(errors)):
            for k in range(len(errors)):
                if j == k: continue
                j_indexes = errors[j][2]
                k_indexes = errors[k][2]
                if j_indexes[0] == k_indexes[0] or j_indexes[1] == k_indexes[1]: 
                    print(f"Index {j} and {k} are the same:")
                    print("Error[j] = ", errors[j])
                    print("Error[k] = ", errors[k])

        # Should also display if some word is corrected by multiple correctors ie. index[0] == index[0] or index[1] == index[1]
        print(f"{i+1}/{len(messages)} done.")
    print("Indexes correct.\n")
    print("Average time per word: ", round(np.mean(average_time_per_word), 5), " sec/word.")
    print("Than means: ", round(1/round(np.mean(average_time_per_word), 5), 2), "word/min.")

    print("\n\n## SUCCESS ##\n\n")

    print("You should check these manully on the webpage:")
    print("\n", *message_web, "\n", sep="\n")