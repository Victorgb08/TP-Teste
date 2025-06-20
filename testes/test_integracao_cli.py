import pytest
import subprocess
import os
import sys
import json
from uuid import UUID

# Define o nome do arquivo de teste padrão para os testes de integração
ARQUIVO_JSON_INTEGRACAO = "tarefas_teste_integracao.json"

# Lista para rastrear arquivos temporários criados pelos testes
arquivos_temporarios_a_limpar = [ARQUIVO_JSON_INTEGRACAO]

@pytest.fixture(autouse=True)
def setup_teardown():
    """ Fixture para limpar arquivos JSON de teste antes e depois de cada teste. """
    # Limpa antes do teste
    for arquivo in arquivos_temporarios_a_limpar:
        if os.path.exists(arquivo):
            os.remove(arquivo)
    
    # Limpa a lista para a próxima execução de teste
    arquivos_temporarios_a_limpar.clear()
    arquivos_temporarios_a_limpar.append(ARQUIVO_JSON_INTEGRACAO)
    
    yield

    # Limpa após o teste
    for arquivo in arquivos_temporarios_a_limpar:
        if os.path.exists(arquivo):
            os.remove(arquivo)

def executar_comando(comandos_input, arquivo_json=ARQUIVO_JSON_INTEGRACAO):
    """
    Executa o main.py como um subprocesso, fornecendo entradas e o nome do arquivo de teste.
    """
    caminho_main = os.path.join(os.path.dirname(__file__), '..', 'main.py')
    
    # Garante que o programa sempre saia para não ficar preso em um loop infinito
    if "5" not in comandos_input:
        comandos_input.append("5")
        
    input_str = "\n".join(comandos_input)
    
    # Força o subprocesso a usar UTF-8 para I/O
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    processo = subprocess.run(
        [sys.executable, caminho_main, arquivo_json],
        input=input_str,
        capture_output=True,
        text=True,
        encoding='utf-8', 
        env=env,
        timeout=10
    )
    
    if processo.returncode != 0 and processo.stderr:
        print("Erro no subprocesso:", processo.stderr)

    return processo.stdout

def test_ciclo_de_vida_completo_da_tarefa():
    # --- 1. Adicionar Tarefa ---
    output_add = executar_comando(["1", "Minha Tarefa de Teste E2E", "2025-12-25"])
    assert "Tarefa 'Minha Tarefa de Teste E2E' adicionada com sucesso." in output_add
    # ... (resto do seu teste, sem alterações)
    # --- 2. Visualizar e obter ID ---
    output_view1 = executar_comando(["2"])
    assert "Minha Tarefa de Teste E2E" in output_view1
    assert "Status: Pendente" in output_view1
    id_tarefa = ""
    for linha in output_view1.splitlines():
        if "Minha Tarefa de Teste E2E" in linha:
            id_tarefa = linha.split(" | ")[0].replace("ID: ", "")
            try:
                UUID(id_tarefa, version=4)
            except ValueError:
                pytest.fail(f"ID extraído não é um UUID válido: {id_tarefa}")
    assert id_tarefa, "Não foi possível extrair o ID da tarefa."
    # --- 3. Marcar como Concluída ---
    output_complete = executar_comando(["3", id_tarefa])
    assert "marcada como concluída" in output_complete
    # --- 4. Visualizar Novamente ---
    output_view2 = executar_comando(["2"])
    assert "Status: Concluída" in output_view2
    # --- 5. Remover Tarefa ---
    output_remove = executar_comando(["4", id_tarefa])
    assert "removida com sucesso" in output_remove
    # --- 6. Confirmar Remoção ---
    output_view3 = executar_comando(["2"])
    assert "Nenhuma tarefa cadastrada." in output_view3

def test_tentar_remover_tarefa_inexistente_via_cli():
    output = executar_comando(["4", "id-que-nao-existe"])
    assert "Erro: Tarefa com ID 'id-que-nao-existe' não encontrada para remoção." in output

def test_menu_com_opcao_invalida():
    output = executar_comando(["99", "1", "Tarefa Teste", ""])
    assert "Opção inválida. Por favor, tente novamente." in output
    assert "Tarefa 'Tarefa Teste' adicionada com sucesso." in output

def test_persistência_entre_execucoes():
    executar_comando(["1", "Tarefa Persistente", ""])
    output = executar_comando(["2"])
    assert "Tarefa Persistente" in output
    assert "Status: Pendente" in output

def test_adicionar_tarefa_com_descricao_vazia_pelo_cli():
    output = executar_comando(["1", "   ", "2025-01-01"]) 
    assert "Erro: A descrição da tarefa não pode ser vazia." in output
    output_view = executar_comando(["2"])
    assert "Nenhuma tarefa cadastrada." in output_view

def test_marcar_tarefa_ja_concluida_pelo_cli():
    executar_comando(["1", "Tarefa a ser concluída", ""])
    output_view = executar_comando(["2"])
    id_tarefa = ""
    for linha in output_view.splitlines():
        if "Tarefa a ser concluída" in linha:
            id_tarefa = linha.split(" | ")[0].replace("ID: ", "")
    assert id_tarefa, "Falha ao extrair ID da tarefa após visualização."
    executar_comando(["3", id_tarefa])
    output_reattempt = executar_comando(["3", id_tarefa])
    assert "já estava concluída" in output_reattempt

def test_visualizar_lista_com_multiplas_tarefas():
    executar_comando(["1", "Primeira Tarefa", "2025-01-01"])
    executar_comando(["1", "Segunda Tarefa", "2025-02-01"])
    executar_comando(["1", "Terceira Tarefa", ""])
    output = executar_comando(["2"])
    assert "Primeira Tarefa" in output
    assert "Segunda Tarefa" in output
    assert "Terceira Tarefa" in output
    assert output.count("ID: ") == 3

