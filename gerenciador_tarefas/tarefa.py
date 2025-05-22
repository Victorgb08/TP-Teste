# gerenciador_tarefas/tarefa.py

import uuid

class Tarefa:
    """
    Representa uma tarefa individual no sistema.
    """
    def __init__(self, descricao, data_vencimento=None, id_tarefa=None, concluida=False):
        """
        Inicializa uma nova tarefa.

        Args:
            descricao (str): A descrição da tarefa.
            data_vencimento (str, optional): A data de vencimento da tarefa (formato YYYY-MM-DD). 
                                            Defaults to None.
            id_tarefa (str, optional): O ID único da tarefa. Se None, um novo UUID será gerado.
                                     Defaults to None.
            concluida (bool, optional): O status de conclusão da tarefa. Defaults to False.
        
        Raises:
            ValueError: Se a descrição não for uma string ou se estiver vazia após remover espaços em branco.
        """
        if not isinstance(descricao, str):
            raise ValueError("A descrição da tarefa deve ser uma string.")
        
        desc_stripped = descricao.strip()
        if not desc_stripped:
            raise ValueError("A descrição da tarefa não pode ser vazia.")

        self.id = id_tarefa if id_tarefa else str(uuid.uuid4())
        self.descricao = desc_stripped

        # MODIFICATION START
        if isinstance(data_vencimento, str):
            stripped_date = data_vencimento.strip()
            self.data_vencimento = stripped_date if stripped_date else None
        else:
            self.data_vencimento = data_vencimento # Handles if it's already None or other types
        # MODIFICATION END
        
        self.concluida = concluida

    def marcar_como_concluida(self):
        """Marca a tarefa como concluída."""
        self.concluida = True

    def marcar_como_pendente(self):
        """Marca a tarefa como pendente."""
        self.concluida = False

    def __str__(self):
        """
        Retorna uma representação em string da tarefa.
        """
        status = "Concluída" if self.concluida else "Pendente"
        data_str = f", Vencimento: {self.data_vencimento}" if self.data_vencimento else ""
        return f"ID: {self.id} | Descrição: {self.descricao}{data_str} | Status: {status}"

    def to_dict(self):
        """
        Converte o objeto Tarefa para um dicionário, útil para serialização JSON.
        """
        return {
            "id": self.id,
            "descricao": self.descricao,
            "data_vencimento": self.data_vencimento,
            "concluida": self.concluida,
        }

    @classmethod
    def from_dict(cls, data_dict):
        """
        Cria um objeto Tarefa a partir de um dicionário.

        Args:
            data_dict (dict): Dicionário contendo os dados da tarefa.
        
        Returns:
            Tarefa: Uma instância da classe Tarefa.

        Raises:
            ValueError: Se os dados de entrada não forem um dicionário, ou se a descrição
                        for inválida conforme as regras do construtor.
        """
        if not isinstance(data_dict, dict):
            raise ValueError("Os dados de entrada devem ser um dicionário.")
        
        # A validação da descrição (incluindo se é None, vazia, ou só espaços)
        # será tratada pelo construtor __init__
        return cls(
            descricao=data_dict.get("descricao"),
            data_vencimento=data_dict.get("data_vencimento"),
            id_tarefa=data_dict.get("id"),
            concluida=data_dict.get("concluida", False), # Default para False se não presente
        )