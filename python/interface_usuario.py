# -*- coding: utf-8 -*-
import wx
import wx.grid as wxgrid
import wx.lib.scrolledpanel as scrolledpanel
import ComunicadorArduino as Leitor
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

#classe para manipular os dados de leitura com a distancia, velocidade e aceleracao
class DadoLeituraVelocidadeAceleracao(Leitor.DadoLeitura):

    velocidade = 0
    aceleracao = 0
    posicao_cru = 0
    posicao_cm = 0

    def __init__(self, dado, tempo_leitura):
        super(DadoLeituraVelocidadeAceleracao, self).__init__(dado, tempo_leitura)
        self.dadoFloat = float(dado)
        self.posicao_cru = self.dadoFloat
        self.posicao_cm = (self.dadoFloat / 29.0) / 2.0 #distancia em CM
        self.velocidade = self.posicao_cm / self.tempo
        self.aceleracao = self.velocidade / self.tempo

    def __str__(self):
        return super(DadoLeituraVelocidadeAceleracao, self).__str__() + " | Posição CM: " + str(self.posicao_cm) + " | Velocidade: " + str(self.velocidade) + " | Aceleração: " + str(self.aceleracao)

    def get_csv(self):
        return super(DadoLeituraVelocidadeAceleracao, self).get_csv() + "," + str(self.posicao_cm) + "," + str(self.posicao_cm) + "," + str(self.velocidade) + "," + str(self.aceleracao)

#classe que representa os graficos que sao mostrados na tela
class Grafico(wx.Panel):

    altura_grafico = 250
    largura_grafico = 750

    def __init__(self, pai, posicao):
        wx.Panel.__init__(self, pai, -1, posicao, size=(Grafico.largura_grafico, Grafico.altura_grafico))

        #cria uma nova figura que vai conter o grafico
        self.figura = Figure()

        #cria um canvas para imagem
        self.canvas = FigureCanvas(self, -1, self.figura)

        #cria um só plot
        self.eixos = self.figura.add_subplot(111)

    #desenha os pontos x e y. Dois vetores que devem ter o mesmo tamanho
    #os vertices serão (pontosX[n], pontosY[n])
    def desenha(self, pontosX, pontosY):
        #adiciona os pontos x e y no grafico
        self.eixos.plot(pontosX, pontosY)
        self.canvas.draw()



