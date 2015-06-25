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
        return super(DadoLeituraVelocidadeAceleracao, self).get_csv() + "," + str(self.posicao_cm) + "," + str(self.velocidade) + "," + str(self.aceleracao)

#classe que representa os graficos que sao mostrados na tela
class Grafico(wx.Panel):

    altura_grafico = 340
    largura_grafico = 550

    def __init__(self, pai, posicao, labely, labelx):
        wx.Panel.__init__(self, pai, -1, posicao, size=(Grafico.largura_grafico, Grafico.altura_grafico))

        self.labelx = labelx
        self.labely = labely

        self.inicia()

    #funcao que inicia os gráficos
    def inicia(self):
        #cria uma nova figura que vai conter o grafico
        self.figura = Figure()

        #cria um canvas para imagem
        self.canvas = FigureCanvas(self, -1, self.figura)

        #cria um só plot
        self.eixos = self.figura.add_subplot(111)
        self.eixos.set_ylabel(self.labely)
        self.eixos.set_xlabel(self.labelx)

        self.figura.set_size_inches(7, 4.2, forward=True)
        self.figura.set_edgecolor("m")

    #desenha os pontos x e y. Dois vetores que devem ter o mesmo tamanho
    #os vertices serão (pontosX[n], pontosY[n])
    def desenha(self, pontosX, pontosY):
        #adiciona os pontos x e y no grafico
        self.eixos.plot(pontosX, pontosY)
        self.canvas.draw()

    #limpa o grafico
    def limpa(self):
        self.inicia()