def test_adicionar_e_remover_tarefa_do_meio():
    executar_comando(["1", "Tarefa 1 (Manter)", ""])
    executar_comando(["1", "Tarefa 2 (Remover)", ""])
    executar_comando(["1", "Tarefa 3 (Manter)", ""])
    output_view = executar_comando(["2"])
    ids = {}
    for linha in output_view.splitlines():
        if "ID: " in linha:
            descricao = linha.split("Descrição: ")[1].split(" | ")[0]
            task_id = linha.split(" | ")[0].replace("ID: ", "")
            ids[descricao] = task_id
    assert len(ids) == 3, "Esperava encontrar 3 tarefas na visualização."
    id_para_remover = ids.get("Tarefa 2 (Remover)")
    assert id_para_remover, "Não foi possível encontrar o ID da tarefa a ser removida."
    executar_comando(["4", id_para_remover])
    output_final = executar_comando(["2"])
    assert "Tarefa 1 (Manter)" in output_final
    assert "Tarefa 3 (Manter)" in output_final
    assert "Tarefa 2 (Remover)" not in output_final
    assert output_final.count("ID: ") == 2

def test_saida_imediata_do_programa():
    output = executar_comando([]) 
    assert "Saindo do Gerenciador de Tarefas. Até logo!" in output

def test_adicionar_tarefa_com_data_vencimento_invalida_string():
    executar_comando(["1", "Tarefa com data estranha", "isso-nao-e-uma-data"])
    output = executar_comando(["2"])
    assert "Tarefa com data estranha" in output
    assert "Vencimento: isso-nao-e-uma-data" in output

def test_iniciar_com_json_corrompido():
    """
    Testa se a CLI exibe uma mensagem de erro ao tentar carregar um JSON
    malformado e, em seguida, inicia com uma lista de tarefas vazia.
    """
    arquivo_json_corrompido = 'teste_corrompido.json'
    arquivos_temporarios_a_limpar.append(arquivo_json_corrompido)
    
    # Cria um arquivo JSON com sintaxe inválida (vírgula extra)
    with open(arquivo_json_corrompido, 'w', encoding='utf-8') as f:
        f.write('[{"descricao": "tarefa 1", "concluida": false,},]')
    
    # Executa o comando apontando para o arquivo corrompido
    saida = executar_comando(comandos_input=['2'], arquivo_json=arquivo_json_corrompido)
    
    assert "Erro ao decodificar JSON" in saida
    assert "Nenhuma tarefa cadastrada." in saida

def test_iniciar_com_json_de_tipo_inesperado():
    """
    Testa se a CLI informa ao usuário se o arquivo JSON não contém
    uma lista (por exemplo, contém um dicionário).
    """
    arquivo_json_nao_lista = 'teste_nao_lista.json'
    arquivos_temporarios_a_limpar.append(arquivo_json_nao_lista)

    # Cria um arquivo com um objeto JSON em vez de uma lista
    with open(arquivo_json_nao_lista, 'w', encoding='utf-8') as f:
        f.write('{"erro": "isto não é uma lista de tarefas"}')

    saida = executar_comando(comandos_input=['2'], arquivo_json=arquivo_json_nao_lista)

    assert "Erro: O conteúdo do arquivo" in saida
    assert "não é uma lista JSON válida" in saida
    assert "Iniciando com lista vazia" in saida
    
    # Também garantimos que, após o erro, a lista de tarefas está vazia.
    assert "Nenhuma tarefa cadastrada." in saida

def test_iniciar_com_dados_de_tarefa_invalidos():
    """
    Testa se, ao carregar um JSON com uma tarefa com dados inválidos (ex: sem 'descricao'),
    a CLI pula essa tarefa, carrega as válidas e informa o erro.
    """
    arquivo_json_dados_invalidos = 'teste_dados_invalidos.json'
    arquivos_temporarios_a_limpar.append(arquivo_json_dados_invalidos)

    tarefa_valida = {"descricao": "Tarefa Válida", "concluida": False, "data_vencimento": None}
    tarefa_invalida = {"desc": "Chave Incorreta", "concluida": False} 
    
    with open(arquivo_json_dados_invalidos, 'w', encoding='utf-8') as f:
        json.dump([tarefa_valida, tarefa_invalida], f)

    saida = executar_comando(comandos_input=['2'], arquivo_json=arquivo_json_dados_invalidos)

    assert "Erro nos dados ao carregar uma tarefa do arquivo" in saida
    assert "Tarefa Válida" in saida
    assert "Chave Incorreta" not in saida

def test_isolamento_de_dados_com_argumento_cli():
    """
    Verifica se a passagem de diferentes nomes de arquivo como argumento
    na linha de comando resulta em bancos de dados de tarefas separados.
    """
    arquivo_a = 'tarefas_A.json'
    arquivo_b = 'tarefas_B.json'
    arquivos_temporarios_a_limpar.extend([arquivo_a, arquivo_b])

    # Adiciona "Tarefa A" no arquivo_a
    executar_comando(['1', 'Tarefa A', ''], arquivo_json=arquivo_a)
    # Adiciona "Tarefa B" no arquivo_b
    executar_comando(['1', 'Tarefa B', ''], arquivo_json=arquivo_b)

    # Verifica o conteúdo do arquivo_a
    saida_a = executar_comando(['2'], arquivo_json=arquivo_a)
    assert "Tarefa A" in saida_a
    assert "Tarefa B" not in saida_a

    # Verifica o conteúdo do arquivo_b
    saida_b = executar_comando(['2'], arquivo_json=arquivo_b)
    assert "Tarefa B" in saida_b
    assert "Tarefa A" not in saida_b