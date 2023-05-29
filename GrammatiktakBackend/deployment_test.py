from main import correct_input
from Utilities.utils import check_if_index_is_correct

print("This scripts checks for errors when using the corrector. \n This will not check for frontend errors.")

messages = [
    "jeg heder lucas. jeg har fødseldag idag",
    "En anden form for bias er confirmation bias, hvor man som forsker vægte undersøgelser som understøtte ens hypotse end undersøgelser som vil modsige ens hypotese. Det omfatter også, at hvis man har en vis forventning af et bestemt præparat virkning, at man i så fald også vil fortolke ens data på en måde som understøtter ens forventning. Confirmation bias kan også påvirke ens testpersoner, hvis man ikke er opmærksom på dette. Fx hvis man giver en testperson et præparat som testpersonen forventer har en effekt, vil dette kunne påvirke testpersonens opfattelse af stoffets virkning, på en måde som igen understøtter ens forventning. I det sidstnævnte eksempel er det placeboeffekten som vil kunne give patienten en fornemmelse af at præparatet virker selvom det ikke nødvendigvis er tilfældet. For at modvirker confirmation bias kan man foretage sig af blinding i tre forskellige grader. Ved almindelig blinding ved selve deltagerne i studiet ikke om de modtager den aktuelle behandling eller om de ikke gør, fx ved at give en kalkpille eller lign. Dette er med til at modvirke patientens egne forventninger til behandlingen. Dertil er der også dobbeltblinding hvor hverken patienten eller personalet ved om den behandling de får/giver er den faktiske behandling eller blot placebo. Dette er med til at modvirke at personalets forventning til behandlingen videregives ubevidst under kommunikation. Til sidst kan man også tripelblinde, der lægges til de to tidligere med at dem som behandlinger og analyser data fra studiet ikke ved hvilken gruppe som har modtaget den faktiske behandling. Disse tre former for blinding bidrager til at mindske mængden af confirmation bias mest muligt.",
    "min and spiser massere af rødbedesaft og den løbe popcorn",
    "Jeg bor i det hus, som den anden pige allerede har boet i.",
    "Jeg kan ikke lærer og cyklede det hele på en dag. Jeg lære dansk i skolen",
    "Så er vi tilbage på 0 på annotate. Jeg har sendt billeder af statistics. Jeg har også lavet en PE med nogle fixes, flere static filtre og evnen til at specificere om en person faller på videoen, sover og hvorvidt patienten har dyne på. Jeg kan vise mere i morgen. Er du på kontoret i morgen?",
]

for i, message in enumerate(messages):
    errors = correct_input(message)
    if not check_if_index_is_correct(errors, message, info=False):
        raise IndexError("Index is not correct for message {}".format(message))
    print("Indexes correct.")
    print(f"{i+1}/{len(messages)} done.")

print("SUCCESS")