#classe do programa, contem os controles de tela, a janela, etc. Herda de wx.Frame
class Interface(wx.Frame, Leitor.RecebeLeitura):

    largura_tela = 1024
    altura_tela = 768
    largura_botoes = 75
    altura_botoes = 25

    def __init__(self):
        #cria o aplicativo
        self.app = wx.App()

        #chama o contrutor dos pais
        wx.Frame.__init__(self, None, 0, "Sensor Sônico", (0, 0), (Interface.largura_tela, Interface.altura_tela))

        self.cria_interface()

        #mostra a tela e entra no loop de eventos do aplicativo
        self.SetMinSize((Interface.largura_tela, Interface.altura_tela))
        self.SetMaxSize((Interface.largura_tela, Interface.altura_tela))

        self.Show(True)
        self.app.MainLoop()

    def cria_interface(self):
        self.arquivo_gravacao = "saida_serial_arduino.txt"
        self.arquivo_gravacao_csv = "saida_serial_arduino.csv"

        self.informacoes_leitura = []

        self.sizer_janela = wx.BoxSizer(wx.HORIZONTAL)

        #seta cor de fundo branca
        self.SetBackgroundColour("white")

        #inicia o leitor serial
        self.leitor = Leitor.Leitor(self)

        #adiciona status bar
        self.CreateStatusBar()
        self.SetStatusText("Ok")

        #cria botão de iniciar e finalizar
        self.btn_iniciar = wx.Button(self, 2, "Iniciar", (10, 10), (Interface.largura_botoes, Interface.altura_botoes))
        self.btn_finalizar = wx.Button(self, 3, "Finalizar", (20 + Interface.largura_botoes, 10), (Interface.largura_botoes, Interface.altura_botoes))
        self.Bind(wx.EVT_BUTTON, self.on_iniciar, id=2)
        self.Bind(wx.EVT_BUTTON, self.on_finalizar, id=3)

        #cria o panel onde ficará a grid
        self.panel_grid = scrolledpanel.ScrolledPanel(self, -1, (10, 70), (200, 300))

        #cria os graficos
        self.grafico_velocidade = Grafico(self, (500, 10))
        self.grafico_aceleracao = Grafico(self, (500, Grafico.altura_grafico + 10))

        #cria a grid para mostrar os dados da leitura mostrando no panel
        self.grid_dados = wxgrid.Grid(self.panel_grid)
        self.grid_dados.CreateGrid(0, 4)
        self.grid_dados.SetColLabelValue(0, "T")
        self.grid_dados.SetColLabelValue(1, "X")
        self.grid_dados.SetColLabelValue(2, "V")
        self.grid_dados.SetColLabelValue(3, "A")

        #cria os sizer para os objetos da tela
        self.sizer_grid = wx.BoxSizer(wx.VERTICAL)
        self.sizer_velocidade = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_aceleracao = wx.BoxSizer(wx.HORIZONTAL)

        #adiciona os objetos nos sizers
        self.sizer_velocidade.Add(self.grafico_velocidade)
        self.sizer_aceleracao.Add(self.grafico_aceleracao)
        self.sizer_grid.Add(self.grid_dados)
        self.panel_grid.SetSizerAndFit(self.sizer_grid)
        self.grafico_velocidade.SetSizerAndFit(self.sizer_velocidade)
        self.grafico_aceleracao.SetSizerAndFit(self.sizer_aceleracao)

        self.arquivo = None
        self.arquivo_csv = None

        #conecta o evento de fechar a janela a função
        self.Bind(wx.EVT_CLOSE, self.on_close)

    #Evento do botao iniciar
    def on_iniciar(self, event):
        self.StatusBar.SetStatusText("Lendo dados da porta serial...")
        self.leitor.inicia()
        self.arquivo = open(self.arquivo_gravacao, "w")
        self.arquivo_csv = open(self.arquivo_gravacao_csv, "w")

    #Evento do botão finalizar
    def on_finalizar(self, event):
        self.StatusBar.SetStatusText("Ok")
        self.leitor.finaliza()

        if not self.arquivo == None:
            self.arquivo.close()

        if not self.arquivo_csv == None:
            self.arquivo_csv.close()

    def receber(self, dado_leitura):
        #calcula os dados
        try:
           informacoes = float(dado_leitura.dado)

           informacoes = DadoLeituraVelocidadeAceleracao(informacoes, dado_leitura.tempo)
        except Exception:
            return None

        print(informacoes)

        if (not self.arquivo.closed):
            self.arquivo.write(informacoes.__str__() + '\r')

        if (not self.arquivo_csv.closed):
            self.arquivo_csv.write(informacoes.get_csv() + '\r')

        self.grid_dados.AppendRows()
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 0, str(informacoes.tempo))
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 1, str(informacoes.posicao_cm))
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 2, str(informacoes.velocidade))
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 3, str(informacoes.aceleracao))

        self.informacoes_leitura.append(informacoes)

        velocidades = []
        tempos = []
        posicoes = []

        for informacao in self.informacoes_leitura:
            tempos.append(informacao.tempo)
            posicoes.append(informacao.posicao_cm)
            velocidades.append(informacao.velocidade)

        self.grafico_velocidade.desenha(tempos, posicoes)
        self.grafico_aceleracao.desenha(tempos, velocidades)

        if (self.panel_grid.Size.GetHeight() < self.Size.GetHeight() - 150):
            self.panel_grid.SetSizerAndFit(self.sizer_grid)

    def on_close(self, event):
        self.on_finalizar(event)
        self.app.Exit()