import json
import streamlit as st
from openai import AzureOpenAI
import prompturi

from dotenv import load_dotenv
import os

load_dotenv()

azure_endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("API_KEY")
api_version = os.getenv("API_VERSION")

client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=api_version
)

numar_intrebari = 6

def mesaj_chat(primul=False):
    if primul:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompturi.get_prompt_original(st.session_state.questions_deja_puse)}]
        )
    else:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompturi.get_prompt_original(st.session_state.questions_deja_puse)},
                      {"role": "user", "content": st.session_state.raspunsuri_deja_date[-1]}]
        )
    st.session_state.questions_deja_puse.append(response.choices[0].message.content)
    return response.choices[0].message.content

if "questions_deja_puse" not in st.session_state:
    st.session_state.questions_deja_puse = []
if "raspunsuri_deja_date" not in st.session_state:
    st.session_state.raspunsuri_deja_date = []

st.markdown("""
    <style>
    .stAppViewContainer {
        background-color: #FDDA0D;
    }
    
    .stMainBlockContainer {
        background: white;
        padding: 30px;
        border-radius: 25px;
        margin-top: 150px;
    }
    
    input[type="text"] {
        autocomplete: off;
    };
    .centered-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .centered-subtitle {
        text-align: center;
        font-size: 1.5rem;
        font-weight: normal;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="white-container">', unsafe_allow_html=True)

    st.markdown("<h1 class=\"centered-title\">Generatorul de Oferte Raiffeisen</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class=\"centered-subtitle\">Solutia perfecta pentru tine in cativa pasi</h2>", unsafe_allow_html=True)

    if "start" not in st.session_state:
        st.session_state.start = True
        question = mesaj_chat(primul=True)
        st.session_state.questions = [question]
        st.session_state.answers = []

    st.subheader("Te rugăm să răspunzi la următoarele întrebări:")
    for i, q in enumerate(st.session_state.questions):
        with st.expander(f"Întrebarea {i + 1}"):
            st.write(q)
            answer = st.text_input(f"Răspunsul tău pentru Întrebarea {i + 1}", key=f"answer_{i}", autocomplete="off")

            if answer and i == len(st.session_state.answers):
                st.session_state.answers.append(answer)
                st.session_state.raspunsuri_deja_date.append(answer)

                if len(st.session_state.answers) < numar_intrebari:
                    question = mesaj_chat()
                    st.session_state.questions.append(question)

    if len(st.session_state.answers) == numar_intrebari:
        st.success("Ai completat toate întrebările! Generăm oferta...")

        perechi_intrebare_raspuns = ""
        for i in range(numar_intrebari):
            perechi_intrebare_raspuns += f"Intrebarea este: {st.session_state.questions_deja_puse[i]}, iar raspunsul este: {st.session_state.raspunsuri_deja_date[i]}\n"
        prompt_generare_oferta = perechi_intrebare_raspuns
        prompt_generare_oferta += prompturi.get_prompt_recomandare()

        response_oferta = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system",
                       "content": "Esti un agent al bancii Raiffeisen si doresti sa vinzi o oferta personalizata clientului tau pe baza profilului utilizatorului"},
                      {"role": "user", "content": prompt_generare_oferta}]
        )
        not_cleaned_data = response_oferta.choices[0].message.content

        prompt_generare_profil = perechi_intrebare_raspuns
        prompt_generare_profil += prompturi.get_prompt_for_profile()
        response_profil = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system",
                       "content": "Esti un agent al bancii Raiffeisen si doresti sa faci profilul utilizatorului pe care tocmai l-ai interogat"},
                      {"role": "user", "content": prompt_generare_profil}]
        )
        print(f"Profilul candidatului cu care tocmai ai vorbit: \n {response_profil.choices[0].message.content}")
        c = not_cleaned_data.strip().removeprefix('```json').removesuffix('```').strip()
        data = json.loads(c)

        st.markdown("---")
        st.markdown(f"<h3><b>{data['mesaj']}</b></h3>", unsafe_allow_html=True)

        st.subheader("Cele mai bune opțiuni de card pentru tine")
        pachete = data["pachete"]
        cols = st.columns(2)
        for idx, col in enumerate(cols):
            with col:
                st.image(pachete[idx]["poza"], caption=pachete[idx]['nume_card'], use_container_width=True)
                st.markdown("### Beneficii:")
                for beneficiu in pachete[idx]['beneficii']:
                    st.write(f"- {beneficiu}")

        st.markdown("---")
        st.markdown(f"<h4 style='text-align: center; color: #4CAF50;'>{data['concluzie']}</h4>", unsafe_allow_html=True)

    else:
        st.info("Răspunde la toate întrebările pentru a genera oferta.")

    st.markdown('</div>', unsafe_allow_html=True)
