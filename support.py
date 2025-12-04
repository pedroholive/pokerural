from settings import *
from os.path import join
from os import walk # Função vital para navegar pelas pastas do sistema operacional
from pytmx.util_pygame import load_pygame # Biblioteca externa para ler mapas do Tiled (.tmx)

# ==============================================================================
# IMPORTAÇÃO DE IMAGENS E ARQUIVOS
# ==============================================================================

def import_image(*path, alpha = True, format = 'png'):
    """
    Carrega uma única imagem do disco.
    *path: Permite passar pastas separadas como argumentos ('graphics', 'items', 'espada').
    alpha: Se True, mantém a transparência (PNG). Se False, converte para opaco (melhor performance para fundos).
    """
    full_path = join(*path) + f'.{format}'
    # convert_alpha() é crucial para sprites com fundo transparente.
    # convert() é mais rápido para o computador desenhar, mas perde a transparência.
    surf = pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()
    return surf

def simple_icon_importer(folder_path):
    """
    Carrega ícones de uma pasta e normaliza os nomes para minúsculo.
    Isso evita erros onde o código pede 'embercan' e o arquivo chama 'Embercan.png'.
    """
    icon_frames = {}
    
    # Navega pela pasta
    for folder_name, sub_folders, file_names in walk(folder_path):
        for file_name in file_names:
            if file_name.endswith(('.png', '.jpg', '.jpeg')):
                full_path = join(folder_name, file_name)
                
                # Carrega a imagem
                surf = pygame.image.load(full_path).convert_alpha()
                
                # Cria a chave do dicionário (nome do arquivo sem extensão, em minúsculo)
                key_name = file_name.split('.')[0].lower()
                
                icon_frames[key_name] = surf
                
    return icon_frames

def import_folder(*path):
    """
    Importa uma sequência de imagens para uma LISTA.
    Usado para animações frame a frame (ex: frame 0, frame 1, frame 2...).
    """
    frames = []
    for folder_path, sub_folders, image_names in walk(join(*path)):
        # 'sorted' garante que a animação toque na ordem certa (0, 1, 2...) e não aleatória
        for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
            full_path = join(folder_path, image_name)
            surf = pygame.image.load(full_path).convert_alpha()
            frames.append(surf)
    return frames

def import_folder_dict(*path):
    """
    Importa imagens para um DICIONÁRIO {nome_arquivo: imagem}.
    Usado para carregar assets que não são animações sequenciais (ex: tiles de terreno).
    """
    frames = {}
    for folder_path, sub_folders, image_names in walk(join(*path)):
        for image_name in image_names:
            full_path = join(folder_path, image_name)
            surf = pygame.image.load(full_path).convert_alpha()
            frames[image_name.split('.')[0]] = surf
    return frames

def import_sub_folders(*path):
    """
    Importa imagens recursivamente (pastas dentro de pastas).
    Retorna um dicionário onde a chave é o nome da subpasta.
    """
    frames = {}
    for _, sub_folders, __ in walk(join(*path)):
        if sub_folders:
            for sub_folder in sub_folders:
                frames[sub_folder] = import_folder(*path, sub_folder)
    return frames

# ==============================================================================
# MANIPULAÇÃO DE SPRITESHEETS (RECORTES)
# ==============================================================================

def import_tilemap(cols, rows, *path):
    """
    Corta uma imagem grande (SpriteSheet) em vários pedaços menores (Grid).
    cols: Quantas colunas tem a imagem.
    rows: Quantas linhas tem a imagem.
    """
    frames = {}
    surf = import_image(*path) # Carrega a imagem completa
    
    # Calcula o tamanho de cada célula individual
    cell_width, cell_height = surf.get_width() / cols, surf.get_height() / rows
    
    for col in range(cols):
        for row in range(rows):
            # Define o retângulo da área que queremos cortar
            cutout_rect = pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height)
            
            # Cria uma superfície nova vazia
            cutout_surf = pygame.Surface((cell_width, cell_height))
            cutout_surf.fill('green') # Preenche de verde
            cutout_surf.set_colorkey('green') # Diz que "verde é transparente" (Chroma Key)
            
            # Copia apenas o pedaço do retângulo para a nova superfície
            cutout_surf.blit(surf, (0,0), cutout_rect)
            
            # Salva no dicionário usando coordenadas (x, y) como chave
            frames[(col, row)] = cutout_surf
    return frames