#classe do programa, contem os controles de tela, a janela, etc. Herda de wx.Frame
class Interface(wx.Frame, Leitor.RecebeLeitura):

    largura_tela = 1024
    altura_tela = 768
    largura_botoes = 75
    altura_botoes = 25

    def __init__(self):
        #cria o aplicativo
        self.app = wx.App()

        self.app.SetAppName("Sensor Sônico")

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
        self.btn_pausar = wx.Button(self, 3, "Pausar", (Interface.largura_botoes + 10, 10), (Interface.largura_botoes, Interface.altura_botoes))
        self.btn_finalizar = wx.Button(self, 4, "Finalizar", (Interface.largura_botoes * 2 + 10, 10), (Interface.largura_botoes, Interface.altura_botoes))
        self.Bind(wx.EVT_BUTTON, self.on_iniciar, id=2)
        self.Bind(wx.EVT_BUTTON, self.on_pausar, id=3)
        self.Bind(wx.EVT_BUTTON, self.on_finalizar, id=4)

        #cria check box para inicio automático de leitura
        self.chk_inicio_automatico = wx.CheckBox(self, 5, "Inicio automatico (inicia no movimento).", (10, Interface.altura_botoes + 20))
        self.Bind(wx.EVT_CHECKBOX, self.on_chk_inicio_automatico, id=5)

        #cria o panel onde ficará a grid
        self.panel_grid = scrolledpanel.ScrolledPanel(self, -1, (10, 70), (200, 300))

        #cria os graficos
        self.grafico_velocidade = Grafico(self, (425, 10), "POSICAO", "TEMPO")
        self.grafico_aceleracao = Grafico(self, (425, Grafico.altura_grafico + 20), "VELOCIDADE", "TEMPO")

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

        #define valores iniciais
        self.arquivo = None
        self.arquivo_csv = None
        self.automatico = False
        self.dado_inicial = None
        self.informacoes_leitura = []

        #inicia leitor dos dados
        self.leitor.inicia()

        #conecta o evento de fechar a janela a função
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def valida_leitura(self, dado):
        if self.automatico:
            if self.dado_inicial == None:
                self.dado_inicial = dado
            else:
                if (self.dado_inicial != dado):
                    #se vamos ler, podemos definir a leitura automatica como false e desabilita o checkbox durante leitura
                    self.automatico = False
                    self.chk_inicio_automatico.SetValue(False)
                    self.btn_iniciar.SetLabelText("Continuar")
                    self.desabilita([self.chk_inicio_automatico, self.btn_finalizar, self.btn_iniciar])
                    return True
                else:
                    return False
        else:
            return True

    #desabilita uma série de controles
    def desabilita(self, controles):
        for controle in controles:
            controle.Disable()

    #desabilita uma série de controles
    def habilita(self, controles):
        for controle in controles:
            controle.Enable()

    #função que limpa os dados da tela
    def limpa(self):
        if (self.grid_dados.NumberRows > 0):
            self.grid_dados.DeleteRows(0, self.grid_dados.GetNumberRows())

        #limpa os dados
        self.informacoes_leitura = []
        self.grafico_velocidade.limpa()
        self.grafico_aceleracao.limpa()
        self.leitor.reinicia()

        #fecha arquivos
        if (self.arquivo != None):
            self.arquivo.close()
        if (self.arquivo_csv != None):
            self.arquivo_csv.close()

    #evento do check box de inicio automatico
    def on_chk_inicio_automatico(self, event):
        self.automatico = not self.automatico
        self.chk_inicio_automatico.SetValue(self.automatico)

        if self.automatico:
            self.on_iniciar(event)
            self.dado_inicial = None

    #Evento do botao iniciar
    def on_iniciar(self, event):
        #limpa dados da tela
        self.StatusBar.SetStatusText("Lendo dados da porta serial...")

        self.leitor.continua()

        #abre arquivos para escrita
        if (self.arquivo == None or self.arquivo.closed):
            self.arquivo = open(self.arquivo_gravacao, "w")

        if (self.arquivo_csv == None or self.arquivo_csv):
            self.arquivo_csv = open(self.arquivo_gravacao_csv, "w")

        #escreve cabeçalho das tabelas
        self.arquivo_csv.write("Tempo,Dado Arduino,Posição CM,Velocidade,Aceleração \r")

        self.automatico = False
        self.chk_inicio_automatico.SetValue(False)
        self.btn_iniciar.SetLabelText("Continuar")
        self.desabilita([self.chk_inicio_automatico, self.btn_finalizar, self.btn_iniciar])

    #Evento do botão finalizar
    def on_pausar(self, event):
        self.StatusBar.SetStatusText("Ok")

        #finaliza leitura do arduino
        self.leitor.pausa()

        #habilita novamento o checkbox
        self.habilita([self.chk_inicio_automatico, self.btn_finalizar, self.btn_iniciar])

    #processa os dados lidos do arduino
    def receber(self, dado_leitura):

        #calcula os dados e valida se é um número válido
        try:
           informacoes = float(dado_leitura.dado)
           informacoes = DadoLeituraVelocidadeAceleracao(informacoes, dado_leitura.tempo)
        except Exception:
            return None

        #printa as informacoes no console
        print(informacoes)

        #valida se devemos processar as infomacoes (validacao necessaria por causa da leitura automatica)
        if not self.valida_leitura(informacoes):
            return None

        #escreve informações nos arquivos
        if (self.arquivo != None and not self.arquivo.closed):
            self.arquivo.write(informacoes.__str__() + '\r')
        if (self.arquivo_csv != None and not self.arquivo_csv.closed):
            self.arquivo_csv.write(informacoes.get_csv() + '\r')

        #adiciona a linha na grid
        self.grid_dados.AppendRows()
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 0, str(informacoes.tempo))
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 1, str(informacoes.posicao_cm))
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 2, str(informacoes.velocidade))
        self.grid_dados.SetCellValue(self.grid_dados.GetNumberRows()-1, 3, str(informacoes.aceleracao))

        #concatena as informacoes no vetor de informacoes
        self.informacoes_leitura.append(informacoes)

        velocidades = []
        tempos = []
        posicoes = []

        #separa as velocidades, tempos e posicoes de todas as leituras
        for informacao in self.informacoes_leitura:
            tempos.append(informacao.tempo)
            posicoes.append(informacao.posicao_cm)
            velocidades.append(informacao.velocidade)

        #printa tudo nos graficos
        self.grafico_velocidade.desenha(tempos, posicoes)
        self.grafico_aceleracao.desenha(tempos, velocidades)

        #atualiza tamanho da grid desde que seja menor que a janela
        if (self.panel_grid.Size.GetHeight() < self.Size.GetHeight() - 150):
            self.panel_grid.SetSizerAndFit(self.sizer_grid)

    #evento do botão limpar
    def on_finalizar(self, event):
        self.limpa()
        self.btn_iniciar.SetLabelText("Iniciar")

    #evento de fechar o programa
    def on_close(self, event):
        self.limpa()
        self.on_finalizar(event)
        self.leitor.finaliza()
        self.app.Exit()