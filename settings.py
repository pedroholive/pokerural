import pygame
from pygame.math import Vector2 as vector 
from sys import exit

# --- CONFIGURAÇÕES GERAIS DA JANELA E DO JOGO ---
# Define a resolução da tela (Largura x Altura). 1280x720 é o padrão HD (720p).
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

# Define o tamanho de cada "quadrado" do mapa. 
# O mapa é uma grade (grid). Cada tile terá 64x64 pixels.
TILE_SIZE = 64 

# Velocidade global das animações. 
# Quanto maior o número, mais quadros de animação são pulados ou mais rápido eles trocam.
ANIMATION_SPEED = 6

# Espessura da linha branca que aparece ao selecionar um monstro ou opção na batalha.
BATTLE_OUTLINE_WIDTH = 4

# --- PALETA DE CORES ---
# Um dicionário com códigos Hexadecimais para todas as cores usadas no jogo.
# Facilita o uso de nomes legíveis ('gold') em vez de códigos ('#ffd700') no código principal.
# Inclui cores para UI, texto e tipos de elementos (fogo, água, planta).
COLORS = {
    'white': '#f4fefa', 
    'pure white': '#ffffff',
    'dark': '#2b292c',
    'light': '#c8c8c8',
    'gray': '#3a373b',
    'gold': '#ffd700',      # Usado para seleção ou destaque
    'light-gray': '#4b484d',
    'fire':'#f8a060',       # Cor temática do tipo Fogo
    'water':'#50b0d8',      # Cor temática do tipo Água
    'plant': '#64a990',     # Cor temática do tipo Planta
    'black': '#000000', 
    'red': '#f03131',       # Geralmente usado para barra de Vida (HP)
    'blue': '#66d7ee',      # Geralmente usado para barra de Energia (Mana)
    'normal': '#ffffff',
    'dark white': '#f0f0f0'
}

# --- CAMADAS DO MUNDO (OVERWORLD LAYERS) ---
# Define a ordem de desenho (Z-Index) no mapa de exploração.
# O Pygame desenha em ordem: números menores ficam no fundo, maiores ficam na frente.
WORLD_LAYERS = {
    'water': 0,   # Desenhado primeiro (fundo absoluto)
    'bg': 1,      # Terreno sólido (grama, areia)
    'shadow': 2,  # Sombras (desenhadas entre o chão e o personagem)
    'main': 3,    # Personagens, Jogador e Paredes
    'top': 4      # Copas das árvores (o jogador passa "por baixo" visualmente)
}

# --- POSIÇÕES DA BATALHA ---
# Define as coordenadas (X, Y) onde os monstros ficarão parados durante a luta.
# O jogo suporta até 3 monstros de cada lado (top, center, bottom).
BATTLE_POSITIONS = {
    'left': {'top': (360, 260), 'center': (190, 400), 'bottom': (410, 520)},   # Posições do Jogador
    'right': {'top': (900, 260), 'center': (1110, 390), 'bottom': (900, 550)}  # Posições do Inimigo
}

# --- CAMADAS DA BATALHA (BATTLE LAYERS) ---
# Define a ordem de desenho dentro da cena de batalha.
BATTLE_LAYERS =  {
    'outline': 0, # O contorno de seleção (desenhado atrás do monstro)
    'name': 1,    # O chão/base onde o monstro pisa ou seu nome
    'monster': 2, # O sprite do monstro em si
    'effects': 3, # Partículas de ataques (fogo, explosão) ficam na frente do monstro
    'overlay': 4  # UI, menus e barras de vida ficam na frente de tudo
}

# --- MENUS DE BATALHA (UI) ---
# Define a disposição dos ícones de comando (Lutar, Defender, Trocar, Capturar).
# 'pos': É um vetor relativo ao centro do menu radial.
# 'icon': O nome do arquivo de imagem a ser carregado.
BATTLE_CHOICES = {
    # Menu Completo: Usado contra monstros selvagens (permite capturar/catch)
    'full': {
        'fight':  {'pos' : vector(30, -60), 'icon': 'sword'},
        'defend': {'pos' : vector(40, -20), 'icon': 'shield'},
        'switch': {'pos' : vector(40, 20), 'icon': 'arrows'},
        'catch':  {'pos' : vector(30, 60), 'icon': 'hand'}}, # Opção extra
    
    # Menu Limitado: Usado contra Treinadores (não pode capturar monstro de outra pessoa)
    'limited': {
        'fight':  {'pos' : vector(30, -40), 'icon': 'sword'},
        'defend': {'pos' : vector(40, 0), 'icon': 'shield'},
        'switch': {'pos' : vector(30, 40), 'icon': 'arrows'}}
}