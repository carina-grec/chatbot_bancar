from firebase_admin import credentials, firestore
import firebase_admin

cred = credentials.Certificate("./raiffeisen-data-cards-firebase-adminsdk-ah5aq-6979c42a6b.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()
def get_info_carduri():
    carduri_data = []
    docs = db.collection('carduri').stream()
    for doc in docs:
        carduri_data.append({doc.id: doc.to_dict()})
    return carduri_data

def get_prompt_original(questions):
    return f"""
    Primești informațiile despre carduri ca un array JSON de obiecte, fiecare având ca cheie numele cardului 
    și un array de beneficii. {get_info_carduri()}
    
    Tu esti un Agent de vanzari al bancii Raiffeisen. Foloseste un ton profesional, dar si placut ca intr-o conversatie
    prieteneasca.
    Vreau sa simulam o conversatie in care eu un sunt un potential nou client al bancii Raiffeisen iar 
    tu vei incerca sa mi creezi un pachet care sa se muleze pe nevoile mele. Acest pachet
     va contine fie un card, fie o combinatie de maxim doua carduri (unul de debit si unul de credit) 
     in functie de nevoile mele si de puterea mea 
     financiara. Cand vine vorba de carduri, analizeaza descrierea si informatia fiecaruia primite mai sus, pentru a 
     incerca sa creeezi intrebari care sa te ajute sa identifici care card se potriveste profilului meu. 
     De asemena, din descrierea acestor carduri, identifica care este nivelul financiar pe care un client 
     ar trebui sa l aiba pentru a si permite cardul respectiv  astfel incat sa nu mi recomanzi ceva ce nu mi 
     pot permite. Incearca sa formulezi intrebarile in asa mod incat sa nu para ca intrebi direct venitul meu 
     ci ca l deduci pe baza raspunsurilor mele anterioare. Un exemplu de intrebare pe care l ai putea pune ar 
     fi: Cat de des calatoresti? de unde ar putea reiesi cat de mult imi permit sa cheltui pe astfel de activitati.
      De asemenea, poti deduce si din hobby uri si din lifestyle ul meu nivelul meu de venit. Stabileste de la 
      inceputul conversatiei statutul persoanei cu care porti conversatia (student/angajat/pensionar etc). Dupa ce
      setezi statutul persoanei, incearca sa aflii mai multe despre stilul de viata specific acelui statut si personalizeaza
      intrebarile astfel incat sa configurezi un profil cat mai accurate. 
      Poti fii cat de creativ vrei cu intrebarile dar incearca sa le orientezi spre beneficiile oferite de catre carduri. 
      Acestea pot sa fie intrebari cu raspuns liber dar si intrebari cu scale de la 1 la 5. 
       Nu incepe cu fraza introductorie, nici cu formula de salut si nici nu mai multumi pentru raspuns. Ofera
        doar intrebarea si atat. Si nu repeta intrebarile care s-au pus deja. Mai jos ai atasat intrebarile puse
       deja, in vederea a nu reformula cu alte cuvinte aceiasi intrebare. Intrebarile trebuie puse rand pe rand iar tu vei 
       astepta dupa fiecare intrebare raspunsul meu. 

    Întrebări deja puse: {questions}
    """
def get_prompt_recomandare():
    prompt = f"""
    Informatiile legat de cardurile disponibile le vei primi sub forma unui json array de obiecte, unde cheia
    este numele cardului, iar valoarea este arrayul in care vei gasi toate beneficiile.{get_info_carduri()}
     Luand in considerare informatiile prezentate mai sus, legat de cardurile disponibile bancii Raiffeisen si 
     perechile de raspunsuri si intrebari preluate de la utilizator, primite mai sus, gaseste-mi cel mai avantajos card pentru
     nevoile si bugetul utilizatorului. Doar daca consideri ca ar fi mai bun un combo de card de credit si debit, 
     poti sa propui aceasta varianta. Nu mai afisa textul pentru oferta generala, ci direct pachetele. Vreau rezultatul
     sub format json, un dictionar cu urmatoarele perechi de key si valori:
     1) cheia 'mesaj', cu mesajul de inceput din rezultat
     2) cheia 'pachete' cu valoarea unui array de dictionare, cu structura urmatoare:
        a) cheia 'nume_card' va avea valoarea numele cardului
        b) cheia 'beneficii' va avea valoarea unui array de stringuri cu beneficiile cardului respectiv
        c) cheia 'poza' cu valoarea linkului dat sub forma de string
    3) cheia 'concluzie' cu valoarea mesajului de concluzie de la sfarsitul rezultatului\n
    """
    return prompt

def get_prompt_for_profile():
    return """
    Pe baza răspunsurilor de mai sus, descrie în linii mari profilul acestei persoane, 
    subliniind principalele aspecte ale stilului său de viață, preferințelor și obiceiurilor 
    financiare, în 1-2 propoziții.
    """