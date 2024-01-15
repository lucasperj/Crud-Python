import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# Cria um banco de dados SQLite em memória
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT
    )
''')
conn.commit()

class CRUDHandler(BaseHTTPRequestHandler):
    def _send_response(self, status_code, body=''):
        # Função para enviar a resposta HTTP ao cliente
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def _renderizar_botoes(self, item_id):
        # Função para gerar HTML dos botões de editar e excluir
        botoes_html = f"""
            <a href="/editar/{item_id}"><button>Editar</button></a>
            <a href="/remover/{item_id}"><button>Excluir</button></a>
        """
        return botoes_html

    def _listar_itens_com_botoes(self):
        # Função para renderizar a lista de itens com botões
        self._send_response(200, body='<html><head><title>Lista de Colaboradores</title></head><body style="text-align:center; margin-top:50px; font-family: Arial, sans-serif;"><h1 style="font-size:36px;">Lista de Colaboradores</h1>')
        cursor.execute('SELECT id, nome FROM itens')
        for row in cursor.fetchall():
            item_id, nome = row[0], row[1]
            botoes_html = self._renderizar_botoes(item_id)
            self.wfile.write(f'<p style="font-size:18px;">{item_id}: {nome} - {botoes_html}</p>'.encode('utf-8'))
        adicionar_botao_html = '<a href="/adicionar"><button style="font-size:18px;">Adicionar Novo</button></a>'
        self.wfile.write(f'<br><br>{adicionar_botao_html}</body></html>'.encode('utf-8'))

    def _renderizar_formulario_adicao(self):
        # Função para renderizar o formulário de adição de item
        adicionar_html = '''
            <html>
            <head>
                <title>Adicionar Colaborador</title>
            </head>
            <body style="text-align:center; margin-top:50px; font-family: Arial, sans-serif;">
                <h1 style="font-size:36px;">Adicionar Colaborador</h1>
                <form method="POST" action="/adicionar">
                    <label style="font-size:18px;">Nome:</label> <input type="text" name="nome" required><br><br>
                    <button type="submit" style="font-size:18px;">Adicionar</button>
                </form>
                <br>
                <a href="/listar"><button style="font-size:18px;">Voltar para Lista</button></a>
            </body>
            </html>
        '''
        self._send_response(200, body=adicionar_html)

    def _adicionar_item(self, nome):
        # Função para adicionar um item ao banco de dados
        cursor.execute('INSERT INTO itens (nome) VALUES (?)', (nome,))
        conn.commit()

    def _renderizar_formulario_edicao(self, item_id):
        # Função para renderizar o formulário de edição de item
        cursor.execute('SELECT nome FROM itens WHERE id = ?', (item_id,))
        result = cursor.fetchone()
        if result:
            nome_atual = result[0]
            editar_html = f'''
                <html>
                <head>
                    <title>Editar Colaborador</title>
                </head>
                <body style="text-align:center; margin-top:50px; font-family: Arial, sans-serif;">
                    <h1 style="font-size:36px;">Editar Colaborador</h1>
                    <p style="font-size:18px;">Nome atual: {nome_atual}</p>
                    <form method="POST" action="/editar/{item_id}">
                        <label style="font-size:18px;">Novo Nome:</label> <input type="text" name="novo_nome" required><br><br>
                        <button type="submit" style="font-size:18px;">Salvar</button>
                    </form>
                    <br>
                    <a href="/listar"><button style="font-size:18px;">Voltar para Lista</button></a>
                </body>
                </html>
            '''
            self._send_response(200, body=editar_html)
        else:
            self._send_response(404, body='Colaborador não encontrado')

    def _editar_item(self, item_id, novo_nome):
        # Função para editar um item no banco de dados
        cursor.execute('UPDATE itens SET nome = ? WHERE id = ?', (novo_nome, item_id))
        conn.commit()

    def _remover_item(self, item_id):
        # Função para remover um item do banco de dados
        cursor.execute('DELETE FROM itens WHERE id = ?', (item_id,))
        conn.commit()

    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == '/listar':
            self._listar_itens_com_botoes()
        elif parsed_url.path == '/adicionar':
            self._renderizar_formulario_adicao()
        elif parsed_url.path.startswith('/editar'):
            item_id = int(parsed_url.path.split('/')[2])
            self._renderizar_formulario_edicao(item_id)
        elif parsed_url.path.startswith('/remover'):
            item_id = int(parsed_url.path.split('/')[2])
            self._remover_item(item_id)
            self._listar_itens_com_botoes()
        else:
            self._send_response(404, body='Página não encontrada')

    def do_POST(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == '/adicionar':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = parse_qs(post_data)

            nome = parsed_data.get('nome', [''])[0]

            self._adicionar_item(nome)
            self._listar_itens_com_botoes()
        elif parsed_url.path.startswith('/editar'):
            item_id = int(parsed_url.path.split('/')[2])
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = parse_qs(post_data)

            novo_nome = parsed_data.get('novo_nome', [''])[0]

            self._editar_item(item_id, novo_nome)
            self._listar_itens_com_botoes()
        else:
            self._send_response(404, body='Página não encontrada')

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CRUDHandler)
    print('Servidor rodando em http://localhost:8000/')
    httpd.serve_forever()
