# testes/test_logica.py

import pytest
import os
import json
from gerenciador_tarefas.logica import GerenciadorDeTarefas
from gerenciador_tarefas.tarefa import Tarefa

# Define um nome de arquivo de teste para não interferir com o arquivo padrão
ARQUIVO_TESTE_JSON = "tarefas_teste_logica.json"

@pytest.fixture
def gerenciador_vazio():
    """Fixture para criar um GerenciadorDeTarefas com um arquivo de teste limpo."""
    if os.path.exists(ARQUIVO_TESTE_JSON):
        os.remove(ARQUIVO_TESTE_JSON)
    gerenciador = GerenciadorDeTarefas(arquivo_json=ARQUIVO_TESTE_JSON)
    # Certifique-se de que o arquivo é limpo após a inicialização, se _carregar_tarefas o criar.
    if os.path.exists(ARQUIVO_TESTE_JSON):
         with open(ARQUIVO_TESTE_JSON, "w") as f:
             json.dump([], f)
         gerenciador.tarefas = [] # Garante que a lista interna também está vazia
    return gerenciador

@pytest.fixture
def gerenciador_com_tarefas(gerenciador_vazio):
    """Fixture para um gerenciador com algumas tarefas pré-adicionadas."""
    t1 = gerenciador_vazio.adicionar_tarefa("Tarefa de Teste 1", "2024-01-01")
    t2 = gerenciador_vazio.adicionar_tarefa("Tarefa de Teste 2")
    t3 = gerenciador_vazio.adicionar_tarefa("Tarefa Concluída Teste", "2024-02-01")
    gerenciador_vazio.marcar_tarefa_como_concluida(t3.id)
    return gerenciador_vazio, [t1, t2, t3]

@pytest.fixture
def arquivo_teste(tmp_path):
    """Cria um caminho de arquivo temporário para teste."""
    return tmp_path / "tarefas_teste.json"


