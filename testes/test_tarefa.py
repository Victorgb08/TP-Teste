# testes/test_tarefa.py

import pytest
from gerenciador_tarefas.tarefa import Tarefa

class TestTarefa:
    """
    Conjunto de testes para a classe Tarefa.
    """

    def test_criar_tarefa_com_sucesso(self):
        """Testa a criação de uma tarefa válida."""
        tarefa = Tarefa("Comprar pão", "2024-12-31")
        assert tarefa.descricao == "Comprar pão"
        assert tarefa.data_vencimento == "2024-12-31"
        assert not tarefa.concluida
        assert tarefa.id is not None

    def test_criar_tarefa_sem_data_vencimento(self):
        """Testa a criação de uma tarefa sem data de vencimento."""
        tarefa = Tarefa("Estudar Python")
        assert tarefa.descricao == "Estudar Python"
        assert tarefa.data_vencimento is None
        assert not tarefa.concluida

    def test_criar_tarefa_com_id_especifico(self):
        """Testa a criação de uma tarefa com um ID fornecido."""
        id_customizado = "tarefa-123"
        tarefa = Tarefa("Tarefa com ID", id_tarefa=id_customizado)
        assert tarefa.id == id_customizado

    def test_marcar_tarefa_como_concluida(self):
        """Testa marcar uma tarefa como concluída."""
        tarefa = Tarefa("Lavar louça")
        assert not tarefa.concluida
        tarefa.marcar_como_concluida()
        assert tarefa.concluida

    def test_marcar_tarefa_como_pendente(self):
        """Testa marcar uma tarefa concluída como pendente."""
        tarefa = Tarefa("Passear com o cachorro", concluida=True)
        assert tarefa.concluida
        tarefa.marcar_como_pendente()
        assert not tarefa.concluida

    def test_representacao_string_tarefa_pendente(self):
        """Testa a representação em string de uma tarefa pendente."""
        tarefa = Tarefa("Ler livro", "2025-01-15")
        esperado = f"ID: {tarefa.id} | Descrição: Ler livro, Vencimento: 2025-01-15 | Status: Pendente"
        assert str(tarefa) == esperado

    def test_representacao_string_tarefa_concluida_sem_data(self):
        """Testa a representação em string de uma tarefa concluída sem data de vencimento."""
        tarefa = Tarefa("Fazer café", concluida=True)
        # A linha abaixo é redundante pois a tarefa já é inicializada como concluída.
        # tarefa.marcar_como_concluida() 
        esperado = f"ID: {tarefa.id} | Descrição: Fazer café | Status: Concluída"
        assert str(tarefa) == esperado
    
    def test_criar_tarefa_descricao_vazia_levanta_erro(self):
        """Testa que criar tarefa com descrição vazia levanta ValueError."""
        with pytest.raises(ValueError, match="A descrição da tarefa não pode ser vazia"):
            Tarefa("")

    def test_criar_tarefa_descricao_none_levanta_erro(self):
        """Testa que criar tarefa com descrição None levanta ValueError."""
        with pytest.raises(ValueError, match="A descrição da tarefa deve ser uma string."): # MODIFIED
            Tarefa(None)

    def test_to_dict_serializa_corretamente(self):
        """Testa a serialização da tarefa para um dicionário."""
        tarefa = Tarefa("Pagar contas", "2024-06-30", concluida=False)
        tarefa_dict = tarefa.to_dict()
        assert tarefa_dict["id"] == tarefa.id
        assert tarefa_dict["descricao"] == "Pagar contas"
        assert tarefa_dict["data_vencimento"] == "2024-06-30"
        assert tarefa_dict["concluida"] is False

    def test_from_dict_cria_tarefa_corretamente(self):
        """Testa a criação de uma tarefa a partir de um dicionário."""
        dados_dict = {
            "id": "test-id-from-dict",
            "descricao": "Tarefa de Dicionário",
            "data_vencimento": "2025-03-03",
            "concluida": True
        }
        tarefa = Tarefa.from_dict(dados_dict)
        assert tarefa.id == "test-id-from-dict"
        assert tarefa.descricao == "Tarefa de Dicionário"
        assert tarefa.data_vencimento == "2025-03-03"
        assert tarefa.concluida is True

    def test_from_dict_com_dados_minimos(self):
        """Testa a criação de uma tarefa a partir de um dicionário com dados mínimos."""
        dados_dict = {
            "descricao": "Tarefa Mínima"
            # id, data_vencimento, concluida são opcionais ou têm defaults
        }
        tarefa = Tarefa.from_dict(dados_dict)
        assert tarefa.descricao == "Tarefa Mínima"
        assert tarefa.id is not None # Deve gerar um UUID
        assert tarefa.data_vencimento is None
        assert tarefa.concluida is False

    def test_from_dict_entrada_invalida_levanta_erro(self):
        """Testa que from_dict com entrada não dicionário levanta ValueError."""
        with pytest.raises(ValueError, match="Os dados de entrada devem ser um dicionário."):
            Tarefa.from_dict("não é um dict")
            
    def test_to_dict_e_from_dict_roundtrip(self):
        """Testa a serialização e desserialização de uma tarefa (roundtrip)."""
        tarefa_original = Tarefa("Teste Roundtrip", "2025-01-01", concluida=True)
        tarefa_dict = tarefa_original.to_dict()
        tarefa_nova = Tarefa.from_dict(tarefa_dict)
        assert tarefa_nova.id == tarefa_original.id
        assert tarefa_nova.descricao == tarefa_original.descricao
        assert tarefa_nova.data_vencimento == tarefa_original.data_vencimento
        assert tarefa_nova.concluida == tarefa_original.concluida

    def test_from_dict_com_descricao_none_levanta_erro(self):
        """Testa que from_dict com descrição None no dicionário de dados levanta ValueError."""
        with pytest.raises(ValueError, match="A descrição da tarefa deve ser uma string."): # MODIFIED
            Tarefa.from_dict({"descricao": None, "id": "some-id"})