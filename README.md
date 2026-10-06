Entrega 1:
# [Documentação do Projeto](https://docs.google.com/document/d/1EDQCacfWvLBCjdXh_7zgwd9wqbn4b2d5PoFBhlLHu4o/edit?usp=sharing)
# [Slides-Apresentação-1](https://canva.link/xlduro76m4e0qeo)
# [EAP](https://miro.com/welcomeonboard/bjVoRWl0V0xnYjVnQWt2TmJhYW81cDZqeUxjaUV4VWtBR25JckplSlczemdyejIrejZ0UnBiUHppaEhTaUptZ0NQYjNsM2x3RDNGbTI3MXJWNDJFQStqclVtd3BKc3hyeWxodjFscTlVVFV1YXlxQXhQOGVQb2UxU1hOaVkrQnl0R2lncW1vRmFBVnlLcVJzTmdFdlNRPT0hdjE=?share_link_id=919471880283)
# [Planning-Poker](https://docs.google.com/spreadsheets/d/1Yz6jbonyVkHRdsvSAaqtGTZrwQl84KrsC02DeMmMkWo/edit?gid=743590422#gid=743590422&range=A1:C49)
# [Cronograma-Gannt](https://docs.google.com/spreadsheets/d/1SOWDvGxckjB0B3mOY98AnQBcsC7bbVxy6Q-bGrFTeFM/edit?gid=1578635526#gid=1578635526)

Entrega 2:
# [Slides-Apresentação-2](https://www.canva.com/design/DAHW-cChu10/zdGLB3z2tCbWna195MAFiA/edit)
# [Gráfico AVA](https://docs.google.com/spreadsheets/d/1JaM0zrvAG_xRMVr6tqbV3LSPicThSVG_gpZtkAw7rlY/edit?usp=sharing)

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
