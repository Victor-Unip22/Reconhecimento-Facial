import tkinter as tk
import cv2
import os
import sqlite3
import numpy as np

# Conectar ao banco de dados (ou criar um novo)
conn = sqlite3.connect('usuarios.db')
c = conn.cursor()

# Criar tabela se não existir
c.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY,
    nome TEXT,
    email TEXT,
    numero TEXT,
    caminho_fotos TEXT
)
''')
conn.commit()

# Função para capturar fotos
def capturar_foto(usuario_nome):
    caminho_diretorio = "imagens/" + usuario_nome
    if not os.path.exists(caminho_diretorio):
        os.makedirs(caminho_diretorio)
    
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Capturar Foto")
    contador = 0

    while contador < 10:
        ret, frame = cam.read()
        if not ret:
            print("Falha ao capturar a imagem")
            break
        cv2.imshow("Capturar Foto", frame)
        
        k = cv2.waitKey(1)
        if k % 256 == 27:  # ESC
            print("Fechando sem salvar.")
            break
        elif k % 256 == 32:  # SPACE
            img_name = f"{caminho_diretorio}/foto_{contador}.png"
            cv2.imwrite(img_name, frame)
            print(f"Foto {img_name} salva!")
            contador += 1
    
    cam.release()
    cv2.destroyAllWindows()
    
    return caminho_diretorio

# Função para cadastrar o usuário no banco de dados
def cadastrar_usuario():
    nome = entry_nome.get()
    email = entry_email.get()
    numero = entry_numero.get()
    
    # Capturar fotos do usuário
    caminho_fotos = capturar_foto(nome)
    
    # Armazenar dados no banco de dados
    c.execute('INSERT INTO usuarios (nome, email, numero, caminho_fotos) VALUES (?, ?, ?, ?)', 
              (nome, email, numero, caminho_fotos))
    conn.commit()
    print(f"Usuário cadastrado: {nome}, {email}, {numero}, Fotos armazenadas em: {caminho_fotos}")

# Função para treinar o reconhecimento facial
def login_reconhecimento_facial(caminho_imagens):
    caminho_haarcascade = r'C:\Users\victo\Documents\UNIP\APS 6 Semestre_CC\.venv\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml'
    classificador = cv2.CascadeClassifier(caminho_haarcascade)

    if classificador.empty():
        raise FileNotFoundError("Arquivo haarcascade_frontalface_default.xml não encontrado. Verifique o caminho.")
    
    rostos = []
    rosto_ids = []

    for usuario_id, usuario in enumerate(os.listdir(caminho_imagens)):
        for imagem_nome in os.listdir(os.path.join(caminho_imagens, usuario)):
            imagem_path = os.path.join(caminho_imagens, usuario, imagem_nome)
            imagem = cv2.imread(imagem_path)

            if imagem is None:
                print(f"Imagem não carregada: {imagem_path}")
                continue
            
            imagem_gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
            rostos_detectados = classificador.detectMultiScale(imagem_gray, scaleFactor=1.3, minNeighbors=5)

            for (x, y, w, h) in rostos_detectados:
                rostos.append(imagem_gray[y:y+h, x:x+w])
                rosto_ids.append(usuario_id)

    if len(rostos) > 0:
        reconhecedor = cv2.face.LBPHFaceRecognizer_create()
        reconhecedor.train(rostos, np.array(rosto_ids))
        reconhecedor.save('modelo_reconhecimento.xml')
        print("Modelo treinado e salvo com sucesso.")
    else:
        print("Nenhum rosto detectado para treinamento.")

# Função para fazer login com reconhecimento facial
def login_reconhecimento_facial_usuario():
    print("Iniciando o reconhecimento facial...")
    reconhecedor = cv2.face.LBPHFaceRecognizer_create()
    reconhecedor.read('modelo_reconhecimento.xml')
    print("Modelo carregado com sucesso.")

    classificador = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Reconhecimento Facial")

    while True:
        print("Capturando imagem para reconhecimento...")
        ret, frame = cam.read()
        if not ret:
            print("Falha ao capturar a imagem")
            break

        imagem_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostos_detectados = classificador.detectMultiScale(imagem_gray, scaleFactor=1.3, minNeighbors=5)

        if len(rostos_detectados) == 0:
            print("Nenhum rosto detectado.")

        for (x, y, w, h) in rostos_detectados:
            id_usuario, confianca = reconhecedor.predict(imagem_gray[y:y+h, x:x+w])
            print(f"ID do usuário detectado: {id_usuario}, Confiança: {confianca}")

            # Alterado para imprimir o ID antes de consultar o nome
            print(f"ID do usuário reconhecido: {id_usuario}")

            # Verificar se o ID do usuário é válido e consultar o nome
            if confianca < 50:  # Ajuste o limiar de confiança aqui
                c.execute("SELECT nome FROM usuarios WHERE id=?", (id_usuario,))
                resultado = c.fetchone()
                if resultado:
                    nome_usuario = resultado[0]
                    print(f"Usuário reconhecido: {nome_usuario}")
                    cv2.putText(frame, f'Bem-vindo {nome_usuario}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                else:
                    print("Usuário desconhecido para o ID fornecido.")
                    cv2.putText(frame, 'Usuario desconhecido', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                print("Confiança alta. Usuário desconhecido.")
                cv2.putText(frame, 'Usuario desconhecido', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Reconhecimento Facial", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:  # ESC
            print("Fechando.")
            break

    cam.release()
    cv2.destroyAllWindows()

# Criação da janela principal
root = tk.Tk()
root.title("Cadastro de Usuário com Reconhecimento Facial")

# Labels e Entradas
label_nome = tk.Label(root, text="Nome:")
label_nome.grid(row=0, column=0, padx=10, pady=10)
entry_nome = tk.Entry(root)
entry_nome.grid(row=0, column=1, padx=10, pady=10)

label_email = tk.Label(root, text="E-mail:")
label_email.grid(row=1, column=0, padx=10, pady=10)
entry_email = tk.Entry(root)
entry_email.grid(row=1, column=1, padx=10, pady=10)

label_numero = tk.Label(root, text="Número:")
label_numero.grid(row=2, column=0, padx=10, pady=10)
entry_numero = tk.Entry(root)
entry_numero.grid(row=2, column=1, padx=10, pady=10)

# Botão para cadastrar o usuário
btn_cadastrar = tk.Button(root, text="Cadastrar", command=cadastrar_usuario)
btn_cadastrar.grid(row=3, column=1, padx=10, pady=10)

# Botão para treinar reconhecimento facial
btn_treinar = tk.Button(root, text="Treinar Reconhecimento", command=lambda: login_reconhecimento_facial('imagens/'))
btn_treinar.grid(row=4, column=1, padx=10, pady=10)

# Botão para reconhecer usuário
btn_reconhecer = tk.Button(root, text="Reconhecer Usuário", command=login_reconhecimento_facial_usuario)
btn_reconhecer.grid(row=5, column=1, padx=10, pady=10)

# Iniciar o loop da interface gráfica
root.mainloop()
