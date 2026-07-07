import cv2
import numpy as np
from sklearn.cluster import KMeans

def nada(x):
    pass

cv2.namedWindow("Controle de Contraste")
cv2.resizeWindow("Controle de Contraste", 400, 300)

cv2.createTrackbar("H Min", "Controle de Contraste", 0, 180, nada)
cv2.createTrackbar("H Max", "Controle de Contraste", 180, 180, nada)
cv2.createTrackbar("S Min", "Controle de Contraste", 0, 255, nada)
cv2.createTrackbar("S Max", "Controle de Contraste", 45, 255, nada)
cv2.createTrackbar("V Min", "Controle de Contraste", 180, 255, nada)
cv2.createTrackbar("V Max", "Controle de Contraste", 245, 255, nada)

cap = cv2.VideoCapture(2)

while True:
    retorno, frame = cap.read()
    if not retorno:
        print("Não foi possível acessar a câmera.")
        break   
        
    frameBorrado = cv2.GaussianBlur(frame, (5, 5), 0)
    frameHsv = cv2.cvtColor(frameBorrado, cv2.COLOR_BGR2HSV)
    
    hMin = cv2.getTrackbarPos("H Min", "Controle de Contraste")
    hMax = cv2.getTrackbarPos("H Max", "Controle de Contraste")
    sMin = cv2.getTrackbarPos("S Min", "Controle de Contraste")
    sMax = cv2.getTrackbarPos("S Max", "Controle de Contraste")
    vMin = cv2.getTrackbarPos("V Min", "Controle de Contraste")
    vMax = cv2.getTrackbarPos("V Max", "Controle de Contraste")
    
    limiteInf = (0, 0, 110)
    limiteSup = (180, 255, 255)
    mascara = cv2.inRange(frameHsv, limiteInf, limiteSup)

    mascaraInvertida = cv2.bitwise_not(mascara)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mascaraLimpa = cv2.morphologyEx(mascaraInvertida, cv2.MORPH_OPEN, kernel)
    mascaraLimpa = cv2.morphologyEx(mascaraLimpa, cv2.MORPH_CLOSE, kernel)
    
    contornos, _ = cv2.findContours(mascaraLimpa, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    frameContornos = frame.copy()
    dadosParafusos = []
    
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if 3000 > area > 200: 
            x, y, w, h = cv2.boundingRect(contorno)
            hull = cv2.convexHull(contorno)
            rect = cv2.minAreaRect(hull)
            dimensoes = rect[1]
            
            if len(dimensoes) < 2 or dimensoes[0] == 0 or dimensoes[1] == 0:
                continue
                
            comprimento = max(dimensoes)
            espessura = min(dimensoes)
            
            proporcao = comprimento / espessura
            if proporcao < 1.4:
                continue
            
            if espessura > 6:
                dadosParafusos.append({
                    'espessura': espessura,
                    'bbox': (x, y, w, h),
                    'rect': rect
                })
                
    if len(dadosParafusos) >= 3:
        X = np.array([p['espessura'] for p in dadosParafusos]).reshape(-1, 1)
        
        nClusters = min(1, len(dadosParafusos))
        kmeans = KMeans(n_clusters=nClusters, random_state=42, n_init=10).fit(X)
        labels = kmeans.labels_
        
        centros = kmeans.cluster_centers_.flatten()
        indicesOrdenados = np.argsort(centros) 
        
        mapaClasses = {0: "M2", 1: "M3", 2: "M4"}


        
        for idx, p in enumerate(dadosParafusos):
            clusterAtual = labels[idx]
            ordemTamanho = np.where(indicesOrdenados == clusterAtual)[0][0]
            
            classe = mapaClasses.get(ordemTamanho, "Desc.")
            
            box = cv2.boxPoints(p['rect'])
            box = np.intp(box)  
            cv2.drawContours(frameContornos, [box], 0, (0, 255, 0), 2)                
            
            bx, by, bw, bh = p['bbox']

            
            cv2.putText(frameContornos, f"{classe} (espessura={p['espessura']:.1f})", (bx, by - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                  
    elif len(dadosParafusos) > 0:
        for p in dadosParafusos:
            bx, by, bw, bh = p['bbox']
            cv2.putText(frameContornos, "São necessários mais dados", (bx, by - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 165, 255), 1)
    
    cv2.imshow("Mascara de Contraste (HSV)", mascaraLimpa)
    cv2.imshow("Deteccao em Tempo Real", frameContornos)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(f"limiteInferior = ({hMin}, {sMin}, {vMin})")
        print(f"limiteSuperior = ({hMax}, {sMax}, {vMax})\n")
        break

cap.release()
cv2.destroyAllWindows()