# Gerenciador de Tarefas Simples (CLI)

## 1. Membros do Grupo

- Victor Guedes Batista
- João Pedro Maduro Menezes

## 2. Explicação do Sistema

Este é um sistema de Gerenciador de Tarefas simples que opera através da linha de comando (CLI). Ele permite aos usuários adicionar, visualizar, marcar como concluídas e remover tarefas. As tarefas são armazenadas em memória durante a execução do programa, com a opção de salvar e carregar tarefas de um arquivo JSON para persistência de dados entre sessões.

### Funcionalidades Principais:

- **Adicionar Tarefa:** Permite ao usuário adicionar uma nova tarefa com uma descrição e, opcionalmente, uma data de vencimento.
- **Visualizar Tarefas:** Lista todas as tarefas existentes, mostrando seu ID, descrição, data de vencimento (se houver) e status (pendente/concluída).
- **Marcar Tarefa como Concluída:** Permite ao usuário marcar uma tarefa específica como concluída, utilizando seu ID.
- **Remover Tarefa:** Permite ao usuário remover uma tarefa específica da lista, utilizando seu ID.
- **Salvar Tarefas:** Salva o estado atual das tarefas em um arquivo `tarefas.json`.
- **Carregar Tarefas:** Carrega as tarefas de um arquivo `tarefas.json` ao iniciar o programa, se o arquivo existir.

## 3. Tecnologias Utilizadas

- **Linguagem de Programação:** Python 3.x
- **Testes:** Pytest (framework de testes para Python)
- **CI/CD:** GitHub Actions (para automação da execução dos testes em diferentes sistemas operacionais a cada commit)
- **Formato de Dados (Persistência):** JSON (para salvar e carregar tarefas)
- **Controle de Versão:** Git e GitHub

## 4. Cobertura de Testes

A cobertura de testes é mensurada com Coverage.py e os relatórios são publicados automaticamente no [Codecov](https://codecov.io/).

[![codecov](https://codecov.io/gh/Victorgb08/TP-Teste/branch/main/graph/badge.svg)](https://codecov.io/gh/Victorgb08/TP-Teste)
