import asyncio
import time
import flet as ft
import serial
import serial.tools.list_ports
from classe import ScrewDetector

try:
    arduino = serial.Serial('COM4', 9600, timeout=1)
except Exception as e:
    print("Arduino não conectado!")
    arduino = None

async def main(page: ft.Page):
    # configura propriedades basicas da janela
    page.title = "ENG4033 - Classificador de Parafusos"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    # cria um pixel invisivel temporario para evitar erro de imagem vazia ao carregar
    pixelFicticio = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    videoFrame = ft.Image(src=pixelFicticio, fit="contain", width=640, height=480, gapless_playback=True)
    
    # texto informativo de status na base da tela
    statusText = ft.Text(
        "Inicializando câmera", 
        size=16, 
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.GREEN_400
    )

    detector = ScrewDetector(camera_id=0)
    
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
        "tempo_parado": 0.0
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
            
            if arduino is not None:
                arduino.write("COMEÇAR\n".encode("utf-8"))

    def btn_descer_click(e):
        if arduino is not None:
            arduino.write("DESCER\n".encode("utf-8"))

    def btn_subir_click(e):
        if arduino is not None:
            arduino.write("SUBIR\n".encode("utf-8"))

    def btn_magnetizar_click(e):
        if arduino is not None:
            arduino.write("MAGNETIZAR\n".encode("utf-8"))

    def btn_desmagnetizar_click(e):
        if arduino is not None:
            arduino.write("DESMAGNETIZAR\n".encode("utf-8"))
            
            
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
            print("HOME")
            arduino.write(b'HOME\n')
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

    # desenha os botoes na interface
    btn_comecar = ft.ElevatedButton("Começar", icon="play_arrow", on_click=btn_comecar_click, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
    btn_pause = ft.ElevatedButton("Pausar", icon="pause", on_click=btn_pause_click, bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE)
    
    btn_descer = ft.ElevatedButton("Descer", icon="arrow_downward", on_click=btn_descer_click, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
    btn_subir = ft.ElevatedButton("Subir", icon="arrow_upward", on_click=btn_subir_click, bgcolor=ft.Colors.PURPLE_700, color=ft.Colors.WHITE)
    
    btn_magnetizar = ft.ElevatedButton("Ímã ON", icon="bolt", on_click=btn_magnetizar_click, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)
    btn_desmagnetizar = ft.ElevatedButton("Ímã OFF", icon="power_off", on_click=btn_desmagnetizar_click, bgcolor=ft.Colors.BROWN_700, color=ft.Colors.WHITE)

    btn_home = ft.ElevatedButton("Homing", icon="home", on_click=btn_home_click, bgcolor=ft.Colors.BROWN_700, color=ft.Colors.WHITE)

    # campos de texto para movimentacao manual
    input_x = ft.TextField(label="X", width=80, height=40, text_size=14, keyboard_type=ft.KeyboardType.NUMBER)
    input_y = ft.TextField(label="Y", width=80, height=40, text_size=14, keyboard_type=ft.KeyboardType.NUMBER)
    btn_mover = ft.ElevatedButton("Mover", icon="open_with", on_click=btn_mover_click, bgcolor=ft.Colors.TEAL_700, color=ft.Colors.WHITE)

    # agrupa de dois em dois
    controls_grid = ft.Column([
        ft.Row([btn_comecar, btn_pause], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([btn_descer, btn_subir], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([btn_magnetizar, btn_desmagnetizar], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([btn_home], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(color=ft.Colors.WHITE24),
        ft.Row([input_x, input_y, btn_mover], alignment=ft.MainAxisAlignment.CENTER)
    ], spacing=10)

    # inicializa textos de estatisticas
    count_m2_text = ft.Text("M2: 0", size=18, color=ft.Colors.GREEN_400, weight=ft.FontWeight.W_500)
    count_m3_text = ft.Text("M3: 0", size=18, color=ft.Colors.BLUE_400, weight=ft.FontWeight.W_500)
    count_m4_text = ft.Text("M4: 0", size=18, color=ft.Colors.PURPLE_400, weight=ft.FontWeight.W_500)
    count_porcas_text = ft.Text("Porcas: 0", size=18, color=ft.Colors.CYAN_400, weight=ft.FontWeight.W_500)
    count_desc_text = ft.Text("Outros: 0", size=18, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500)
    total_text = ft.Text("Total: 0", size=22, weight=ft.FontWeight.BOLD)

    # agrupa os textos em linhas para poupar espaco vertical
    parafusos_row = ft.Row([count_m2_text, count_m3_text, count_m4_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    outros_row = ft.Row([count_porcas_text, count_desc_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
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
    chk_porcas = ft.Checkbox(label="Porcas", value=True)
    filtros_container = ft.Container(
        content=ft.Column([
            ft.Text("Filtros de Detecção", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            chk_porcas,
            chk_parafusos,
            ft.Row([chk_m2, chk_m3, chk_m4], alignment=ft.MainAxisAlignment.START)
        ], spacing=2)
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
        height=720,
        alignment=ft.Alignment.TOP_LEFT
    )

    page.add(
        ft.Row(
            controls=[
                ft.Card(
                    content=ft.Container(
                        content=videoFrame,
                        padding=5,
                        bgcolor=ft.Colors.BLACK,
                        border_radius=12
                    ),
                    elevation=8
                ),
                info_panel
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=20
        ),
        ft.Container(
            content=statusText,
            margin=ft.Margin(0, 20, 0, 0)
        )
    )

    # parametros de calibracao da cnc (mapeamento camera -> real)
    #24.3 altura
    escala_x_mm_por_pixel = 0.5 
    escala_y_mm_por_pixel = 0.5 
    offset_x_mm = 100.0
    offset_y_mm = 50.0
    # variavel de controle para a maquina nao pegar o mesmo parafuso duas vezes
    alvos_enviados = []

    # loop principal infinito que roda em paralelo com a tela (async)
    async def loop_video():
        while True:
            try:
                # le os filtros escolhidos na interface
                filtros_atuais = {
                    "parafusos": chk_parafusos.value,
                    "porcas": chk_porcas.value,
                    "m2": chk_m2.value,
                    "m3": chk_m3.value,
                    "m4": chk_m4.value
                }
            
                # processamento da imagem ao vivo da camera
                retorno, dadosBase64, stats, alvos = detector.process_frame(filters=filtros_atuais)
                
                if not retorno:
                    await asyncio.sleep(0.01)
                    continue
                    
                # atualiza o video na tela
                videoFrame.src = f"data:image/jpeg;base64,{dadosBase64}"
                videoFrame.update()

                # executa atualizacao de numeros se estiver operando
                if estado["running"]:
                    # converte o tempo para formato de horas e minutos
                    current_elapsed = estado["tempo_parado"] + (time.time() - estado["comecar_time"])
                    horas, resto = divmod(int(current_elapsed), 3600)
                    minutos, segundos = divmod(resto, 60)
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

                    new_porcas = f"Porcas: {stats['porcas']}"
                    if count_porcas_text.value != new_porcas:
                        count_porcas_text.value = new_porcas
                        count_porcas_text.update()

                    new_desc = f"Outros: {stats['outros']}"
                    if count_desc_text.value != new_desc:
                        count_desc_text.value = new_desc
                        count_desc_text.update()

                    new_total = f"Total: {stats['total']}"
                    if total_text.value != new_total:
                        total_text.value = new_total
                        total_text.update()

                    if arduino is not None and len(alvos) > 0:
                        for alvo in alvos:
                            # cria um id unico baseado na posicao grosseira para nao mandar o mesmo alvo duas vezes
                            alvo_id = f"{alvo['classe']}_{int(alvo['cx'])}_{int(alvo['cy'])}"
                            
                            if alvo_id not in alvos_enviados:
                                # converte as coordenadas de pixels (camera) para milimetros (mesa cnc)
                                pos_x_real = offset_x_mm + (alvo["cx"] * escala_x_mm_por_pixel)
                                pos_y_real = offset_y_mm + (alvo["cy"] * escala_y_mm_por_pixel)
                                
                                # monta o comando que o arduino vai entender(i nclui classe para talvez caixas diferentes)
                                # PEGAR M4 = vai para x,y -> desce servo -> liga rele -> sobe servo -> vai pra caixa M4 -> desliga rele
                                comando = f"PEGAR,{alvo['classe']},{pos_x_real:.1f},{pos_y_real:.1f}\n"
                                #PEGAR,m4,x,y
                                # envia o comando pela porta serial (descomente quando for ligar a maquina)
                                arduino.write(comando.encode("utf-8"))
                                
                                # salva na lista de concluidos
                                alvos_enviados.append(alvo_id)
                                print(f"Comando preparado: {comando.strip()}")
                                
                                # pausa de seguranca entre um envio e outro para o arduino nao engasgar
                                # na pratica, o ideal e ler um "OK" do arduino antes de enviar o proximo!
                                await asyncio.sleep(0.5)

                await asyncio.sleep(0.03)

            except Exception as e:
                print(f"Erro no loop assíncrono: {str(e)}")
                await asyncio.sleep(1.0)

    # avisa ao flet para rodar a camera sem travar os botoes
    page.run_task(loop_video)

ft.app(main)