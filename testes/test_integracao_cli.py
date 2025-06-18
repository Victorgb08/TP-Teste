# testes/test_integracao_cli.py

import pytest
import subprocess
import os
import sys
import json
from uuid import UUID

# Define o nome do arquivo de teste para os testes de integração
ARQUIVO_JSON_INTEGRACAO = "tarefas_teste_integracao.json"

@pytest.fixture(autouse=True)
def setup_teardown():
    """ Fixture para limpar o arquivo JSON de teste antes e depois de cada teste. """
    if os.path.exists(ARQUIVO_JSON_INTEGRACAO):
        os.remove(ARQUIVO_JSON_INTEGRACAO)
    
    yield

    if os.path.exists(ARQUIVO_JSON_INTEGRACAO):
        os.remove(ARQUIVO_JSON_INTEGRACAO)

def executar_comando(comandos_input):
    """
    Executa o main.py como um subprocesso, fornecendo entradas e o nome do arquivo de teste.
    """
    caminho_main = os.path.join(os.path.dirname(__file__), '..', 'main.py')
    
    if "5" not in comandos_input:
        comandos_input.append("5")
        
    input_str = "\n".join(comandos_input)
    
    # Força o subprocesso a usar UTF-8 para I/O, resolvendo o problema de encoding no Windows
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    processo = subprocess.run(
        # Passa o nome do arquivo como um argumento de linha de comando
        [sys.executable, caminho_main, ARQUIVO_JSON_INTEGRACAO],
        input=input_str,
        capture_output=True,
        text=True,
        encoding='utf-8', 
        env=env, # Passa o ambiente com a correção de encoding
        timeout=10
    )
    
    if processo.returncode != 0 and processo.stderr:
        print("Erro no subprocesso:", processo.stderr)

    return processo.stdout

# OS TESTES ABAIXO PERMANECEM IGUAIS

def test_ciclo_de_vida_completo_da_tarefa():
    """
    Teste de integração E2E (end-to-end)
    """
    # --- 1. Adicionar Tarefa ---
    output_add = executar_comando(["1", "Minha Tarefa de Teste E2E", "2025-12-25"])
    assert "Tarefa 'Minha Tarefa de Teste E2E' adicionada com sucesso." in output_add

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
    """ Testa a interação do usuário ao tentar remover uma tarefa com ID inválido. """
    output = executar_comando(["4", "id-que-nao-existe"])
    assert "Erro: Tarefa com ID 'id-que-nao-existe' não encontrada para remoção." in output

def test_menu_com_opcao_invalida():
    """ Testa a resposta do menu a uma entrada inválida. """
    output = executar_comando(["99", "1", "Tarefa Teste", ""])
    assert "Opção inválida. Por favor, tente novamente." in output
    assert "Tarefa 'Tarefa Teste' adicionada com sucesso." in output

def test_persistência_entre_execucoes():
    """ Testa se uma tarefa adicionada em uma execução persiste em uma nova. """
    # Primeira execução: Adicionar a tarefa
    executar_comando(["1", "Tarefa Persistente", ""])
    
    # Segunda execução: Visualizar a tarefa
    output = executar_comando(["2"])
    assert "Tarefa Persistente" in output
    assert "Status: Pendente" in output

def test_adicionar_tarefa_com_descricao_vazia_pelo_cli():
    """
    Testa a tentativa de adicionar uma tarefa com descrição vazia ou só com espaços.
    A lógica interna deve impedir isso e o usuário deve ver uma mensagem de erro.
    """
    # Tenta adicionar uma tarefa com descrição contendo apenas espaços
    output = executar_comando(["1", "   ", "2025-01-01"]) 
    
    # Verifica se a mensagem de erro da camada de lógica é exibida na saída do CLI
    assert "Erro: A descrição da tarefa não pode ser vazia." in output
    
    # Garante que, após a falha, nenhuma tarefa foi de fato adicionada
    output_view = executar_comando(["2"])
    assert "Nenhuma tarefa cadastrada." in output_view


