# Reconhecimento-Facial

# Tutorial de Configuração
Este tutorial orienta como configurar o ambiente necessário para executar o código do sistema de reconhecimento facial.

# Passo 1: Criar e Ativar um Ambiente Virtual
Criar o Ambiente Virtual: Abra o terminal (ou o prompt de comando) e navegue até a pasta do seu projeto. Execute o seguinte comando para criar um ambiente virtual:

python -m venv .venv
Windows: .venv\Scripts\activate
Mac/Linux: source .venv/bin/activate

# Passo 2: Instalar as Bibliotecas Necessárias
pip install opencv-python
pip install numpy
pip install dlib
pip install opencv-contrib-python

# Passo 3: Configurar o Caminho do Classificador
O código utiliza um arquivo XML para o reconhecimento facial. Caso encontre erros relacionados ao caminho do arquivo haarcascade_frontalface_default.xml, você pode precisar alterar o caminho absoluto no código.

No seu código, localize a seguinte linha: 
caminho_haarcascade = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

Substitua-a por:
caminho_haarcascade = 'C:/caminho/absoluto/para/o/arquivo/haarcascade_frontalface_default.xml'

Certifique-se de alterar 'C:/caminho/absoluto/para/o/arquivo/' para o caminho real onde o arquivo XML está localizado no seu sistem

# Solução de Problemas
Erro ao Carregar o Classificador: Certifique-se de que o caminho do arquivo XML está correto e que o arquivo existe.

Problemas de Importação: Verifique se o ambiente virtual está ativado e se todas as bibliotecas foram instaladas corretamente.