class TestGerenciadorDeTarefas:
    """
    Conjunto de testes para a classe GerenciadorDeTarefas.
    """

    def test_adicionar_tarefa_com_sucesso(self, gerenciador_vazio):
        """Testa adicionar uma tarefa válida."""
        tarefa = gerenciador_vazio.adicionar_tarefa("Nova Tarefa Teste", "2025-10-10")
        assert tarefa is not None
        assert tarefa.descricao == "Nova Tarefa Teste"
        assert len(gerenciador_vazio.tarefas) == 1
        assert gerenciador_vazio.tarefas[0] == tarefa

    def test_adicionar_tarefa_descricao_vazia_retorna_none(self, gerenciador_vazio, capsys):
        """Testa que adicionar tarefa com descrição vazia não adiciona e imprime erro."""
        tarefa = gerenciador_vazio.adicionar_tarefa("   ")
        assert tarefa is None
        assert len(gerenciador_vazio.tarefas) == 0
        captured = capsys.readouterr()
        assert "Erro: A descrição da tarefa não pode ser vazia." in captured.out

    def test_visualizar_tarefas_vazio(self, gerenciador_vazio):
        """Testa visualizar tarefas quando a lista está vazia."""
        assert gerenciador_vazio.visualizar_tarefas() == ["Nenhuma tarefa cadastrada."]

    def test_visualizar_tarefas_com_conteudo(self, gerenciador_com_tarefas):
        """Testa visualizar tarefas quando há tarefas na lista."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        visualizacao = gerenciador.visualizar_tarefas()
        assert len(visualizacao) == len(tarefas_originais)
        for tarefa_original in tarefas_originais:
            assert any(tarefa_original.id in s for s in visualizacao)

    def test_encontrar_tarefa_por_id_existente(self, gerenciador_com_tarefas):
        """Testa encontrar uma tarefa existente pelo ID."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        tarefa_alvo = tarefas_originais[0]
        encontrada = gerenciador.encontrar_tarefa_por_id(tarefa_alvo.id)
        assert encontrada is not None
        assert encontrada.id == tarefa_alvo.id

    def test_encontrar_tarefa_por_id_inexistente(self, gerenciador_com_tarefas):
        """Testa encontrar uma tarefa com ID inexistente."""
        gerenciador, _ = gerenciador_com_tarefas
        encontrada = gerenciador.encontrar_tarefa_por_id("id-que-nao-existe-123")
        assert encontrada is None
    
    def test_encontrar_tarefa_id_invalido(self, gerenciador_com_tarefas):
        """Testa encontrar tarefa com ID None ou não string."""
        gerenciador, _ = gerenciador_com_tarefas
        assert gerenciador.encontrar_tarefa_por_id(None) is None
        assert gerenciador.encontrar_tarefa_por_id(123) is None 

    def test_marcar_tarefa_como_concluida_sucesso(self, gerenciador_com_tarefas, capsys):
        """Testa marcar uma tarefa pendente como concluída."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        tarefa_pendente = tarefas_originais[0] 
        assert not tarefa_pendente.concluida
        
        resultado = gerenciador.marcar_tarefa_como_concluida(tarefa_pendente.id)
        assert resultado is True
        assert tarefa_pendente.concluida 
        
        tarefa_recarregada = gerenciador.encontrar_tarefa_por_id(tarefa_pendente.id)
        assert tarefa_recarregada.concluida 
        
        captured = capsys.readouterr()
        assert f"Tarefa '{tarefa_pendente.descricao}' marcada como concluída." in captured.out

    def test_marcar_tarefa_ja_concluida(self, gerenciador_com_tarefas, capsys):
        """Testa marcar uma tarefa que já está concluída."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        tarefa_concluida_originalmente = tarefas_originais[2] 
        
        assert tarefa_concluida_originalmente.concluida
        resultado = gerenciador.marcar_tarefa_como_concluida(tarefa_concluida_originalmente.id)
        assert resultado is False 
        assert tarefa_concluida_originalmente.concluida 
        
        captured = capsys.readouterr()
        assert f"Tarefa '{tarefa_concluida_originalmente.descricao}' já estava concluída." in captured.out

    def test_marcar_tarefa_como_concluida_id_inexistente(self, gerenciador_vazio, capsys):
        """Testa marcar tarefa como concluída com ID inexistente."""
        resultado = gerenciador_vazio.marcar_tarefa_como_concluida("id-fantasma")
        assert resultado is False
        captured = capsys.readouterr()
        assert "Erro: Tarefa com ID 'id-fantasma' não encontrada." in captured.out

    def test_remover_tarefa_sucesso(self, gerenciador_com_tarefas, capsys):
        """Testa remover uma tarefa existente."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        id_para_remover = tarefas_originais[1].id
        desc_tarefa_removida = tarefas_originais[1].descricao
        tamanho_antes = len(gerenciador.tarefas)

        resultado = gerenciador.remover_tarefa(id_para_remover)
        assert resultado is True
        assert len(gerenciador.tarefas) == tamanho_antes - 1
        assert gerenciador.encontrar_tarefa_por_id(id_para_remover) is None
        
        captured = capsys.readouterr()
        assert f"Tarefa '{desc_tarefa_removida}' removida com sucesso." in captured.out

    def test_remover_tarefa_id_inexistente(self, gerenciador_com_tarefas, capsys):
        """Testa remover tarefa com ID inexistente."""
        gerenciador, _ = gerenciador_com_tarefas
        tamanho_antes = len(gerenciador.tarefas)
        resultado = gerenciador.remover_tarefa("id-sumido")
        assert resultado is False
        assert len(gerenciador.tarefas) == tamanho_antes 
        
        captured = capsys.readouterr()
        assert "Erro: Tarefa com ID 'id-sumido' não encontrada para remoção." in captured.out

    def test_salvar_e_carregar_tarefas(self, gerenciador_vazio):
        """Testa a persistência (salvar e carregar) das tarefas."""
        t1 = gerenciador_vazio.adicionar_tarefa("Tarefa para salvar 1", "2025-11-11")
        t2 = gerenciador_vazio.adicionar_tarefa("Tarefa para salvar 2")
        gerenciador_vazio.marcar_tarefa_como_concluida(t2.id) 
        
        tarefas_originais_dict = sorted([t.to_dict() for t in gerenciador_vazio.tarefas], key=lambda x: x['id'])

        novo_gerenciador = GerenciadorDeTarefas(arquivo_json=ARQUIVO_TESTE_JSON)
        assert len(novo_gerenciador.tarefas) == len(tarefas_originais_dict)
        
        tarefas_carregadas_dict = sorted([t.to_dict() for t in novo_gerenciador.tarefas], key=lambda x: x['id'])
        assert tarefas_carregadas_dict == tarefas_originais_dict

    def test_carregar_de_arquivo_inexistente_inicia_vazio(self, capsys):
        """Testa que carregar de um arquivo inexistente não levanta erro e inicia vazio."""
        nome_arquivo_fantasma = "arquivo_que_nao_existe_jamais_logica.json"
        if os.path.exists(nome_arquivo_fantasma): 
            os.remove(nome_arquivo_fantasma)
            
        gerenciador = GerenciadorDeTarefas(arquivo_json=nome_arquivo_fantasma)
        assert len(gerenciador.tarefas) == 0
        captured = capsys.readouterr()
        assert f"Arquivo {nome_arquivo_fantasma} não encontrado." in captured.out

    def test_carregar_de_arquivo_json_mal_formado(self, capsys):
        """Testa o carregamento de um arquivo JSON mal formado."""
        nome_arquivo_corrompido = "corrompido_teste_logica.json"
        with open(nome_arquivo_corrompido, "w") as f:
            f.write("isto não é json válido {")
        
        gerenciador = GerenciadorDeTarefas(arquivo_json=nome_arquivo_corrompido)
        assert len(gerenciador.tarefas) == 0 
        captured = capsys.readouterr()
        assert f"Erro ao decodificar JSON do arquivo {nome_arquivo_corrompido}" in captured.out

        if os.path.exists(nome_arquivo_corrompido):
            os.remove(nome_arquivo_corrompido)
            
    def test_limpar_todas_as_tarefas(self, gerenciador_com_tarefas, capsys):
        """Testa a funcionalidade de limpar todas as tarefas."""
        gerenciador, _ = gerenciador_com_tarefas
        assert len(gerenciador.tarefas) > 0 

        gerenciador.limpar_todas_as_tarefas()
        assert len(gerenciador.tarefas) == 0
        
        # Verifica se o arquivo foi esvaziado
        if os.path.exists(ARQUIVO_TESTE_JSON):
            with open(ARQUIVO_TESTE_JSON, "r") as f:
                dados_arquivo = json.load(f)
            assert dados_arquivo == []
            
        captured = capsys.readouterr()
        assert "Todas as tarefas foram removidas." in captured.out

    def test_visualizar_tarefas_filtrando_apenas_concluidas(self, gerenciador_com_tarefas):
        """Testa visualizar apenas tarefas concluídas."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        tarefa_concluida = next(t for t in tarefas_originais if t.concluida)

        visualizacao = gerenciador.visualizar_tarefas(mostrar_concluidas=True, mostrar_pendentes=False)
        assert len(visualizacao) == 1
        assert tarefa_concluida.id in visualizacao[0]
        assert "Status: Concluída" in visualizacao[0]

    def test_visualizar_tarefas_filtrando_apenas_pendentes(self, gerenciador_com_tarefas):
        """Testa visualizar apenas tarefas pendentes."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        tarefas_pendentes = [t for t in tarefas_originais if not t.concluida]

        visualizacao = gerenciador.visualizar_tarefas(mostrar_concluidas=False, mostrar_pendentes=True)
        assert len(visualizacao) == len(tarefas_pendentes)
        for tp in tarefas_pendentes:
            assert any(tp.id in s for s in visualizacao)
        assert all("Status: Pendente" in s for s in visualizacao)

    def test_visualizar_tarefas_filtro_nao_retorna_nada(self, gerenciador_com_tarefas):
        """Testa um filtro que não deve retornar nenhuma tarefa."""
        gerenciador, _ = gerenciador_com_tarefas
        for tarefa_obj in gerenciador.tarefas: # Usar tarefa_obj para evitar conflito com módulo tarefa
             if tarefa_obj.concluida:
                 tarefa_obj.marcar_como_pendente()
        gerenciador._salvar_tarefas()

        visualizacao = gerenciador.visualizar_tarefas(mostrar_concluidas=True, mostrar_pendentes=False)
        assert visualizacao == ["Nenhuma tarefa corresponde aos critérios de filtro."]
        
    def test_adicionar_tarefa_com_data_vencimento_vazia(self, gerenciador_vazio):
        """Testa adicionar tarefa com string de data de vencimento vazia."""
        tarefa_obj = gerenciador_vazio.adicionar_tarefa("Tarefa sem data explícita", "") # Usar tarefa_obj
        assert tarefa_obj is not None
        assert tarefa_obj.data_vencimento is None

    def test_remover_tarefa_de_lista_vazia(self, gerenciador_vazio, capsys):
        """Testa remover tarefa de uma lista vazia."""
        resultado = gerenciador_vazio.remover_tarefa("id-inexistente-em-lista-vazia")
        assert not resultado
        captured = capsys.readouterr()
        assert "Erro: Tarefa com ID 'id-inexistente-em-lista-vazia' não encontrada para remoção." in captured.out

    def test_salvar_tarefas_com_erro_io(self, monkeypatch, gerenciador_com_tarefas, capsys):
        """Testa o comportamento de _salvar_tarefas ao encontrar um IOError."""
        gerenciador, _ = gerenciador_com_tarefas
        
        def mock_open_raise_io_error(*args, **kwargs):
            if args[0] == ARQUIVO_TESTE_JSON and args[1] == "w": # Apenas para escrita no arquivo de teste
                raise IOError("Erro de escrita simulado")
            return open(*args, **kwargs) # Chamada original para outros casos
        
        monkeypatch.setattr("builtins.open", mock_open_raise_io_error)
        
        gerenciador.adicionar_tarefa("Tarefa para teste de erro IO") 
        
        captured = capsys.readouterr()
        # A mensagem de "adicionada com sucesso" pode aparecer antes do erro de salvar, dependendo da ordem.
        # O importante é que o erro de IO seja capturado e impresso.
        assert f"Erro de E/S ao salvar tarefas em {ARQUIVO_TESTE_JSON}: Erro de escrita simulado" in captured.out

    def test_carregar_tarefas_com_erro_io(self, monkeypatch, capsys):
        """Testa o comportamento de _carregar_tarefas ao encontrar um IOError."""
        arquivo_teste_io_error = "io_error_test_file_logica.json"

        # Garante que o arquivo exista para que a tentativa de leitura ocorra
        with open(arquivo_teste_io_error, "w") as f:
            json.dump([{"id": "1", "descricao": "teste", "data_vencimento": None, "concluida": False}], f)

        def mock_open_raise_io_error_on_read(*args, **kwargs):
            if args[0] == arquivo_teste_io_error and args[1] == 'r':
                raise IOError("Erro de leitura simulado")
            return open(*args, **kwargs) # Chamada original para outros casos

        monkeypatch.setattr("builtins.open", mock_open_raise_io_error_on_read)
        # Mock os.path.exists para garantir que o código tente ler o arquivo
        original_exists = os.path.exists
        def mock_exists(path):
            if path == arquivo_teste_io_error:
                return True
            return original_exists(path)
        monkeypatch.setattr("os.path.exists", mock_exists)


        gerenciador = GerenciadorDeTarefas(arquivo_json=arquivo_teste_io_error)
        assert gerenciador.tarefas == [] 
        captured = capsys.readouterr()
        assert f"Erro de E/S ao tentar ler o arquivo {arquivo_teste_io_error}" in captured.out
        
        if os.path.exists(arquivo_teste_io_error):
            os.remove(arquivo_teste_io_error)

    def test_adicionar_tarefa_levanta_value_error(self, monkeypatch, capsys):
        """Força um ValueError no Tarefa.__init__ e verifica o except de adicionar_tarefa."""
        # Garante que o arquivo de persistência não existe para não atrapalhar o __init__
        if os.path.exists(ARQUIVO_TESTE_JSON):
            os.remove(ARQUIVO_TESTE_JSON)

        ger = GerenciadorDeTarefas(arquivo_json=ARQUIVO_TESTE_JSON)

        # Monkeypatch: quando o Gerenciador chamar Tarefa(...), levantará ValueError
        def fake_tarefa_ctor(descricao, data_vencimento=None):
            raise ValueError("Erro simulado ao criar Tarefa")
        monkeypatch.setattr("gerenciador_tarefas.logica.Tarefa", fake_tarefa_ctor)

        resultado = ger.adicionar_tarefa("Descrição qualquer", "2025-01-01")
        assert resultado is None

        saida = capsys.readouterr().out
        assert "Erro ao criar tarefa: Erro simulado ao criar Tarefa" in saida

    def test_carregar_tarefas_conteudo_nao_lista(self, arquivo_teste, capsys):
        """Quando o JSON existe mas não é uma lista, deve cair no primeiro ramo do _carregar_tarefas."""
        # Cria um JSON que é um dicionário, não uma lista
        arquivo_teste.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")

        ger = GerenciadorDeTarefas(arquivo_json=str(arquivo_teste))

        # Como o conteúdo não é lista, não carrega nada
        assert ger.tarefas == []

        saida = capsys.readouterr().out
        assert f"Erro: O conteúdo do arquivo {arquivo_teste} não é uma lista JSON válida" in saida

    def test_carregar_tarefas_dados_invalidos(self, arquivo_teste, capsys):
        """Quando há itens na lista mas Tarefa.from_dict levanta ValueError, deve imprimir mensagem e ignorar."""
        # Monta uma lista com um dicionário que torna Tarefa.from_dict inválido (descricao=None)
        dados_invalidos = [{"id": "1", "descricao": None, "data_vencimento": "2025-12-31", "concluida": False}]
        arquivo_teste.write_text(json.dumps(dados_invalidos), encoding="utf-8")

        ger = GerenciadorDeTarefas(arquivo_json=str(arquivo_teste))

        # Nenhuma tarefa válida deve ser carregada
        assert ger.tarefas == []

        saida = capsys.readouterr().out
        assert f"Erro nos dados ao carregar uma tarefa do arquivo {arquivo_teste}" in saida

    @classmethod
    def teardown_class(cls):
        """Limpa o arquivo de teste JSON após todos os testes da classe."""
        if os.path.exists(ARQUIVO_TESTE_JSON):
            os.remove(ARQUIVO_TESTE_JSON)
        if os.path.exists("corrompido_teste_logica.json"):
            os.remove("corrompido_teste_logica.json")
        if os.path.exists("io_error_test_file_logica.json"):
            os.remove("io_error_test_file_logica.json")
        if os.path.exists("arquivo_que_nao_existe_jamais_logica.json"):
            os.remove("arquivo_que_nao_existe_jamais_logica.json")
