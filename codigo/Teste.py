import cv2

# Use o caminho absoluto ou a string crua
caminho_haarcascade = r'C:\\Users\\vanil\\Documents\\APS 6 Semestre_CC\\haarcascade_frontalface_default.xml.'
classificador = cv2.CascadeClassifier(caminho_haarcascade)

if classificador.empty():
    print("Classificador não foi carregado.")
else:
    print("Classificador carregado com sucesso.")
