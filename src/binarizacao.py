import cv2
import numpy as np

def geraImagemBinarizadaThresholdAdapatado(path):
    imagem = cv2.imread(path)
    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    borrada = cv2.GaussianBlur(imagemCinza, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(borrada, 255, 
                                   cv2.ADAPTIVE_THRESH_MEAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    cv2.imshow("Imagem Binarizada", thresh)
    threshGaussiana = cv2.adaptiveThreshold(imagemCinza, 255, 
                                              cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                              cv2.THRESH_BINARY_INV, 11, 2)
    cv2.imshow("Imagem Binarizada Gaussiana", threshGaussiana)
    cv2.waitKey(0)
    cv2.destroyAllWindows()    

path1 = r"C:\Users\prmorais\Documents\GitHub\Pick-and-Place\src\images\com_flash_longe.jpeg"
path2 = r"C:\Users\prmorais\Documents\GitHub\Pick-and-Place\src\images\sem_flash_longe.jpeg"
path3 = r"C:\Users\prmorais\Documents\GitHub\Pick-and-Place\src\images\com_flash_perto.jpeg"

def geraImagemBinarizadaThreshold(path):
    imagem = cv2.imread(path)
    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    borrada = cv2.GaussianBlur(imagemCinza, (5, 5), 0)
    _, threshGlobal = cv2.threshold(borrada, 100, 255, cv2.THRESH_BINARY)
    contornos, _ = cv2.findContours(threshGlobal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contornos:
        perimetro = cv2.arcLength(c, True)
        if perimetro > 100:
            cv2.drawContours(imagem, [c], -1, (0, 255, 0), 2)
    cv2.imshow('Contornos com Threshold Global', imagem)
    _, threshInvertida = cv2.threshold(borrada, 85, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow("Limiarizacao Binaria Invertida", threshInvertida)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def filtroDeCanny(path):
    imagem = cv2.imread(path)
    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    borrada = cv2.GaussianBlur(imagemCinza, (5, 5), 0)
    edges = cv2.Canny(borrada, 50, 150)
    cv2.imshow("Filtro de Canny", edges)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def erosao(path):
    imagem = cv2.imread(path)
    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((2, 2), np.uint8)
    borrada = cv2.GaussianBlur(imagemCinza, (3, 3), 0)
    imagemErodida = cv2.erode(borrada, kernel, iterations=2)
    _, threshInvertida = cv2.threshold(imagemErodida, 110, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow("Limiarizacao Binaria Invertida + erosao", threshInvertida)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

geraImagemBinarizadaThreshold(path3)
filtroDeCanny(path3)
erosao(path3)