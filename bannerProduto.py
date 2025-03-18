
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.app import App
from botoes import *
from functools import partial

class BannerProduto(GridLayout):

    def __init__(self, **kwargs):
        self.rows = 1
        super().__init__()
        with self.canvas:
            Color(rgb=(0, 0, 0, 1))
            self.rec = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.atualiza_rec, size=self.atualiza_rec)
        codigo = kwargs['codigo']
        referencia = kwargs['codigo'][:7]
        cor = kwargs['cor']
        tamanho = kwargs['tamanho']
        descricao = kwargs['descricao'][:20]
        preco = kwargs['preco']
        self.id = codigo
        produto = FloatLayout()
        label_referencia = Label(text=f'Referencia: [color=#00CFDB]{referencia}[/color]', markup=True, pos_hint={'right': 0.37, 'top': 0.95}, size_hint=(0.3, 0.33))
        label_nome = Label(text=f'Descricão: [color=#00CFDB]{descricao}[/color]', markup=True, pos_hint={'right': 0.60, 'top': 0.45}, size_hint=(0.5, 0.5))
        label_preco = Label(text=f'Preço: [color=#00CFDB]{preco}[/color]', markup=True, pos_hint={'right': 0.32, 'top': 0.7}, size_hint=(0.2, 0.33))
        label_cor = Label(text=f'Cor: [color=#00CFDB]{cor}[/color]', markup=True, pos_hint={'right': 0.8, 'top': 0.95}, size_hint=(0.2, 0.33))
        label_tamanho = Label(text=f'Tamanho: [color=#00CFDB]{tamanho}[/color]', markup=True, pos_hint={'right': 0.8, 'top': 0.7}, size_hint=(0.2, 0.33))
        label_codigo = Label(text='', pos_hint={'right': 0.4, 'top': 0.6}, size_hint=(0.3, 0.33))
        app = App.get_running_app()
        imagem = ImageButton(source='icones/excluir.png', pos_hint={'right': 1, 'top': 0.9}, size_hint=(0.12, 0.5), on_release=partial(app.excluir_item, codigo))
        produto.add_widget(label_referencia)
        produto.add_widget(label_nome)
        produto.add_widget(label_preco)
        produto.add_widget(label_cor)
        produto.add_widget(label_tamanho)
        produto.add_widget(label_codigo)
        produto.add_widget(imagem)
        self.add_widget(produto)

    def atualiza_rec(self, *args):
        self.rec.pos = self.pos
        self.rec.size = self.size

class BannerColeta(GridLayout):

    def __init__(self,**kwargs):
        self.rows = 1
        super().__init__()
        with self.canvas:
            Color(rgb=(0,0,0,1))
            self.rec = Rectangle(size= self.size, pos= self.pos)
        self.bind(pos=self.atualiza_rec, size=self.atualiza_rec)
        codigo = kwargs['codigo']
        nome = kwargs['nome']
        quantidade = kwargs['quantidade']
        id_usuario = kwargs['id_usuario']
        id_tela =  kwargs['id_tela']
        status = kwargs['status']
        self.id = codigo
        coleta = FloatLayout()
        label_nome = Label(text=f'Nome: {nome}', pos_hint={'right': 0.55, 'top': 0.95}, size_hint=(0.58, 0.33))
        label_qnt = Label(text=f'Quantidade: {quantidade}', pos_hint={'right': 0.35, 'top': 0.60}, size_hint=(0.2 , 0.33))
        self.id_tela_anterior = id_tela
        app = App.get_running_app()
        # imagem_lista = ImageButton(source='icones/list.png',
        #                      pos_hint={"right": 0.60, "top": 0.90}, size_hint=(0.20, 0.5),
        #                      on_release=partial(app.mudar_tela,'produtopage',codigo,id_usuario,self.id_tela_anterior))

        if status != '0':
            imagem = ImageButton(source='icones/ok.png',
                                 pos_hint={"right": 0.80, "top": 0.90}, size_hint=(0.12, 0.5))
            coleta.add_widget(imagem)

        coleta.add_widget(label_nome)
        coleta.add_widget(label_qnt)
        #coleta.add_widget(imagem_lista)

        self.add_widget(coleta)


    def atualiza_rec(self,*args):
        self.rec.pos = self.pos
        self.rec.size = self.size