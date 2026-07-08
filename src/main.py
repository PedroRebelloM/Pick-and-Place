import asyncio
import time
import flet as ft
import serial
import serial.tools.list_ports
from classe import ScrewDetector

try:
    arduino = serial.Serial('COM9', 9600, timeout=1)
except Exception as e:
    print(f"Arduino não conectado! Erro detalhado: {e}")
    arduino = None

async def main(page: ft.Page):
    # configura propriedades basicas da janela
    page.title = "ENG4033 - Classificador de Parafusos"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    # cria um pixel invisivel temporario para evitar erro de imagem vazia ao carregar
    pixelFicticio = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    videoFrame = ft.Image(src=pixelFicticio, fit="contain", gapless_playback=True)
    
    # texto informativo de status na base da tela
    statusText = ft.Text(
        "Inicializando câmera", 
        size=16, 
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.GREEN_400
    )

    detector = ScrewDetector(camera_id=1)
    
    # atualiza o status dependendo se o hardware foi localizado
    if detector.is_opened():
        statusText.value = "Sistema pronto"
    else:
        statusText.value = "Erro"
        statusText.color = ft.Colors.RED_400

    # guarda os dados da operacao
    estado = {
        "running": False,
        "comecar_time": None,
        "tempo_parado": 0.0,
        "movendo": False, 
        "magnetizado": False,
        "zm_atual": (0, 0, 540, 1080),
        "ignorar_ate": 0.0,
        "fase_movimento": "livre"
    }

    time_text = ft.Text("Tempo: 00:00:00", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.YELLOW_400)

    # funcao executada ao clicar no botao comecar
    def btn_comecar_click(e):
        if not estado["running"]:
            estado["running"] = True
            estado["comecar_time"] = time.time()
            statusText.value = "Sistema operando"
            statusText.color = ft.Colors.GREEN_400
            statusText.update()

    def btn_descer_click(e):
        if arduino is not None:
            arduino.write("IMA DESCE\n".encode("utf-8"))

    def btn_subir_click(e):
        if arduino is not None:
            arduino.write("IMA SOBE\n".encode("utf-8"))

    def btn_magnetizar_click(e):
        if arduino is not None:
            arduino.write("IMA LIGA\n".encode("utf-8"))
            estado["magnetizado"] = True
        else:
            print("Erro magnetizar")

    def btn_desmagnetizar_click(e):
        if arduino is not None:
            arduino.write("IMA DESLIGA\n".encode("utf-8"))
            estado["magnetizado"] = False
        else:
            print("Erro desmagnetizar")
            
            
    # funcao executada ao clicar no botao pausar
    def btn_pause_click(e):
        if estado["running"]:
            estado["running"] = False
            estado["tempo_parado"] += time.time() - estado["comecar_time"]
            statusText.value = "Sistema PAUSADO"
            statusText.color = ft.Colors.ORANGE_400
            statusText.update()
            
            if arduino is not None:
                arduino.write("STOP\n".encode("utf-8"))

    def btn_home_click(e):
        if arduino is not None:
            estado["movendo"] = True
            estado["fase_movimento"] = "indo_home"
            arduino.write(b'HOME\n')
            print("Enviado: HOME")

        else:
            print("Erro home")

    def btn_mover_click(e):
        if arduino is not None:
            x_val = input_x.value if input_x.value else "0"
            y_val = input_y.value if input_y.value else "0"
            comando = f"MOVE X{x_val} Y{y_val}\n"
            
            print(f"Python enviou: {comando.strip()}")
            arduino.write(comando.encode("utf-8"))
        else:
            print("Erro mover_click")

    def btn_restaurar_padroes(e):
        detector.restaurar_padroes()
        input_h_min.value = str(detector.default_limite_inf[0])
        input_s_min.value = str(detector.default_limite_inf[1])
        input_v_min.value = str(detector.default_limite_inf[2])
        input_h_max.value = str(detector.default_limite_sup[0])
        input_s_max.value = str(detector.default_limite_sup[1])
        input_v_max.value = str(detector.default_limite_sup[2])
        
        statusText.value = "Padrões Restaurados"
        statusText.color = ft.Colors.BLUE_400
        statusText.update()
        page.update()

    def btn_espalhar_click(e):
        if arduino is not None:
            # Envia o comando "ESPALHA" pela porta serial
            arduino.write("ESPALHA\n".encode("utf-8"))
            print("Enviado: ESPALHA")
            estado["movendo"] = True
            # Como a máquina vai demorar, você pode opcionalmente criar um estado novo "espalhando" ou só usar "livre"
            estado["fase_movimento"] = "espalhando"
            statusText.value = "Espalhando Parafusos"
            statusText.color = ft.Colors.PURPLE_400
            statusText.update()

    # desenha os botoes na interface
    btn_comecar = ft.Button("Começar", icon="play_arrow", on_click=btn_comecar_click, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
    btn_pause = ft.Button("Pausar", icon="pause", on_click=btn_pause_click, bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE)
    
    btn_descer = ft.Button("Descer", icon="arrow_downward", on_click=btn_descer_click, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
    btn_subir = ft.Button("Subir", icon="arrow_upward", on_click=btn_subir_click, bgcolor=ft.Colors.PURPLE_700, color=ft.Colors.WHITE)
    
    btn_magnetizar = ft.Button("Ímã ON", icon="bolt", on_click=btn_magnetizar_click, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)
    btn_desmagnetizar = ft.Button("Ímã OFF", icon="power_off", on_click=btn_desmagnetizar_click, bgcolor=ft.Colors.BROWN_700, color=ft.Colors.WHITE)

    btn_home = ft.Button("Homing", icon="home", on_click=btn_home_click, bgcolor=ft.Colors.BROWN_700, color=ft.Colors.WHITE)
    btn_restaurar = ft.Button("Restaurar Limites", icon="restore", on_click=btn_restaurar_padroes, bgcolor=ft.Colors.GREY_700, color=ft.Colors.WHITE)

    btn_espalhar = ft.Button("Espalhar", icon="", on_click=btn_espalhar_click, bgcolor=ft.Colors.GREY_700, color=ft.Colors.WHITE)

    # campos de texto para movimentacao manual
    input_x = ft.TextField(label="X", width=80, height=40, text_size=14, keyboard_type=ft.KeyboardType.NUMBER)
    input_y = ft.TextField(label="Y", width=80, height=40, text_size=14, keyboard_type=ft.KeyboardType.NUMBER)
    btn_mover = ft.Button("Mover", icon="open_with", on_click=btn_mover_click, bgcolor=ft.Colors.TEAL_700, color=ft.Colors.WHITE)

    # agrupa de dois em dois
    controls_grid = ft.Column([
        ft.Row([btn_comecar, btn_pause], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([btn_descer, btn_subir], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([btn_magnetizar, btn_desmagnetizar], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([btn_home, btn_restaurar], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([btn_espalhar, ft.Container(width=100)], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(color=ft.Colors.WHITE24),
        ft.Row([input_x, input_y, btn_mover], alignment=ft.MainAxisAlignment.CENTER)
    ], spacing=10)

    # inicializa textos de estatisticas
    count_m2_text = ft.Text("M2: 0", size=18, color=ft.Colors.GREEN_400, weight=ft.FontWeight.W_500)
    count_m3_text = ft.Text("M3: 0", size=18, color=ft.Colors.BLUE_400, weight=ft.FontWeight.W_500)
    count_m4_text = ft.Text("M4: 0", size=18, color=ft.Colors.PURPLE_400, weight=ft.FontWeight.W_500)
    count_desc_text = ft.Text("Outros: 0", size=18, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500)
    total_text = ft.Text("Total: 0", size=22, weight=ft.FontWeight.BOLD)

    # agrupa os textos em linhas para poupar espaco vertical
    parafusos_row = ft.Row([count_m2_text, count_m3_text, count_m4_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    outros_row = ft.Row([count_desc_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    # constroi as caixas de selecao de filtros
    chk_m2 = ft.Checkbox(label="M2", value=True)
    chk_m3 = ft.Checkbox(label="M3", value=True)
    chk_m4 = ft.Checkbox(label="M4", value=True)
    
    # esconde as opcoes m2 m3 e m4 se a opcao parafusos for desmarcada
    def on_parafusos_change(e):
        chk_m2.visible = chk_parafusos.value
        chk_m3.visible = chk_parafusos.value
        chk_m4.visible = chk_parafusos.value
        page.update()
        
    chk_parafusos = ft.Checkbox(label="Parafusos", value=True, on_change=on_parafusos_change)
    filtros_container = ft.Container(
        content=ft.Column([
            ft.Text("Filtros de Detecção", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            chk_parafusos,
            ft.Row([chk_m2, chk_m3, chk_m4], alignment=ft.MainAxisAlignment.START)
        ], spacing=2)
    )
    def update_zm(e):
        pass

    # controles da zona morta
    input_zx1 = ft.TextField(label="X1", value="0", width=65, height=40, text_size=12, keyboard_type=ft.KeyboardType.NUMBER, on_change=update_zm)
    input_zy1 = ft.TextField(label="Y1", value="0", width=65, height=40, text_size=12, keyboard_type=ft.KeyboardType.NUMBER, on_change=update_zm)
    input_zx2 = ft.TextField(label="X2", value="540", width=65, height=40, text_size=12, keyboard_type=ft.KeyboardType.NUMBER, on_change=update_zm)
    input_zy2 = ft.TextField(label="Y2", value="1080", width=65, height=40, text_size=12, keyboard_type=ft.KeyboardType.NUMBER, on_change=update_zm)
    
    zona_morta_container = ft.Container(
        content=ft.Column([
            ft.Text("Configurar Zona Morta:", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=16),
            ft.Row([input_zx1, input_zy1], spacing=10),
            ft.Row([input_zx2, input_zy2], spacing=10)
        ], spacing=10),
        padding=15,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        border_radius=12,
    )
    
    # controles HSV
    input_h_min = ft.TextField(label="H Min", value="0", width=65, height=40, text_size=12, keyboard_type=ft.KeyboardType.NUMBER)
    input_s_min = ft.TextField(label="S Min", value="0", width=65, height=40, text_size=12, keyboard_type=ft.KeyboardType.NUMBER)
    input_v_min = ft.TextField(label="V Min", value="110", width=65, height=40, text_size=12, keyboard_type=ft.KeyboardType.NUMBER)
    input_h_max = ft.TextField(label="H Max", value="180", width=65, height=40, text_size=12, keyboard_type=ft.KeyboardType.NUMBER)
    input_s_max = ft.TextField(label="S Max", value="255", width=65, height=40, text_size=12, keyboard_type=ft.KeyboardType.NUMBER)
    input_v_max = ft.TextField(label="V Max", value="255", width=65, height=40, text_size=12, keyboard_type=ft.KeyboardType.NUMBER)

    hsv_container = ft.Container(
        content=ft.Column([
            ft.Text("Limites HSV de Cores:", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=16),
            ft.Row([input_h_min, input_s_min, input_v_min], spacing=10),
            ft.Row([input_h_max, input_s_max, input_v_max], spacing=10)
        ], spacing=10),
        padding=15,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        border_radius=12,
    )

    # monta o retangulo de dados na tela
    info_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Estatísticas", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.WHITE24),
                total_text,
                ft.Container(height=5),
                parafusos_row,    
                outros_row,       
                ft.Divider(color=ft.Colors.WHITE24),
                filtros_container,
                ft.Divider(color=ft.Colors.WHITE24),
                time_text,
                controls_grid
            ],
            spacing=5
        ),
        padding=25,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        border_radius=12,
        width=350,
        height=820,
        alignment=ft.Alignment.TOP_LEFT
    )

    page.add(
        ft.Row(
            controls=[
                ft.Column([
                    ft.Card(
                        content=ft.Container(
                            content=videoFrame,
                            padding=5,
                            bgcolor=ft.Colors.BLACK,
                            border_radius=12,
                        ),
                    ),
                    ft.Row([
                        ft.Container(content=zona_morta_container, expand=True),
                        ft.Container(content=hsv_container, expand=True)
                    ], spacing=15, alignment=ft.MainAxisAlignment.START)
                ], expand=True, spacing=15),
                info_panel
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=20
        ),
        ft.Container(
            content=statusText,
            margin=ft.Margin(0, 20, 0, 0)
        )
    )

    #24.3 altura
    offset_x_mm = 10
    offset_y_mm = 50
    # variavel de controle para a maquina nao pegar o mesmo parafuso duas vezes
    alvos_enviados = []

    # loop principal infinito que roda em paralelo com a tela (async)
    async def loop_video():
        while True:
            try:
                # le os filtros escolhidos na interface
                filtros_atuais = {
                    "parafusos": chk_parafusos.value,
                    "m2": chk_m2.value,
                    "m3": chk_m3.value,
                    "m4": chk_m4.value
                }
            
                # tenta ler a zona morta, usa o valor atual se o campo estiver vazio ou invalido
                try:
                    estado["zm_atual"] = (int(float(input_zx1.value)), int(float(input_zy1.value)), 
                                          int(float(input_zx2.value)), int(float(input_zy2.value)))
                except:
                    pass # mantem a zona morta valida anterior

                zm = estado["zm_atual"]
                
                # tenta ler e aplicar limites HSV customizados em tempo real
                try:
                    h_min = int(input_h_min.value)
                    s_min = int(input_s_min.value)
                    v_min = int(input_v_min.value)
                    h_max = int(input_h_max.value)
                    s_max = int(input_s_max.value)
                    v_max = int(input_v_max.value)
                    detector.limite_inf = (h_min, s_min, v_min)
                    detector.limite_sup = (h_max, s_max, v_max)
                except:
                    pass
                
            
                # processamento da imagem ao vivo da camera
                deve_detectar = not estado["movendo"] and time.time() > estado["ignorar_ate"]
                retorno, dadosBase64, stats, alvos = detector.process_frame(filters=filtros_atuais, detect=deve_detectar, zona_morta=zm)
                
                if not retorno:
                    await asyncio.sleep(0.01)
                    continue
                    
                # atualiza o video na tela
                videoFrame.src = f"data:image/jpeg;base64,{dadosBase64}"
                videoFrame.update()
                
                # executa atualizacao de numeros se estiver operando
                if estado["running"]:
                    # converte o tempo para formato de horas e minutos
                    current_elapsed = int(estado["tempo_parado"] + (time.time() - estado["comecar_time"]))
                    horas = current_elapsed // 3600
                    minutos = (current_elapsed % 3600) // 60
                    segundos = current_elapsed % 60
                    novo_tempo = f"Tempo: {horas:02d}:{minutos:02d}:{segundos:02d}"
                    
                    if time_text.value != novo_tempo:
                        time_text.value = novo_tempo
                        time_text.update()

                new_m2 = f"M2: {stats['m2']}"
                if count_m2_text.value != new_m2:
                    count_m2_text.value = new_m2
                    count_m2_text.update()
                
                new_m3 = f"M3: {stats['m3']}"
                if count_m3_text.value != new_m3:
                    count_m3_text.value = new_m3
                    count_m3_text.update()

                new_m4 = f"M4: {stats['m4']}"
                if count_m4_text.value != new_m4:
                    count_m4_text.value = new_m4
                    count_m4_text.update()


                new_desc = f"Outros: {stats['outros']}"
                if count_desc_text.value != new_desc:
                    count_desc_text.value = new_desc
                    count_desc_text.update()

                new_total = f"Total: {stats['total']}"
                if total_text.value != new_total:
                    total_text.value = new_total
                    total_text.update()

                # verifica se o arduino enviou alguma mensagem
                if arduino is not None and arduino.in_waiting > 0:
                    try:
                        dados_lidos = arduino.read(arduino.in_waiting).decode("utf-8").strip()
                        for linha in dados_lidos.split('\n'):
                            linha = linha.strip()
                            if not linha:
                                continue
                                
                            fase = estado["fase_movimento"]
                            print(f"[ARDUINO RESP] {linha} | Fase atual: {fase}")
                            
                            if linha == "CHEGUEI":
                                if fase == "indo_pegar": #indo pegar o parafuso
                                    arduino.write("IMA DESCE\n".encode("utf-8"))
                                    estado["fase_movimento"] = "descendo_pegar"
                                elif fase == "indo_caixa": #indo soltar o parafuso na caixa
                                    estado["fase_movimento"] = "desligando_ima"
                                    arduino.write("IMA DESLIGA\n".encode("utf-8"))
                            
                            elif linha == "DESCI":
                                if fase == "descendo_pegar": # descendo para pegar o parafuso
                                    arduino.write("IMA LIGA\n".encode("utf-8"))
                                    estado["fase_movimento"] = "ligando_ima"
                                    
                            elif linha == "DESLIGUEI":
                                if fase == "desligando_ima":
                                    estado["magnetizado"] = False
                                    arduino.write("HOME\n".encode("utf-8"))
                                    estado["fase_movimento"] = "indo_home"
                                    print("Máquina soltou o parafuso e está retornando ao HOME")

                            elif linha == "LIGUEI":
                                if fase == "ligando_ima":
                                    arduino.write("IMA SOBE\n".encode("utf-8"))
                                    estado["fase_movimento"] = "subindo_pegar"
                                    
                            elif linha == "SUBI":
                                if fase == "subindo_pegar": #subindo com o parafuso
                                    estado["magnetizado"] = True
                                    classe = estado["alvo_atual_classe"]
                                    if classe == "M2":
                                        arduino.write("MOVE X150 Y400\n".encode("utf-8"))
                                    elif classe == "M3":
                                        arduino.write("MOVE X150 Y800\n".encode("utf-8"))
                                    elif classe == "M4":
                                        arduino.write("MOVE X150 Y1200\n".encode("utf-8"))
                                    else:
                                        arduino.write("MOVE X150 Y400\n".encode("utf-8"))
                                    estado["fase_movimento"] = "indo_caixa"
                            elif "PAROU" in linha:
                                if estado["movendo"]:
                                    estado["movendo"] = False
                                    estado["fase_movimento"] = "livre"
                                    estado["ignorar_ate"] = time.time() + 4.0
                                    print("Máquina finalizou a rota e está livre para o próximo alvo")

                            elif linha == "ESPALHEI":
                                if estado["fase_movimento"] == "espalhando":
                                    estado["movendo"] = False
                                    estado["fase_movimento"] = "livre"
                                    print("Máquina finalizou o espalhamento e está livre")

                    except Exception as e:
                        print(f"Erro na leitura serial: {e}")

                # só envia o próximo comando se o sistema estiver rodando ("Começar") e a máquina NÃO estiver se movendo
                if estado["running"] and arduino is not None and len(alvos) > 0 and not estado["movendo"]:
                    for alvo in alvos:
                        # cria um id unico baseado na posicao grosseira para nao mandar o mesmo alvo duas vezes
                        alvo_id = f"{alvo['classe']}_{int(alvo['cx'])}_{int(alvo['cy'])}"
                        
                        if alvo_id not in alvos_enviados:
                            # usa a escala fixa real do detector (0.29 mm/px)
                            escala_real = 0.1735
                            
                            # converte as coordenadas de pixels (camera) para milimetros (mesa cnc)
                            pos_x_real = offset_x_mm + (alvo["cx"] * escala_real)
                            pos_y_real = offset_y_mm + (alvo["cy"] * escala_real)
                            
                            pos_x_passos = (pos_x_real / 10) * 50 
                            pos_y_passos = (pos_y_real / 10) * 50
                            
                            # monta o comando que o arduino vai entender(i nclui classe para talvez caixas diferentes)
                            comando = f"MOVE X{int(pos_x_passos)} Y{int(pos_y_passos)}\n"
                            # envia o comando pela porta serial (descomente quando for ligar a maquina)
                            arduino.write(comando.encode("utf-8"))
                            print(f"Enviando comando para pegar {alvo['classe']}: {comando.strip()}")
                            
                            # salva a classe atual para saber em qual caixa soltar depois
                            estado["alvo_atual_classe"] = alvo['classe']
                            
                            # trava o envio de novos comandos até receber o CHEGOU/PAROU
                            estado["movendo"] = True
                            estado["fase_movimento"] = "indo_pegar"
                            
                            # salva na lista de concluidos
                            alvos_enviados.append(alvo_id)
                            
                            # como enviamos um comando de movimento, paramos de olhar os outros alvos neste frame
                            # para esperar o PAROU chegar no próximo ciclo!
                            break
                await asyncio.sleep(0.03)

            except Exception as e:
                print(f"Erro no loop assíncrono: {str(e)}")
                await asyncio.sleep(1.0)

    # avisa ao flet para rodar a camera sem travar os botoes
    page.run_task(loop_video)

ft.app(main)