# main.py

from gerenciador_tarefas.logica import GerenciadorDeTarefas

def exibir_menu():
    """Exibe o menu de opções para o usuário."""
    print("\n--- Gerenciador de Tarefas ---")
    print("1. Adicionar Tarefa")
    print("2. Visualizar Tarefas")
    print("3. Marcar Tarefa como Concluída")
    print("4. Remover Tarefa")
    print("5. Sair")
    print("------------------------------")

def main():
    """Função principal que executa o loop da aplicação CLI."""
    gerenciador = GerenciadorDeTarefas()

    while True:
        exibir_menu()
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            descricao = input("Digite a descrição da tarefa: ")
            data_vencimento = input("Digite a data de vencimento (YYYY-MM-DD, opcional, deixe em branco se não houver): ")
            data_vencimento = data_vencimento if data_vencimento.strip() else None
            gerenciador.adicionar_tarefa(descricao, data_vencimento)
        
        elif escolha == "2":
            print("\n--- Lista de Tarefas ---")
            tarefas_str = gerenciador.visualizar_tarefas()
            # A função visualizar_tarefas já retorna uma lista com mensagens apropriadas
            # se não houver tarefas, então podemos simplesmente iterar e imprimir.
            for t_str in tarefas_str:
                print(t_str)
            print("------------------------")

        elif escolha == "3":
            id_tarefa = input("Digite o ID da tarefa a ser marcada como concluída: ")
            gerenciador.marcar_tarefa_como_concluida(id_tarefa)

        elif escolha == "4":
            id_tarefa = input("Digite o ID da tarefa a ser removida: ")
            gerenciador.remover_tarefa(id_tarefa)

        elif escolha == "5":
            print("Saindo do Gerenciador de Tarefas. Até logo!")
            break
        
        else:
            print("Opção inválida. Por favor, tente novamente.")

if __name__ == "__main__":
    main()