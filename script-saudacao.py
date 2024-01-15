# Script de Saudação Interativa em Python

def obter_nome_usuario():
    """Função para obter o nome do usuário."""
    nome = input("Digite seu nome: ")
    return nome

def saudar_usuario(nome):
    """Função para saudar o usuário."""
    print(f"Olá, {nome}! Bem-vindo ao nosso programa de saudação.")

if __name__ == "__main__":
    # Bloco de execução principal quando o script é executado diretamente.
    
    # Obtém o nome do usuário chamando a função.
    nome_do_usuario = obter_nome_usuario()
    
    # Sauda o usuário com base no nome fornecido.
    saudar_usuario(nome_do_usuario)
