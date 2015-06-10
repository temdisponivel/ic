# -*- coding: utf-8 -*-
import wx
import wx.grid as wxgrid
import wx.lib.scrolledpanel as scrolledpanel
import leitor_serial as Leitor
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas


class DadoLeitura():

    VELOCIDADE = 0
    ACELERACAO = 0
    TEMPO = 0
    POSICAO = 0

    def __init__(self, dado, tempo_leitura):
        dadoFloat = float(dado)
        DadoLeitura.TEMPO = tempo_leitura #tempo em millisegundos*
        DadoLeitura.POSICAO = dadoFloat / 29.0 / 2.0 #distancia em CM
        DadoLeitura.VELOCIDADE = DadoLeitura.POSICAO / DadoLeitura.TEMPO
        DadoLeitura.ACELERACAO = DadoLeitura.VELOCIDADE / DadoLeitura.TEMPO

    def __str__(self):
        return "Tempo: " + str(DadoLeitura.TEMPO) + " | Posição: " + str(DadoLeitura.POSICAO) + " | Velocidade: " + str(DadoLeitura.VELOCIDADE) + " | Aceleração: " + str(DadoLeitura.ACELERACAO)

    def GetCsv(self):
        return str(DadoLeitura.TEMPO) + "," + str(DadoLeitura.POSICAO) + "," + str(DadoLeitura.VELOCIDADE) + "," + str(DadoLeitura.ACELERACAO)

class Grafico(wx.Panel):

    ALTURA_GRAFICO = 1000
    LARGURA_GRAFICO = 1000

    def __init__(self, pai, posicao):
        wx.Panel.__init__(self, pai, -1, posicao, size=(Grafico.LARGURA_GRAFICO, Grafico.ALTURA_GRAFICO))

        #cria uma nova figura que vai conter o grafico
        self.figura = Figure()

        #cria um canvas para imagem
        self.canvas = FigureCanvas(self, -1, self.figura)

        #cria um só plot
        self.eixos = self.figura.add_subplot(111)

    #desenha os pontos x e y. Dois vetores que devem ter o mesmo tamanho
    #os vertices serão (pontosX[n], pontosY[n])
    def Desenha(self, pontosX, pontosY):
        #adiciona os pontos x e y no grafico
        self.eixos.plot(pontosX, pontosY)
        self.canvas.draw()



#classe do programa, contem os controles de tela, a janela, etc. Herda de wx.Frame
class Interface(wx.Frame):

    LARGURA_TELA = 1024
    ALTURA_TELA = 768
    LARGURA_BOTOES = 75
    ALTURA_BOTOES = 25

    def __init__(self):
        #cria o aplicativo
        self.app = wx.App()

        self.arquivo_gravacao = "saida_serial_arduino.txt"
        self.arquivo_gravacao_csv = "saida_serial_arduino.csv"

        self.informacoes_leitura = []

        #chama o contrutor do pai - wx.Frame
        wx.Frame.__init__(self, None, 0, "Sensor Sônico", (0, 0), (Interface.LARGURA_TELA, Interface.ALTURA_TELA))

        #seta cor de fundo branca
        self.SetBackgroundColour("white")

        #inicia o leitor serial
        self.leitor = Leitor.Leitor(self)

        #adiciona status bar
        self.CreateStatusBar()
        self.SetStatusText("Ok")

        #cria botão de iniciar e finalizar
        self.btn_iniciar = wx.Button(self, 2, "Iniciar", (10, 10), (Interface.LARGURA_BOTOES, Interface.ALTURA_BOTOES))
        self.btn_finalizar = wx.Button(self, 3, "Finalizar", (20 + Interface.LARGURA_BOTOES, 10), (Interface.LARGURA_BOTOES, Interface.ALTURA_BOTOES))
        self.Bind(wx.EVT_BUTTON, self.OnIniciar, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnFinalizar, id=3)

        #cria o panel onde ficará a grid
        self.panel_grid = scrolledpanel.ScrolledPanel(self, -1, (10, 70), (100, 300))

        #cria os graficos
        self.grafico_velocidade = Grafico(self, (500, 10))
        self.grafico_aceleracao = Grafico(self, (500, 525))

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

        #mostra a tela e entra no loop de eventos do aplicativo
        self.Show(True)
        self.app.MainLoop()

    #Evento do botao iniciar
    def OnIniciar(self, event):
        #self.statusbar.SetStatusText("Lendo dados da porta serial...")
        self.leitor.Inicia()
        self.arquivo = open(self.arquivo_gravacao, "w")
        self.arquivo_csv = open(self.arquivo_gravacao_csv, "w")

    #Evento do botão finalizar
    def OnFinalizar(self, event):
        #self.statusbar.SetStatusText("Ok")
        self.leitor.Finaliza()
        self.arquivo.close()

    def RecebeLeitura(self, dados, tempo):
        #calcula os dados
        try:
           informacoes = float(dados)
           informacoes = DadoLeitura(informacoes, tempo)
        except Exception:
            return None

        print(informacoes)

        """
            abre, escreve e fecha o arquivo. Aberto e fechado a toda leitura de linha
            para que mesmo se a leitura for cancelada, haja dados no arquivo
        """
        if (not self.arquivo.closed):
            self.arquivo.write(informacoes.__str__() + '\r')

        if (not self.arquivo_csv.closed):
            self.arquivo_csv.write(informacoes.GetCsv() + '\r')

        self.grid_dados.AppendRows()
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 0, str(informacoes.TEMPO))
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 1, str(informacoes.POSICAO))
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 2, str(informacoes.VELOCIDADE))
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 3, str(informacoes.ACELERACAO))

        self.informacoes_leitura.append(informacoes)

        tempos = []
        posicoes = []

        for informacao in self.informacoes_leitura:
            tempos.append(informacao.TEMPO)
            posicoes.append(informacao.POSICAO)


        self.grafico_velocidade.Desenha(tempos, posicoes)

        if (self.panel_grid.Size.GetHeight() < self.Size.GetHeight() - 150):
            self.panel_grid.SetSizerAndFit(self.sizer_grid)



