import os

from api.rotas import app

if __name__ == "__main__":
    # HOST=0.0.0.0 deixa o backend acessível em todos os IPs locais da máquina
    # (ex.: http://<ip-da-máquina>:5000). Pode sobrescrever com as variáveis HOST e PORT.
    host = os.environ.get("HOST", "0.0.0.0")
    porta = int(os.environ.get("PORT", "5000"))

    print("Motor de Xadrez — Backend Flask")
    print(f"Servidor iniciando em http://localhost:{porta} (rede local: porta {porta})")
    print("Pressione Ctrl+C para encerrar.\n")
    app.run(debug=True, host=host, port=porta)
