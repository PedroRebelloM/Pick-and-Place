import cv2
import numpy as np
import base64
from sklearn.cluster import KMeans

class ScrewDetector:
    def __init__(self, camera_id=0):
        """inicializa a camera e configura o detector"""
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        # Escala de milímetros por pixel calibrada
        self.escala_mm_por_pixel = 0.1735
        
        # Limites HSV de cor
        self.default_limite_inf = (0, 0, 110)
        self.default_limite_sup = (180, 255, 255)
        self.limite_inf = self.default_limite_inf
        self.limite_sup = self.default_limite_sup

    def restaurar_padroes(self):
        """Volta os limites HSV para o padrão de fábrica"""
        self.limite_inf = self.default_limite_inf
        self.limite_sup = self.default_limite_sup
        
    def is_opened(self):
        """verifica se a camera foi aberta com sucesso"""
        return self.cap.isOpened()
        
    def process_frame(self, filters=None, detect=True, zona_morta=(0, 0, 540, 1080)):
        """le o frame da camera aplica deteccao e retorna resultados"""
        if filters is None:
            filters = {"parafusos": True, "porcas": True, "m2": True, "m3": True, "m4": True}
        retorno, frame = self.cap.read()
        if not retorno:
            return False, None, None, None
            
        # garante que a variavel existe (caso seja a primeira execucao)
        if not hasattr(self, 'contador_print'):
            self.contador_print = 0
            
        self.contador_print += 1
            
        if not detect:
            # apenas retorna a imagem bruta sem aplicar IA para nao pegar a correia movendo
            cv2.putText(frame, "MAQUINA EM MOVIMENTO - LEITURA PAUSADA", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
            _, buffer = cv2.imencode(".jpg", frame)
            dadosBase64 = base64.b64encode(buffer).decode("utf-8")
            
            stats_zerado = {
                "total": 0, "m2": 0, "m3": 0, "m4": 0, "porcas": 0, "outros": 0,
                "espessura_media": 0.0,
                "limite_inf": self.limite_inf,
                "limite_sup": self.limite_sup   
            }
            return True, dadosBase64, stats_zerado, []
            
        # borra a imagem suavemente para eliminar pequenos chiados e sujeiras da lente
        frameBorrado = cv2.GaussianBlur(frame, (5, 5), 0)
        # converte as cores para hsv pois e muito mais estavel para detectar brilho e contornos
        frameHsv = cv2.cvtColor(frameBorrado, cv2.COLOR_BGR2HSV)
        
        # margens de cor usadas para recortar o verde da esteira ou a luz
        limiteInf = self.limite_inf
        limiteSup = self.limite_sup
        
        # cria uma mascara binaria onde tudo que bate com a margem vira branco
        mascara = cv2.inRange(frameHsv, limiteInf, limiteSup)
        # inverte o fundo para focar nas pecas
        mascaraInvertida = cv2.bitwise_not(mascara)
        
        # area limite onde a maquina nao deve contabilizar itens
        zx1, zy1, zx2, zy2 = zona_morta
        
        # limpa ruidos finais com fechamento e abertura da malha da mascara
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mascaraLimpa = cv2.morphologyEx(mascaraInvertida, cv2.MORPH_OPEN, kernel)
        mascaraLimpa = cv2.morphologyEx(mascaraLimpa, cv2.MORPH_CLOSE, kernel)
        
        # desenha o esqueleto das bordas de todos os objetos que sobraram
        contornos, _ = cv2.findContours(mascaraLimpa, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        frameContornos = frame.copy()
        
        cv2.rectangle(frameContornos, (zx1, zy1), (zx2, zy2), (0, 0, 255), 2)
        cv2.putText(frameContornos, "ZONA MORTA", (zx1 + 10, zy1 + 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            
        cv2.circle(frameContornos, (960, 540), 8, (0, 255, 0), 10)  
        dadosParafusos = []
        dadosPorcas = []
        # analisa e separa cada bloco branco achado na tela
        for contorno in contornos:
            area = cv2.contourArea(contorno)
            
            # descarta farelos pequenos ou areas grandes que podem ser sombras
            if 3500 > area > 500: 
                x, y, w, h = cv2.boundingRect(contorno)
                
                cx = x + (w / 2) #centro em x
                cy = y + (h / 2) #centro em y
                
                # Imprime a cada 100 frames para nao poluir o terminal
                if self.contador_print >= 100:
                     print(f"[DEBUG] x: {cx}, y: {cy}")
                     print(f"[DEBUG] xreal: {((cx*0.1735 + 10)/10)*50}, yreal: {((cy*0.1735 + 55)/10)*50}")
                
                if (zx1 <= cx <= zx2) and (zy1 <= cy <= zy2): 
                    continue
                    
                # calcula um retangulo justinho que inclina junto com a rotacao do objeto
                hull = cv2.convexHull(contorno)
                rect = cv2.minAreaRect(hull)
                dimensoes = rect[1]
                
                comprimento = max(dimensoes)
                espessura = min(dimensoes)
                
                # avalia se o objeto e comprido feito parafuso ou se parece quadrado igual uma porca
                proporcao = comprimento / espessura
                is_porca = proporcao < 1.3
                
                if is_porca:
                    if filters.get("porcas", True):
                        dadosPorcas.append({
                            'espessura': espessura,
                            'bbox': (x, y, w, h),
                            'rect': rect
                        })
                else:
                    if espessura > 6 and filters.get("parafusos", True):
                        dadosParafusos.append({
                            'espessura': espessura,
                            'bbox': (x, y, w, h),
                            'rect': rect
                        })
                    
        # inicializa o contador com zero para montar os dados finais desse momento do video
        contagem = {"M2": 0, "M3": 0, "M4": 0, "Desc.": 0, "Porcas": len(dadosPorcas)}
        espessuras = []
        alvos = []
        
        # Reseta o contador apos passar pelo frame 100
        if self.contador_print >= 100:
            self.contador_print = 0
            
        # encontra o contorno e desenha a marcacao das porcas
        for p in dadosPorcas:
            box = cv2.boxPoints(p['rect'])
            box = np.intp(box)  
            cv2.drawContours(frameContornos, [box], 0, (255, 0, 0), 2) # pinta as porcas de azul
            bx, by, bw, bh = p['bbox']
            
            # adiciona a porca na lista de alvos validos
            cx = bx + (bw / 2)
            cy = by + (bh / 2)
            alvos.append({"classe": "Porca", "cx": cx, "cy": cy})
            
            cv2.putText(frameContornos, "Porca", (bx, by - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # agrupa as espessuras dos parafusos usando inteligencia artificial
        if len(dadosParafusos) >= 3:
            X = np.array([p['espessura'] for p in dadosParafusos]).reshape(-1, 1)
            nClusters = min(2, len(dadosParafusos))
            kmeans = KMeans(
                n_clusters=nClusters, 
                random_state=42, 
                n_init=1, 
                max_iter=100, 
                algorithm='elkan'
            ).fit(X)
            
            labels = kmeans.labels_
            centros = kmeans.cluster_centers_.flatten()
            indicesOrdenados = np.argsort(centros)
            
            mapaClasses = {0: "M2", 1: "M3", 2: "M4"}
            
            for idx, p in enumerate(dadosParafusos):
                clusterAtual = labels[idx]
                ordemTamanho = np.where(indicesOrdenados == clusterAtual)[0][0]
                classe = mapaClasses.get(ordemTamanho, "Desc.")
                
                # verifica se o filtro do parafuso especifico esta ativo
                if not filters.get(classe.lower(), True) and classe != "Desc.":
                    continue
                
                contagem[classe] = contagem.get(classe, 0) + 1
                espessuras.append(p['espessura'])
                
                box = cv2.boxPoints(p['rect'])
                box = np.intp(box)  
                cv2.drawContours(frameContornos, [box], 0, (0, 255, 0), 2)                
                
                bx, by, bw, bh = p['bbox']

                
                # adiciona o parafuso na lista de alvos validos
                cx = bx + (bw / 2)
                cy = by + (bh / 2)
                alvos.append({"classe": classe, "cx": cx, "cy": cy})
                
                cv2.putText(frameContornos, f"{classe} (e={p['espessura']:.1f})", (bx, by - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
        elif len(dadosParafusos) > 0:
            for p in dadosParafusos:
                bx, by, bw, bh = p['bbox']
                cv2.putText(frameContornos, "Aguardando objetos...", (bx, by - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 165, 255), 1)

        # pega a matriz crua que o opencv criou com desenhos em verde e transforma em imagem comprimida
        _, buffer = cv2.imencode(".jpg", frameContornos)
        # converte o jpg puro para dados de texto que podem ser lidos pelo front end
        dadosBase64 = base64.b64encode(buffer).decode("utf-8")
        avg_e = sum(espessuras) / len(espessuras) if espessuras else 0.0
        stats = {
            "total": contagem["M2"] + contagem["M3"] + contagem["M4"] + contagem["Desc."] + contagem["Porcas"],
            "m2": contagem["M2"],
            "m3": contagem["M3"],
            "m4": contagem["M4"],
            "porcas": contagem["Porcas"],
            "outros": contagem["Desc."],
            "espessura_media": avg_e,
            "limite_inf": limiteInf,
            "limite_sup": limiteSup   
        }

        return True, dadosBase64, stats, alvos

    def release(self):
        """libera a camera ao finalizar o uso"""
        self.cap.release()
