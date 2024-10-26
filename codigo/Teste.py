import cv2

# Use o caminho absoluto ou a string crua
caminho_haarcascade = r'C:\Users\victo\Documents\UNIP\APS 6 Semestre_CC\.venv\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml'
classificador = cv2.CascadeClassifier(caminho_haarcascade)

if classificador.empty():
    print("Classificador não foi carregado.")
else:
    print("Classificador carregado com sucesso.")
