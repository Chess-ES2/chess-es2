É preferível que toda a documentação necessária seja visualizada por meios destes links e seus redirecionamentos. Mas em caso de qualquer problema, todos os documentos e diagramas utilizados também foram baixados e adicionados na pasta /documentacao.

Documentação do Projeto: 
https://docs.google.com/document/d/1EDQCacfWvLBCjdXh_7zgwd9wqbn4b2d5PoFBhlLHu4o/edit?usp=sharing

Slides Apresentação 1:
https://canva.link/xlduro76m4e0qeo

## Como rodar (frontend + backend juntos)

Pré-requisitos: [Node.js 18+](https://nodejs.org) e [Python 3.10+](https://www.python.org/downloads/).

Na raiz do projeto:

```bash
npm run dev
```

Na primeira execução o script cria o `.venv`, instala as dependências do backend (pip) e do
frontend (npm) automaticamente. Depois é só acessar:

- Frontend: http://localhost:5173
- Backend (Flask): http://localhost:5000
- API através do frontend: http://localhost:5173/api/... (proxy do Vite para o Flask, sem CORS)
- Rede local: os mesmos serviços ficam disponíveis nos IPs da máquina (o `npm run dev` lista
  todos eles ao iniciar), por exemplo `http://<ip-da-máquina>:5173` e `http://<ip-da-máquina>:5000`

```ts
// exemplo: no frontend, "_/api" é removido ao chegar no backend
fetch('/api/partida/nova', { method: 'POST' }) // -> POST http://localhost:5000/partida/nova
```

Outros comandos:

```bash
npm run setup   # só instala as dependências (backend + frontend)
npm test        # testes do backend (pytest)
npm run build   # build de produção do frontend
npm run lint    # lint do frontend
```
