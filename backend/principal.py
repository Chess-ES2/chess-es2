from api.rotas import app

if __name__ == "__main__":
    print("Motor de Xadrez — Backend Flask")
    print("Servidor iniciando em http://localhost:5000")
    print("Pressione Ctrl+C para encerrar.\n")
    app.run(debug=True, port=5000)
