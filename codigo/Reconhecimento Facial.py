import tkinter as tk
from tkinter import messagebox, ttk
import cv2
import os
import sqlite3
import numpy as np
from datetime import datetime

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

# Funções para captura de fotos e cadastro do usuário
def criar_diretorio(caminho):
    if not os.path.exists(caminho):
        os.makedirs(caminho)

def capturar_foto(usuario_nome):
    caminho_diretorio = "imagens/" + usuario_nome
    criar_diretorio(caminho_diretorio)

    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Capturar Foto")
    contador = 0

    while contador < 10:
        ret, frame = cam.read()
        if not ret:
            break
        cv2.imshow("Capturar Foto", frame)

        k = cv2.waitKey(1)
        if k % 256 == 32:  # Espaço para capturar
            img_name = f"{caminho_diretorio}/foto_{contador}.png"
            cv2.imwrite(img_name, frame)
            contador += 1

    cam.release()
    cv2.destroyAllWindows()
    return caminho_diretorio

def cadastrar_usuario():
    nome = entry_nome.get()
    email = entry_email.get()
    numero = entry_numero.get()

    if not nome or not email or not numero:
        messagebox.showwarning("Campos Vazios", "Por favor, preencha todos os campos.")
        return

    caminho_fotos = capturar_foto(nome)
    c.execute('INSERT INTO usuarios (nome, email, numero, caminho_fotos) VALUES (?, ?, ?, ?)',
              (nome, email, numero, caminho_fotos))
    conn.commit()
    messagebox.showinfo("Cadastro", f"Usuário {nome} cadastrado com sucesso!")

def login_reconhecimento_facial(caminho_imagens):
    caminho_haarcascade = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    classificador = cv2.CascadeClassifier(caminho_haarcascade)

    rostos = []
    rosto_ids = []

    c.execute("SELECT id, nome FROM usuarios")
    usuarios = c.fetchall()

    for usuario_id, usuario_nome in usuarios:
        caminho_usuario = os.path.join(caminho_imagens, usuario_nome)
        if os.path.exists(caminho_usuario):
            for imagem_nome in os.listdir(caminho_usuario):
                imagem_path = os.path.join(caminho_usuario, imagem_nome)
                imagem = cv2.imread(imagem_path)

                if imagem is None:
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
        messagebox.showinfo("Treinamento", "Modelo treinado com sucesso.")

def login_reconhecimento_facial_usuario():
    reconhecedor = cv2.face.LBPHFaceRecognizer_create()
    reconhecedor.read('modelo_reconhecimento.xml')
    classificador = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Reconhecimento Facial")

    # Mensagem de leitura
    cv2.putText(cam.read()[1], 'Posicione-se para o reconhecimento facial...', (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    for i in range(3, 0, -1):  # Contagem regressiva
        cv2.putText(cam.read()[1], f'Reconhecimento em: {i}', (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow("Reconhecimento Facial", cam.read()[1])
        cv2.waitKey(1000)

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        imagem_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostos_detectados = classificador.detectMultiScale(imagem_gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in rostos_detectados:
            id_usuario, confianca = reconhecedor.predict(imagem_gray[y:y+h, x:x+w])
            if confianca < 60:
                c.execute("SELECT nome FROM usuarios WHERE id=?", (id_usuario,))
                resultado = c.fetchone()
                if resultado:
                    nome_usuario = resultado[0]
                    mostrar_tela_boas_vindas(nome_usuario)
                    cam.release()
                    cv2.destroyAllWindows()
                    return
            else:
                cv2.putText(frame, 'Usuario desconhecido', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Reconhecimento Facial", frame)
        if cv2.waitKey(1) % 256 == 27:
            break

    cam.release()
    cv2.destroyAllWindows()

def mostrar_tela_boas_vindas(nome_usuario):
    # Cria uma nova janela de boas-vindas
    welcome_window = tk.Toplevel()
    welcome_window.title("Bem-vindo")
    welcome_window.geometry("400x200")
    welcome_window.configure(bg="#F0F4F8")
    
    # Mensagem de boas-vindas
    mensagem = f"Bem-vindo ao sistema, {nome_usuario}!"
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    label_boas_vindas = tk.Label(welcome_window, text=mensagem, font=("Helvetica", 14, "bold"), bg="#F0F4F8")
    label_boas_vindas.pack(pady=10)

    label_data_hora = tk.Label(welcome_window, text=data_hora, font=("Helvetica", 12), bg="#F0F4F8")
    label_data_hora.pack(pady=10)

    # Botão de logoff
    btn_logoff = ttk.Button(welcome_window, text="Logoff", command=welcome_window.destroy)
    btn_logoff.pack(pady=20)

# Janela principal
root = tk.Tk()
root.title("Cadastro e Login com Reconhecimento Facial")
root.geometry("420x360")
root.configure(bg="#F0F4F8")
root.eval('tk::PlaceWindow . center')

# Frame do cabeçalho
header_frame = tk.Frame(root, bg="#4A90E2", pady=10)
header_frame.pack(fill='x')

header_label = tk.Label(header_frame, text="Sistema de Reconhecimento Facial", bg="#4A90E2", fg="white", font=("Helvetica", 16, "bold"))
header_label.pack()

# Frame principal
main_frame = tk.Frame(root, bg="#F0F4F8", padx=10, pady=20)
main_frame.pack(fill='both', expand=True)

# Campos de entrada
label_nome = ttk.Label(main_frame, text="Nome:", background="#F0F4F8")
label_nome.grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_nome = ttk.Entry(main_frame, width=30)
entry_nome.grid(row=0, column=1, padx=5, pady=5, sticky="w")

label_email = ttk.Label(main_frame, text="E-mail:", background="#F0F4F8")
label_email.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_email = ttk.Entry(main_frame, width=30)
entry_email.grid(row=1, column=1, padx=5, pady=5, sticky="w")

label_numero = ttk.Label(main_frame, text="Número:", background="#F0F4F8")
label_numero.grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_numero = ttk.Entry(main_frame, width=30)
entry_numero.grid(row=2, column=1, padx=5, pady=5, sticky="w")

# Botões de ação
button_frame = tk.Frame(main_frame, bg="#F0F4F8")
button_frame.grid(row=4, column=0, columnspan=2, pady=15)

btn_cadastrar = ttk.Button(button_frame, text="Cadastrar", command=cadastrar_usuario)
btn_cadastrar.grid(row=0, column=0, padx=5)

btn_treinar = ttk.Button(button_frame, text="Treinar Modelo", command=lambda: login_reconhecimento_facial("imagens"))
btn_treinar.grid(row=0, column=1, padx=5)

btn_login = ttk.Button(button_frame, text="Login", command=login_reconhecimento_facial_usuario)
btn_login.grid(row=0, column=2, padx=5)

# Iniciar o loop da interface
root.mainloop()

# Fechar a conexão com o banco de dados ao final
conn.close()

