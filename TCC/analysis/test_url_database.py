# model/test_url_database.py

import unittest
from unittest.mock import patch, MagicMock
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import SeleniumURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from url_database import WebDatabase


class TestWebDatabase(unittest.TestCase):

    # @patch('os.path.exists')
    # @patch('langchain_community.vectorstores.Chroma')
    # def test_init_chroma_db_exists(self, mock_chroma, mock_exists):
    #     # Mock os.path.exists to return True
    #     mock_exists.return_value = True

    #     # Initialize WebDatabase
    #     db = WebDatabase.GetInstance(load=False, database=mock_chroma)

    #     # Check if Chroma was initialized with the correct parameters
    #     mock_chroma.assert_called_once_with(
    #         persist_directory="./chroma_db",
    #         embedding_function=MagicMock()
    #     )

    @patch('os.path.exists')
    @patch('langchain_community.vectorstores.Chroma')
    @patch('langchain_community.document_loaders.SeleniumURLLoader')
    @patch('langchain.text_splitter.RecursiveCharacterTextSplitter')
    def test_init_chroma_db_not_exists(self, mock_text_splitter, mock_loader, mock_chroma, mock_exists):
        # Mock os.path.exists to return False
        mock_exists.return_value = False

        # Mock urls:
        mock_urls = ["https://pt.wikipedia.org/wiki/Javier_Milei",
            "https://www.cbsnews.com/news/super-bowl-winners-list-history/",
        #     "https://ge.globo.com/futebol/times/corinthians/noticia/2024/02/16/corinthians-anuncia-a-contratacao-do-lateral-direito-matheuzinho.ghtml",
        #     "https://ge.globo.com/futebol/times/botafogo/noticia/2024/02/16/luiz-henrique-do-botafogo-tem-lesao-na-panturrilha.ghtml",
        #     "https://ge.globo.com/futebol/times/fluminense/noticia/2024/02/16/escalacao-do-fluminense-diniz-escala-reservas-contra-madureira-mas-tera-john-kennedy-e-douglas-costa.ghtml",
        # "https://www.lemonde.fr/football/article/2024/02/25/ligue-1-le-psg-arrache-le-nul-de-justesse-contre-rennes-monaco-remonte-sur-le-podium_6218528_1616938.html",
        # "https://ge.globo.com/futebol/futebol-internacional/futebol-frances/copa-da-franca/noticia/2024/02/27/perri-e-heroi-nos-penaltis-e-lyon-avanca-de-fase-na-copa-da-franca.ghtml",
        "https://ge.globo.com/tenis/noticia/2024/02/27/joao-fonseca-sofre-com-condicoes-ruins-da-quadra-no-atp-santiago-e-e-eliminado.ghtml",   
        ]

        # Initialize WebDatabase
        db = WebDatabase(load=False, urls=mock_urls, text_splitter=mock_text_splitter, loader=mock_loader)
        db.ask_rag("What is the capital of Brazil?")
        # Mock SeleniumURLLoader to return documents
        mock_loader_instance = mock_loader.return_value
        mock_loader_instance.load.return_value = [MagicMock()]

        # Mock RecursiveCharacterTextSplitter to return splits
        mock_text_splitter_instance = mock_text_splitter.return_value
        mock_text_splitter_instance.split_documents.return_value = [MagicMock()]

        # Check if SeleniumURLLoader was called with the correct URLs
        mock_loader.assert_called_once_with(urls=mock_urls)
        mock_loader_instance.load.assert_called_once()

        # Check if RecursiveCharacterTextSplitter was called with the correct parameters
        mock_text_splitter.assert_called_once_with(chunk_size=1000, chunk_overlap=100)
        mock_text_splitter_instance.split_documents.assert_called_once_with(mock_loader_instance.load.return_value)

        # Check if Chroma was initialized with the correct parameters
        mock_chroma.from_documents.assert_called_once_with(
            documents=mock_text_splitter_instance.split_documents.return_value,
            embedding=MagicMock(),
            persist_directory="./chroma_db"
        )

if __name__ == '__main__':
    unittest.main()