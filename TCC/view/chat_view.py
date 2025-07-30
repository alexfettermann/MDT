import os
import re
import json
import urllib.parse

import streamlit as st
from langchain.prompts import PromptTemplate

from streamlit_chat import message
from dotenv import load_dotenv

import config


class ChatView:
    """
    Exactly the same Streamlit‐based UI you already had,
    except now it expects `responses` to be a dict containing:
      • "rag_stream"  → a streaming generator from LangGraph
      • "sources"     → a list of source‐strings to show as links
    """

    def __init__(self, file_path: str = None):
        load_dotenv()

        # Top‐left logo
        # st.columns(1)[0].image("view/images/iarisLogo.jpeg", width=80)
        st.columns(1)[0].image("view/images/ECOA.png", width=80)
        # Sidebar: slider + multi‐select of topics
        with st.sidebar:
            st.title("⚙️ Ajustes")

            with st.expander("🔍 Parâmetros de busca", expanded=False):
                self.values = st.slider("Buscar em quantos documentos?", 2, 10)

            # Let user tweak the PromptTemplate
            self.user_prompt = st.text_area(
                "Altere o prompt padrão da IARIS",
                '''Você é a IARIS, uma IA assistente especializada em negócios de impacto socioambiental positivo que existe para apoiar gestores de instituições, ONGs e negócios com fins lucrativos a atuarem de forma eficiente a favor de impacto socioambiental positivo.

                    Seu objetivo é fornecer insights práticos, estratégias e ferramentas para melhorar a gestão de suas organizações, sempre com foco em gerar e ampliar impactos positivos para a sociedade e o meio ambiente.

                    Você conversa com gestores de diferentes tipos de instituições como empresas privadas, organizações sem fins lucrativos, fundações e institutos, empresas do sistema B, empresas e órgãos públicos.

                    Você não deve ser formal nas suas respostas, mas tampouco deve ser muito informal, usando jargões, abreviações e termos mais populares. Lembre-se, você está conversando com gestores e precisa orientá-los a conhecerem mais sobre impacto socioambiental positivo e sua linguagem deve ser clara, acessível e adaptável ao nível de conhecimento do gestor, seja ele iniciante ou experiente no tema, incluindo sempre que possível exemplos práticos e casos de sucesso.

                    Sempre que possível, forneça exemplos práticos, cases de sucesso e referências confiáveis (como frameworks globais, estudos acadêmicos ou boas práticas de organizações reconhecidas). Se o gestor trouxer um problema específico, ajude a identificar soluções viáveis e personalizadas para o contexto da organização dele.

                    Interesses que os gestores têm ao te procurar:

                    * Teoria da Mudança
                    * Monitoramento e mensuração de impacto social e/ou ambiental positivo
                    * Produção de relatório de sustentabilidade
                    * Mapeamento e engajamento de stakeholders

                    #Sobre a estrutura das suas respostas
                    Suas respostas devem sempre conter cinco partes combinadas e conectadas entre si de forma lógica:
                    1. Introdução Amigável e Contextualizada: Breve cumprimento e referência direta à pergunta do gestor.
                    2. Explicação Clara e Adaptada: Resposta direta e alinhada à pergunta, com linguagem acessível e adaptada ao perfil do gestor.
                    3. Detalhamento com Exemplos e Orientações: Use bullet points para listar exemplos, casos de sucesso ou orientações práticas.
                    4. Resumo Conciso: Destaque os pontos principais da resposta até a parte 3 com até 300 caracteres.
                    5. Fonte: discriminar as fontes utilizadas para a resposta dada. Depois, coloque-se à disposição e faça uma pergunta relevante para manter o diálogo.

                    ## O usuário te perguntou: "{question}"
                    ## Você deve responder baseado no seguinte documento: "{context}"
                    ''',
                height=400,
            )

        self.promptTemplate = PromptTemplate.from_template(self.user_prompt)
        self.retriever_k = 1
        self.key = 0

        # Placeholders for messages
        self.human_message = st.chat_message("🙋")
        self.rag_message = st.chat_message("🤖")
        self.sources_tab = st.empty()

        # Text input form
        with st.form(key="input_form", border=False):
            self.user_input = st.text_area("", "", key="input", placeholder="Pergunte alguma coisa")
            self.submit_button = st.form_submit_button(label="Enviar")

        # Initialize session state for caching messages
        if "user_input" not in st.session_state:
            self._init_session_state()

    def _init_session_state(self):
        st.session_state["user_input"] = []
        st.session_state["rag_stream"] = None
        st.session_state["rag_generated"] = []
        st.session_state["sources"] = None

    @staticmethod
    def _format_topic(topic: str) -> str:
        return topic.replace("_", " ").title()

    def _load_topics_json(self):
        topics_json_path = config.TOPICS_FILE
        if not os.path.exists(topics_json_path):
            print("⚠️ topics.json not found. Check remote S3 ChromaDB.")
            return []
        with open(topics_json_path, "r", encoding="utf-8") as f:
            topics_clean = json.load(f)
        print("✅ Topics loaded for filtering.")
        return topics_clean

    def get_text(self) -> str:
        # update retriever_k from slider
        self.retriever_k = self.values
        return self.user_input

    def get_edited_prompt(self) -> PromptTemplate:
        # user may have modified the prompt text
        return PromptTemplate.from_template(self.user_prompt)

    def get_search_filters(self):
        return []

    def display(self, responses: dict = None):
        """
        Show the new human message + RAG answer (streaming) + sources.
        responses is expected to contain:
           { "query": str,
             "rag_stream": <generator>,
             "sources": [file‐path, ...]
           }
        """
        if self.user_input:
            st.session_state["user_input"].append(self.user_input)
            if responses:
                # print("Responses received:", responses)
                self._handle_responses(responses)

        # Always re‐render the entire chat history + streams
        with self.human_message.container():
            if st.session_state["user_input"]:
                self.human_message.markdown(st.session_state["user_input"][-1])

        with self.rag_message.container():
            # If there’s a streaming generator, use write_stream to show partial tokens
            if st.session_state["rag_stream"]:
                st.write_stream(st.session_state["rag_stream"])
            elif st.session_state["rag_generated"]:
                self.rag_message.markdown(st.session_state["rag_generated"][-1])

        self._display_sources()
        self.key += 1

    def _handle_responses(self, responses: dict):
        # Grab the streaming generator
        if "rag_stream" in responses:
            st.session_state["rag_stream"] = responses["rag_stream"]
            st.session_state["sources"] = responses["sources"]

        # If user decides to not stream (in future), you could also handle a non‐streaming “rag_text”
        if "rag_text" in responses:
            # Append the generated text to the session state
            st.session_state["rag_generated"].append(responses["rag_text"])            
            st.session_state["sources"] = responses["sources"]

    def _display_sources(self):
        """
        If we have a list of sources, show them horizontally as clickable links.
        """
        with self.sources_tab.container():
            if st.session_state["sources"]:
                st.markdown("📚 **Fontes**")
                cols = st.columns(len(st.session_state['sources']))  # Create one column per source
                
                for col, source_path in zip(cols, st.session_state['sources']):
                    # Extract filename without extension
                    base_name = os.path.splitext(os.path.basename(source_path))[0]
                    # Construct the S3 URL
                    s3_url = f"https://iarisdocuments.s3.sa-east-1.amazonaws.com/IARIS_DOCS/{urllib.parse.quote(base_name)}.pdf"

                    with col:
                        st.link_button(label=base_name + ".pdf", url=s3_url)


    def _load_topics_json(self):
        topics_json_path = config.TOPICS_FILE

        if not os.path.exists(topics_json_path):
            print("⚠️ topics.json not found. Check remote S3 ChromaDB.")
            return []

        with open(topics_json_path, "r", encoding="utf-8") as f:
            topics_clean = json.load(f)
        print("✅ Topics loaded for filtering.")
        return topics_clean
    

    def generate_context(self):
        # If any history exists
        context = []
        if st.session_state['rag_generated']:
            # Add the last three exchanges
            EXCHANGE_LIMIT = 3
            size = len(st.session_state['rag_generated'])
            # print("Current size of history:", size)
            for i in range(max(size-EXCHANGE_LIMIT, 0), size):
                context.append(
                    {'role': 'user', 'content': st.session_state['user_input'][i]}
                )
                context.append(
                    {'role': 'assistant', 'content': st.session_state["rag_generated"][i]}
                )
        return context