def test_marcar_tarefa_ja_concluida_pelo_cli():
    """
    Testa o feedback para o usuário ao tentar marcar uma tarefa que já está concluída.
    """
    # 1. Adiciona a tarefa
    executar_comando(["1", "Tarefa a ser concluída", ""])

    # 2. CORREÇÃO: Visualiza para obter o ID
    output_view = executar_comando(["2"])
    id_tarefa = ""
    for linha in output_view.splitlines():
        if "Tarefa a ser concluída" in linha:
            id_tarefa = linha.split(" | ")[0].replace("ID: ", "")
    assert id_tarefa, "Falha ao extrair ID da tarefa após visualização."

    # 3. Marca a tarefa como concluída pela primeira vez
    executar_comando(["3", id_tarefa])

    # 4. Tenta marcar a mesma tarefa como concluída novamente
    output_reattempt = executar_comando(["3", id_tarefa])

    # 5. Verifica se a mensagem de aviso correta foi exibida
    assert "já estava concluída" in output_reattempt


def test_visualizar_lista_com_multiplas_tarefas():
    """
    Testa se a aplicação exibe corretamente múltiplas tarefas.
    """
    # Adiciona três tarefas em sequência
    executar_comando(["1", "Primeira Tarefa", "2025-01-01"])
    executar_comando(["1", "Segunda Tarefa", "2025-02-01"])
    executar_comando(["1", "Terceira Tarefa", ""])

    # Visualiza a lista
    output = executar_comando(["2"])

    # Verifica se todas as tarefas estão presentes na saída
    assert "Primeira Tarefa" in output
    assert "Segunda Tarefa" in output
    assert "Terceira Tarefa" in output
    assert output.count("ID: ") == 3 # Confirma que há 3 tarefas listadas


def test_adicionar_e_remover_tarefa_do_meio():
    """
    Testa um fluxo mais complexo: adicionar 3 tarefas, remover a do meio,
    e verificar se as corretas permaneceram.
    """
    # 1. Adiciona as 3 tarefas
    executar_comando(["1", "Tarefa 1 (Manter)", ""])
    executar_comando(["1", "Tarefa 2 (Remover)", ""])
    executar_comando(["1", "Tarefa 3 (Manter)", ""])

    # 2. CORREÇÃO: Visualiza a lista para obter todos os IDs de uma vez
    output_view = executar_comando(["2"])
    ids = {}
    for linha in output_view.splitlines():
        if "ID: " in linha:
            descricao = linha.split("Descrição: ")[1].split(" | ")[0]
            task_id = linha.split(" | ")[0].replace("ID: ", "")
            ids[descricao] = task_id # Mapeia descrição para ID

    assert len(ids) == 3, "Esperava encontrar 3 tarefas na visualização."
    id_para_remover = ids.get("Tarefa 2 (Remover)")
    assert id_para_remover, "Não foi possível encontrar o ID da tarefa a ser removida."

    # 3. Remove a tarefa do meio
    executar_comando(["4", id_para_remover])

    # 4. Visualiza a lista final para verificação
    output_final = executar_comando(["2"])

    # 5. Verifica o estado final
    assert "Tarefa 1 (Manter)" in output_final
    assert "Tarefa 3 (Manter)" in output_final
    assert "Tarefa 2 (Remover)" not in output_final
    assert output_final.count("ID: ") == 2


def test_saida_imediata_do_programa():
    """
    Testa o cenário mais simples: o usuário inicia e sai imediatamente.
    """
    # O comando "5" já é adicionado automaticamente pela função `executar_comando`
    # se não estiver presente, então uma lista vazia funciona.
    output = executar_comando([]) 
    assert "Saindo do Gerenciador de Tarefas. Até logo!" in output


def test_adicionar_tarefa_com_data_vencimento_invalida_string():
    """
    Verifica como o sistema se comporta com uma data de vencimento em formato inválido.
    (Atualmente, a lógica aceita qualquer string, então o teste documenta isso).
    """
    executar_comando(["1", "Tarefa com data estranha", "isso-nao-e-uma-data"])
    
    output = executar_comando(["2"])
    
    assert "Tarefa com data estranha" in output
    assert "Vencimento: isso-nao-e-uma-data" in output