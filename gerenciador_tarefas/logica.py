# gerenciador_tarefas/logica.py

import json
from .tarefa import Tarefa

class GerenciadorDeTarefas:
    """
    Gerencia a coleção de tarefas, permitindo adicionar, remover,
    visualizar e modificar tarefas.
    """
    def __init__(self, arquivo_json="tarefas.json"):
        """
        Inicializa o gerenciador de tarefas.
        Tenta carregar tarefas de um arquivo JSON, se existir.

        Args:
            arquivo_json (str, optional): Nome do arquivo JSON para persistência.
                                         Defaults to "tarefas.json".
        """
        self.tarefas = []
        self.arquivo_json = arquivo_json
        self._carregar_tarefas()

    def adicionar_tarefa(self, descricao, data_vencimento=None):
        """
        Adiciona uma nova tarefa à lista.

        Args:
            descricao (str): A descrição da tarefa.
            data_vencimento (str, optional): Data de vencimento (YYYY-MM-DD). Defaults to None.

        Returns:
            Tarefa: O objeto Tarefa criado e adicionado, ou None se a descrição for inválida.
        """
        if not descricao or not isinstance(descricao, str) or not descricao.strip():
            print("Erro: A descrição da tarefa não pode ser vazia.")
            return None
        try:
            nova_tarefa = Tarefa(descricao.strip(), data_vencimento)
            self.tarefas.append(nova_tarefa)
            self._salvar_tarefas()
            print(f"Tarefa '{nova_tarefa.descricao}' adicionada com sucesso.")
            return nova_tarefa
        except ValueError as e:
            print(f"Erro ao criar tarefa: {e}")
            return None


    def visualizar_tarefas(self, mostrar_concluidas=True, mostrar_pendentes=True):
        """
        Retorna uma lista de strings representando as tarefas.

        Args:
            mostrar_concluidas (bool): Se True, inclui tarefas concluídas.
            mostrar_pendentes (bool): Se True, inclui tarefas pendentes.
        
        Returns:
            list: Lista de strings, cada uma representando uma tarefa.
                  Retorna uma lista com uma mensagem se não houver tarefas.
        """
        if not self.tarefas:
            return ["Nenhuma tarefa cadastrada."]

        tarefas_filtradas = []
        for tarefa in self.tarefas:
            if (mostrar_concluidas and tarefa.concluida) or \
               (mostrar_pendentes and not tarefa.concluida):
                tarefas_filtradas.append(str(tarefa))
        
        if not tarefas_filtradas:
            return ["Nenhuma tarefa corresponde aos critérios de filtro."]
            
        return tarefas_filtradas

    def encontrar_tarefa_por_id(self, id_tarefa):
        """
        Encontra uma tarefa pelo seu ID.

        Args:
            id_tarefa (str): O ID da tarefa a ser encontrada.

        Returns:
            Tarefa or None: O objeto Tarefa se encontrado, caso contrário None.
        """
        if not id_tarefa or not isinstance(id_tarefa, str):
            return None
        for tarefa in self.tarefas:
            if tarefa.id == id_tarefa:
                return tarefa
        return None

    def marcar_tarefa_como_concluida(self, id_tarefa):
        """
        Marca uma tarefa como concluída.

        Args:
            id_tarefa (str): O ID da tarefa a ser marcada.

        Returns:
            bool: True se a tarefa foi marcada com sucesso, False caso contrário.
        """
        tarefa = self.encontrar_tarefa_por_id(id_tarefa)
        if tarefa:
            if not tarefa.concluida:
                tarefa.marcar_como_concluida()
                self._salvar_tarefas()
                print(f"Tarefa '{tarefa.descricao}' marcada como concluída.")
                return True
            else:
                print(f"Tarefa '{tarefa.descricao}' já estava concluída.")
                return False
        else:
            print(f"Erro: Tarefa com ID '{id_tarefa}' não encontrada.")
            return False

    def remover_tarefa(self, id_tarefa):
        """
        Remove uma tarefa da lista.

        Args:
            id_tarefa (str): O ID da tarefa a ser removida.

        Returns:
            bool: True se a tarefa foi removida com sucesso, False caso contrário.
        """
        tarefa = self.encontrar_tarefa_por_id(id_tarefa)
        if tarefa:
            self.tarefas.remove(tarefa)
            self._salvar_tarefas()
            print(f"Tarefa '{tarefa.descricao}' removida com sucesso.")
            return True
        else:
            print(f"Erro: Tarefa com ID '{id_tarefa}' não encontrada para remoção.")
            return False

    def _salvar_tarefas(self):
        """
        Salva a lista de tarefas em um arquivo JSON.
        Método privado.
        """
        try:
            with open(self.arquivo_json, "w", encoding="utf-8") as f:
                json.dump([tarefa.to_dict() for tarefa in self.tarefas], f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erro de E/S ao salvar tarefas em {self.arquivo_json}: {e}")


    def _carregar_tarefas(self):
        """
        Carrega a lista de tarefas de um arquivo JSON.
        Método privado.
        """
        try:
            with open(self.arquivo_json, "r", encoding="utf-8") as f:
                tarefas_data = json.load(f)
                
                if not isinstance(tarefas_data, list):
                    print(f"Erro: O conteúdo do arquivo {self.arquivo_json} não é uma lista JSON válida. Iniciando com lista vazia.")
                    self.tarefas = []
                    return

                novas_tarefas = []
                for data in tarefas_data:
                    try:
                        novas_tarefas.append(Tarefa.from_dict(data))
                    except ValueError as ve:
                        print(f"Erro nos dados ao carregar uma tarefa do arquivo {self.arquivo_json}: {ve}. Tarefa ignorada.")
                self.tarefas = novas_tarefas
            
            if self.tarefas or (not self.tarefas and isinstance(tarefas_data, list) and not tarefas_data): # Se carregou tarefas ou o arquivo era uma lista vazia
                 print(f"Tarefas carregadas de {self.arquivo_json}")

        except FileNotFoundError:
            print(f"Arquivo {self.arquivo_json} não encontrado. Iniciando com lista de tarefas vazia.")
            self.tarefas = []
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Erro ao decodificar JSON do arquivo {self.arquivo_json}: {e}. Iniciando com lista vazia.")
            self.tarefas = []
        except IOError as e: 
            print(f"Erro de E/S ao tentar ler o arquivo {self.arquivo_json}: {e}. Iniciando com lista vazia.")
            self.tarefas = []
            
    def limpar_todas_as_tarefas(self):
        """
        Remove todas as tarefas da lista e do arquivo de persistência.
        Útil para testes ou para resetar o estado.
        """
        self.tarefas = []
        self._salvar_tarefas() 
        print("Todas as tarefas foram removidas.")