import os
from google import genai

def list_available_gemini_models():
    """Lista modelos relevantes disponíveis para o seu cliente API."""
    
    # IMPORTANTE: Garanta que sua chave de API esteja definida corretamente aqui ou no ambiente.
    # Se você optou por definir no código, insira-a abaixo:
    api_key = "AIzaSyCgZdIBfD15xmolttEk0RS-3r6gfu4sIu8" 
    
    if not api_key:
        print("Erro: A variável de ambiente GOOGLE_API_KEY não foi encontrada.")
        return

    try:
        client = genai.Client(api_key=api_key)
        
        print("Modelos disponíveis (filtrados por Gemini e Modelos de Geração):\n")
        
        relevant_models = []
        for model in client.models.list():
            model_name = model.name.split('/')[-1]
            
            # Filtro simplificado: Inclui modelos Gemini, de chat e de geração de conteúdo.
            # Excluímos modelos de embedding ou de imagem (como 'aistudio-v2').
            if "gemini" in model_name or "chat" in model_name or "generate" in model_name:
                 # Evita duplicidade se o nome curto for igual ao nome longo
                if model_name not in relevant_models:
                    relevant_models.append((model_name, model.name))

        if not relevant_models:
            print("Nenhum modelo Gemini ou de geração de conteúdo encontrado.")
            return

        for short_name, full_name in relevant_models:
            print(f"- Nome Curto para Uso: {short_name} (Nome Completo: {full_name})")
                
    except Exception as e:
        print(f"Erro inesperado no cliente da API. Verifique sua chave de API novamente: {e}")

if __name__ == "__main__":
    list_available_gemini_models()