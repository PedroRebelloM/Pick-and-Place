import asyncio
import time
import flet as ft
import serial
from classe import ScrewDetector

try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
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
        statusText.value = "Erro fatal: Câmera no ID 0 não respondeu."
        statusText.color = ft.Colors.RED_400

    # guarda os dados da operacao
    state = {
        "running": False,
        "comecar_time": None,
        "elapsed_paused": 0.0
    }

    time_text = ft.Text("Tempo: 00:00:00", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.YELLOW_400)

    # funcao executada ao clicar no botao comecar
    def btn_comecar_click(e):
        if not state["running"]:
            state["running"] = True
            state["comecar_time"] = time.time()
            statusText.value = "Sistema OPERANDO"
            statusText.color = ft.Colors.GREEN_400
            statusText.update()
            
            if arduino is not None:
                arduino.write("COMEÇAR\n".encode("utf-8"))
            
    # funcao executada ao clicar no botao pausar
    def btn_pause_click(e):
        if state["running"]:
            state["running"] = False
            state["elapsed_paused"] += time.time() - state["comecar_time"]
            statusText.value = "Sistema PAUSADO"
            statusText.color = ft.Colors.ORANGE_400
            statusText.update()
            
            if arduino is not None:
                arduino.write("PAUSAR\n".encode("utf-8"))

    # desenha os botoes na interface
    btn_comecar = ft.ElevatedButton("Começar", icon="play_arrow", on_click=btn_comecar_click, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
    btn_pause = ft.ElevatedButton("Pausar", icon="pause", on_click=btn_pause_click, bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE)
    
    controls_row = ft.Row([btn_comecar, btn_pause], alignment=ft.MainAxisAlignment.CENTER)

    # inicializa textos de estatisticas
    count_m2_text = ft.Text("M2: 0", size=18, color=ft.Colors.GREEN_400, weight=ft.FontWeight.W_500)
    count_m3_text = ft.Text("M3: 0", size=18, color=ft.Colors.BLUE_400, weight=ft.FontWeight.W_500)
    count_m4_text = ft.Text("M4: 0", size=18, color=ft.Colors.PURPLE_400, weight=ft.FontWeight.W_500)
    count_porcas_text = ft.Text("Porcas: 0", size=18, color=ft.Colors.CYAN_400, weight=ft.FontWeight.W_500)
    count_desc_text = ft.Text("Outros: 0", size=18, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500)
    total_text = ft.Text("Total: 0", size=22, weight=ft.FontWeight.BOLD)

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
                count_m2_text,
                count_m3_text,
                count_m4_text,
                count_porcas_text,
                count_desc_text,
                ft.Divider(color=ft.Colors.WHITE24),
                filtros_container,
                ft.Divider(color=ft.Colors.WHITE24),
                time_text,
                controls_row
            ],
            spacing=5
        ),
        padding=25,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        border_radius=12,
        width=300,
        height=580,
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
                retorno, dadosBase64, stats = detector.process_frame(filters=filtros_atuais)
                
                if not retorno:
                    await asyncio.sleep(0.01)
                    continue
                    
                # atualiza o video na tela
                videoFrame.src = f"data:image/jpeg;base64,{dadosBase64}"
                videoFrame.update()

                # executa atualizacao de numeros se estiver operando
                if state["running"]:
                    # converte o tempo para formato de horas e minutos
                    current_elapsed = state["elapsed_paused"] + (time.time() - state["comecar_time"])
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

                await asyncio.sleep(0.03)

            except Exception as e:
                print(f"Erro no loop assíncrono: {str(e)}")
                await asyncio.sleep(1.0)

    # avisa ao flet para rodar a camera sem travar os botoes
    page.run_task(loop_video)

ft.app(main)