def character_importer(cols, rows, *path):
    """
    Usa o import_tilemap para organizar sprites de personagens.
    Assume o padrão clássico de RPG Maker:
    Linha 0: Baixo, Linha 1: Esquerda, Linha 2: Direita, Linha 3: Cima.
    """
    frame_dict = import_tilemap(cols, rows, *path)
    new_dict = {}
    for row, direction in enumerate(('down', 'left', 'right', 'up')):
        # Pega todas as colunas daquela linha para criar a animação de andar
        new_dict[direction] = [frame_dict[(col, row)] for col in range(cols)]
        # Pega apenas a primeira coluna para o estado 'idle' (parado)
        new_dict[f'{direction}_idle'] = [frame_dict[(0, row)]]
    return new_dict

def all_character_import(*path):
    """
    Wrapper para importar todos os personagens de uma pasta de uma vez.
    """
    new_dict = {}
    for _, __, image_names in walk(join(*path)):
        for image in image_names:
            image_name = image.split('.')[0]
            # Chama a função acima para cada arquivo encontrado
            new_dict[image_name] = character_importer(4,4,*path, image_name)
    return new_dict

def coast_importer(cols, rows, *path):
    """
    Importador complexo para tiles de costa/água.
    Organiza os tiles baseado em sua posição (canto superior, borda esquerda, etc)
    para criar o autotiling.
    """
    frame_dict = import_tilemap(cols, rows, *path)
    new_dict = {}
    terrains = ['grass', 'grass_i', 'sand_i', 'sand', 'rock', 'rock_i', 'ice', 'ice_i']
    sides = {
        'topleft': (0,0), 'top': (1,0), 'topright': (2,0), 
        'left': (0,1), 'right': (2,1), 'bottomleft': (0,2), 
        'bottom': (1,2), 'bottomright': (2,2)}
    
    for index, terrain in enumerate(terrains):
        new_dict[terrain] = {}
        for key, pos in sides.items():
            # Aritmética para pular para o próximo bloco de terreno no spritesheet
            new_dict[terrain][key] = [frame_dict[(pos[0] + index * 3, pos[1] + row)] for row in range(0,rows, 3)]
    return new_dict

def tmx_importer(*path):
    """
    Carrega arquivos de mapa do Tiled (.tmx).
    """
    tmx_dict = {}
    for folder_path, sub_folders, file_names in walk(join(*path)):
        for file in file_names:
            tmx_dict[file.split('.')[0]] = load_pygame(join(folder_path, file))
    return tmx_dict

def monster_importer(cols, rows, *path):
    """
    Importador específico para monstros de batalha.
    Separa as linhas em 'idle' (parado) e 'attack' (atacando).
    """
    monster_dict = {}
    for folder_path, sub_folders, image_names in walk(join(*path)):
        for image in image_names:
            image_name = image.split('.')[0]
            monster_dict[image_name] = {}
            frame_dict = import_tilemap(cols, rows, *path, image_name)
            for row, key in enumerate(('idle', 'attack')):
                monster_dict[image_name][key] = [frame_dict[(col,row)] for col in range(cols)]
    return monster_dict

