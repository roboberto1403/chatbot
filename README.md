# 🏥 ClinicAI - Assistente de Triagem Médica

O **ClinicAI** é um chatbot inteligente desenvolvido para realizar **triagem médica inicial**.  
Ele **não substitui o diagnóstico médico**, mas ajuda a coletar informações estruturadas que aceleram o atendimento clínico.

---

## 🚀 Funcionalidades

- ✅ Conduz triagem inicial com coleta estruturada de informações:  
  - Queixa principal  
  - Sintomas detalhados  
  - Duração/frequência  
  - Intensidade (0-10)  
  - Histórico relevante  
  - Medidas tomadas  

- ✅ Detecta **sintomas de emergência** (ex: dor no peito, falta de ar, sangramento intenso) e orienta o paciente a procurar ajuda imediata.  

- ✅ Gera um **resumo final estruturado** e pede confirmação ao paciente.  
  - Se confirmado → triagem é encerrada e marcada como concluída.  
  - Se emergência → atendimento é interrompido e alerta é emitido.  

- ✅ Integração com **MongoDB** para armazenar chats, histórico de triagem e status.  

- ✅ API construída em **FastAPI**, pronta para integrar com frontend.  

---

## ⚙️ Tecnologias

- [FastAPI](https://fastapi.tiangolo.com/) - API backend  
- [LangGraph](https://python.langchain.com/docs/langgraph) - Orquestração de fluxo conversacional  
- [Google Gemini](https://ai.google.dev/) - LLM usado para gerar respostas  
- [MongoDB](https://www.mongodb.com/) - Banco de dados  
- Python 3.10+  

---
## 🧩 Funcionamento do Grafo

O fluxo do **LangGraph** garante que o chatbot siga regras rígidas de triagem:

1. **chatbot** → Interage com o usuário e coleta dados.  
   - Gera JSON com `next_response` e `triagem_data`.  
   - Se usuário confirmar resumo → seta `resumo_confirmado = True`.

2. **router_emergency** → Checa se houve palavras-chave de emergência.  
   - Se detectado → vai para `emergency_protocol`.  
   - Caso contrário → segue para `end_or_continue`.

3. **emergency_protocol** → Emite alerta 🚨 e encerra triagem.

4. **end_or_continue** → Decide entre:  
   - Encerrar (se resumo confirmado ou limite de turnos alcançado).  
   - Voltar ao `chatbot` para coletar mais informações.  

---

## 🖼️ Visualização do Grafo

<img width="1900" height="1318" alt="image" src="https://github.com/user-attachments/assets/8cc07c68-a0b5-4732-aefc-0e4dfdf2f66b" />

---

## ▶️ Como Rodar Localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/roboberto1403/chatbot.git
   cd chatbot
   
2.  Crie e ambiente virtual:
   ```bash
   cd server
   python -m venv venv

3. Instale as dependências:
  ```bash
  pip install -r requirements.txt
  cd ..
  npm install

4. Configure as variáveis de ambiente em .env:
  ```bash
  GOOGLE_API_KEY="sua_chave"
  MONGODB_URI="sua_uri"

5. Inicie a API
  ```bash
  cd server
  venv\Scripts\activate
  uvicorn main:app --reload

6. Exponha o servidor com o Ngrok e configure a rota gerada em API_URL dentro do arquivo app.json
  ```bash
  ngrok http 8000

7. Rode o Expo
  ```bash
  npm start

---

## 🚧 Limitações

   - A funcionalidade de identificação de palavras de emergência apresenta inconsistências.

   - É possível identificar alguns bugs visuais que não atrapalham a experiência de forma grave.

## 📝 Licença

Este projeto está sob a licença [MIT license](https://opensource.org/licenses/MIT).

---