def outline_creator(frame_dict, width):
    """
    Cria um contorno branco ao redor dos sprites.
    Técnica: Pega a silhueta (máscara) do sprite e a desenha 8 vezes deslocada
    ao redor do centro, criando uma borda grossa.
    """
    outline_frame_dict = {}
    for monster, monster_frames in frame_dict.items():
        outline_frame_dict[monster] = {}
        for state, frames in monster_frames.items():
            outline_frame_dict[monster][state] = []
            for frame in frames:
                # Cria uma superfície maior para caber o contorno
                new_surf = pygame.Surface(vector(frame.get_size()) + vector(width * 2), pygame.SRCALPHA)
                new_surf.fill((0,0,0,0))
                
                # Cria a máscara branca
                white_frame = pygame.mask.from_surface(frame).to_surface()
                white_frame.set_colorkey('black')

                # Desenha a máscara branca em todas as direções (Cima, Baixo, Diagonais, Lados)
                new_surf.blit(white_frame, (0,0))
                new_surf.blit(white_frame, (width,0))
                new_surf.blit(white_frame, (width * 2,0))
                new_surf.blit(white_frame, (width * 2,width))
                new_surf.blit(white_frame, (width * 2,width * 2))
                new_surf.blit(white_frame, (width,width * 2))
                new_surf.blit(white_frame, (0,width * 2))
                new_surf.blit(white_frame, (0,width))
                
                # O resultado final é uma imagem "gorda" e branca que servirá de fundo
                outline_frame_dict[monster][state].append(new_surf)
    return outline_frame_dict

def attack_importer(*path):
    """
    Carrega animações de ataques (geralmente uma faixa horizontal de frames).
    """
    attack_dict = {}
    for folder_path, _, image_names in walk(join(*path)):
        for image in image_names:
            image_name = image.split('.')[0]
            # Assume 4 frames por animação em 1 linha
            attack_dict[image_name] = list(import_tilemap(4,1,folder_path, image_name).values())
    return attack_dict

def audio_importer(*path):
    """
    Carrega todos os arquivos de som de uma pasta.
    """
    files = {}
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in file_names:
            full_path = join(folder_path, file_name)
            files[file_name.split('.')[0]] = pygame.mixer.Sound(full_path)
    return files

# ==============================================================================
# FUNÇÕES DE UI E LÓGICA DE JOGO
# ==============================================================================

def draw_bar(surface, rect, value, max_value, color, bg_color, radius = 1):
    """
    Desenha uma barra de progresso (Vida/Energia).
    Desenha dois retângulos: um fundo (bg_rect) e a barra atual por cima (progress_rect).
    """
    ratio = rect.width / max_value # Calcula quantos pixels valem 1 ponto de vida
    bg_rect = rect.copy()
    
    # Calcula a largura da barra colorida
    progress = max(0, min(rect.width, value * ratio))
    progress_rect = pygame.FRect(rect.topleft, (progress, rect.height))
    
    pygame.draw.rect(surface, bg_color, bg_rect, 0, radius) # Desenha fundo
    pygame.draw.rect(surface, color, progress_rect, 0, radius) # Desenha valor

def check_connections(radius, entity, target, tolerance = 30):
    """
    Verifica se uma 'entidade' (Jogador) está olhando para e perto de um 'target' (NPC).
    Usado para iniciar diálogos.
    """
    # Calcula o vetor de distância
    relation = vector(target.rect.center) - vector(entity.rect.center)
    
    # Se estiver perto o suficiente (dentro do raio)
    if relation.length() < radius:
        # Verifica a direção e o alinhamento.
        # Ex: Se o jogador olha para a esquerda ('left'), o NPC deve estar à esquerda (relation.x < 0)
        # e mais ou menos na mesma altura (abs(relation.y) < tolerance).
        if entity.facing_direction == 'left' and relation.x < 0 and abs(relation.y) < tolerance or\
           entity.facing_direction == 'right' and relation.x > 0 and abs(relation.y) < tolerance or\
           entity.facing_direction == 'up' and relation.y < 0 and abs(relation.x) < tolerance or\
           entity.facing_direction == 'down' and relation.y > 0 and abs(relation.x) < tolerance:
            return True