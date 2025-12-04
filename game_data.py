# ==============================================================================
# BANCO DE DADOS DE TREINADORES (NPCs)
# ==============================================================================
# Este dicionário contém as configurações de cada NPC no jogo.
# A chave (ex: 'o1', 'p1') é o ID único usado para colocar o NPC no mapa (Tiled).
TRAINER_DATA = {
    # --- Bioma de Floresta (Inimigos Padrão) ---
    'o1': {
        # 'monsters': Define a equipe do NPC. 
        # Formato: {Slot: ('Nome do Monstro', Nível)}
        'monsters': {0: ('sapling', 14), 1: ('embercan', 15)},
        
        # 'dialog': Textos que aparecem na caixa de diálogo.
        # 'default': Antes da batalha. 'defeated': Após vencer o NPC.
        'dialog': {
            'default': ['Ei, como você está?', 'Oh, então você quer lutar?', 'LUTA!'],
            'defeated': ['Você é muito forte!', 'Vamos lutar novamente alguma hora?']},
        
        # 'directions': Lista de direções para onde o NPC pode olhar aleatoriamente.
        'directions': ['down'],
        
        # 'look_around': Se True, o NPC muda de direção aleatoriamente (gira).
        # Se False, ele fica fixo em uma direção.
        'look_around': True,
        
        # 'defeated': Estado inicial. Se True, o NPC já começa derrotado (útil para save games).
        'defeated': False,
        
        # 'biome': Define o fundo (background) que será carregado durante a batalha.
        'biome': 'forest'
    },
    'o2': {
        'monsters': {0: ('capiblu', 14), 1: ('embercan', 15), 2: ('earthshroud', 13), 3: ('sapling', 13)},
        'dialog': {
            'default': ['Eu não gosto de areia', 'É áspera e grossa', 'oh Deus, lute'],
            'defeated': ['Que a força esteja com você']},
        'directions': ['left', 'down'],
        'look_around': False,
        'defeated': False,
        'biome': 'sand'
    },
    'o3': {
        'monsters': {0: ('blazewhelp', 14), 1: ('earthshroud', 15), 2: ('capiblu', 13), 3: ('sapling', 13)},
        'dialog': {
            'default': ['Eu amo patinar!', 'LUTA!'],
            'defeated': ['Boa sorte com o chefe', 'Está tão frio aqui']},
        'directions': ['left', 'right', 'up', 'down'],
        'look_around': True,
        'defeated': False,
        'biome': 'sand'
    },
    # --- Bioma de Floresta (Níveis mais altos / Evoluções) ---
    'o4': {
        'monsters': {0: ('ignisblast', 25), 1: ('wardensawi', 20), 2: ('earthshroud', 24), 3: ('ararablair', 30)},
        'dialog': {
            'default': ['Eu amo patinar!', 'LUTA!'],
            'defeated': ['Boa sorte com o chefe', 'Está tão frio aqui']},
        'directions': ['right'],
        'look_around': True,
        'defeated': False,
        'biome': 'forest'
    },
    'o5': {
        'monsters': {0: ('ibyracy', 20), 1: ('carcalon', 22), 2: ('apexwing', 24), 3: ('earthshroud', 19)},
        'dialog': {
            'default': ['Então você quer desafiar os grandões', 'Isso será divertido!'],
            'defeated': ['Espero que os advogados nunca te encontrem', '<3']},
        'directions': ['up', 'right'],
        'look_around': True,
        'defeated': False,
        'biome': 'forest'
    },
    # --- Bioma de Gelo ---
    'o6': {
        'monsters': {0: ('ibyracy', 15), 1: ('ibyracy', 15), 2: ('ibyracy', 15)}, # Time monotemático
        'dialog': {
            'default': ['Eu amo patinar!', 'LUTA!'],
            'defeated': ['Boa sorte com o chefe', 'Está tão frio aqui']},
        'directions': ['down'],
        'look_around': False,
        'defeated': False,
        'biome': 'ice'
    },
    'o7': {
        'monsters': {0: ('ararablair', 25), 1: ('earthshroud', 20), 2: ('ignisblast', 24), 3: ('jatyglow', 30)},
        'dialog': {
            'default': ['Não há insetos na neve!'],
            'defeated': ['Talvez eu devesse verificar um vulcão...', 'Está tão frio aqui']},
        'directions': ['right'],
        'look_around': False,
        'defeated': False,
        'biome': 'ice'
    },
    # --- Patrulheiros / NPCs Especiais (Prefixos 'p', 'w', 'f') ---
    'p1': {
        'monsters': {0: ('primalsauim', 25), 1: ('earthshroud', 20), 2: ('ignisblast', 24), 3: ('ararablair', 30)},
        'dialog': {
            'default': ['Eu amo árvores', 'e lutas'],
            'defeated': ['Boa sorte com o chefe!']},
        'directions': ['right'],
        'look_around': False,
        'defeated': False,
        'biome': 'forest'
    },
    # (p2, p3, p4, px são clones de p1, usados para povoar o mapa)
    'p2': {
        'monsters': {0: ('primalsauim', 25), 1: ('earthshroud', 20), 2: ('ignisblast', 24), 3: ('ararablair', 30)},
        'dialog': {
            'default': ['Eu amo árvores', 'e lutas'],
            'defeated': ['Boa sorte com o chefe!']},
        'directions': ['right'],
        'look_around': False,
        'defeated': False,
        'biome': 'forest'
    },
    'p3': {
        'monsters': {0: ('primalsauim', 25), 1: ('earthshroud', 20), 2: ('ignisblast', 24), 3: ('ararablair', 30)},
        'dialog': {
            'default': ['Eu amo árvores', 'e lutas'],
            'defeated': ['Boa sorte com o chefe!']},
        'directions': ['right'],
        'look_around': False,
        'defeated': False,
        'biome': 'forest'
    },
    'p4': {
        'monsters': {0: ('primalsauim', 25), 1: ('earthshroud', 20), 2: ('ignisblast', 24), 3: ('ararablair', 30)},
        'dialog': {
            'default': ['Eu amo árvores', 'e lutas'],
            'defeated': ['Boa sorte com o chefe!']},
        'directions': ['right'],
        'look_around': False,
        'defeated': False,
        'biome': 'forest'
    },
    'px': {
        'monsters': {0: ('primalsauim', 25), 1: ('earthshroud', 20), 2: ('ignisblast', 24), 3: ('ararablair', 30)},
        'dialog': {
            'default': ['Eu amo árvores', 'e lutas'],
            'defeated': ['Boa sorte com o chefe!']},
        'directions': ['right'],
        'look_around': False,
        'defeated': False,
        'biome': 'forest'
    },
    # --- Treinadores de Inverno (W - Winter) ---
    'w1': {
        'monsters': {0: ('ararablair', 25), 1: ('earthshroud', 20), 2: ('primalsauim', 24), 3: ('ignisblast', 30)},
        'dialog': {
            'default': ['Está tão frio aqui', 'talvez uma luta me esquente'],
            'defeated': ['Boa sorte com o chefe!']},
        'directions': ['left'],
        'look_around': True,
        'defeated': False,
        'biome': 'ice'
    },
    'w2': {
        'monsters': {0: ('ararablair', 25), 1: ('earthshroud', 20), 2: ('primalsauim', 24), 3: ('ignisblast', 30)},
        'dialog': {
            'default': ['Está tão frio aqui', 'talvez uma luta me esquente'],
            'defeated': ['Boa sorte com o chefe!']},
        'directions': ['right'],
        'look_around': True,
        'defeated': False,
        'biome': 'ice'
    },
    'w3': {
        'monsters': {0: ('ararablair', 25), 1: ('earthshroud', 20), 2: ('primalsauim', 24), 3: ('ignisblast', 30)},
        'dialog': {
            'default': ['Está tão frio aqui', 'talvez uma luta me esquente'],
            'defeated': ['Boa sorte com o chefe!']},
        'directions': ['right'],
        'look_around': True,
        'defeated': False,
        'biome': 'ice'
    },
    'w4': {
        'monsters': {0: ('ararablair', 25), 1: ('earthshroud', 20), 2: ('primalsauim', 24), 3: ('ignisblast', 30)},
        'dialog': {
            'default': ['Está tão frio aqui', 'talvez uma luta me esquente'],
            'defeated': ['Boa sorte com o chefe!']},
        'directions': ['left'],
        'look_around': True,
        'defeated': False,
        'biome': 'ice'
    },
    'w5': {
        'monsters': {0: ('ararablair', 25), 1: ('earthshroud', 20), 2: ('primalsauim', 24), 3: ('ignisblast', 30)},
        'dialog': {
            'default': ['Está tão frio aqui', 'talvez uma luta me esquente'],
            'defeated': ['Boa sorte com o chefe!']},
        'directions': ['right'],
        'look_around': True,
        'defeated': False,
        'biome': 'ice'
    },
    # --- Chefe de Gelo (WX) ---
    'wx': {
        'monsters': {0: ('ararablair', 25), 1: ('earthshroud', 20), 2: ('primalsauim', 24), 3: ('ignisblast', 30)},
        'dialog': {
            'default': ['Espero que você tenha trazido rações', 'Esta será uma longa jornada'],
            'defeated': ['Parabéns!']},
        'directions': ['down'],
        'look_around': False,
        'defeated': False,
        'biome': 'ice'
    },
    # --- Treinadores de Fogo/Areia (F - Fire) ---
    'f1': {
        'monsters': {0: ('jatyglow', 15), 1: ('embercan', 20), 2: ('earthshroud', 24), 3: ('blazewhelp', 30)},
        'dialog': {
            'default': ['Este lugar parece meio quente...', 'luta!'],
            'defeated': ['Parabéns!']},
        'directions': ['right'],
        'look_around': True,
        'defeated': False,
        'biome': 'sand'
    },
    'f2': {
        'monsters': {0: ('jatyglow', 15), 1: ('embercan', 20), 2: ('earthshroud', 24), 3: ('blazewhelp', 30)},
        'dialog': {
            'default': ['Este lugar parece meio quente...', 'luta!'],
            'defeated': ['Parabéns!']},
        'directions': ['right', 'left'],
        'look_around': False,
        'defeated': False,
        'biome': 'sand'
    },
    'f3': {
        'monsters': {0: ('jatyglow', 15), 1: ('embercan', 20), 2: ('earthshroud', 24), 3: ('blazewhelp', 30)},
        'dialog': {
            'default': ['Este lugar parece meio quente...', 'luta!'],
            'defeated': ['Parabéns!']},
        'directions': ['right', 'left'],
        'look_around': True,
        'defeated': False,
        'biome': 'sand'
    },
    'f4': {
        'monsters': {0: ('jatyglow', 15), 1: ('embercan', 20), 2: ('earthshroud', 24), 3: ('blazewhelp', 30)},
        'dialog': {
            'default': ['Este lugar parece meio quente...', 'luta!'],
            'defeated': ['Parabéns!']},
        'directions': ['up', 'right'],
        'look_around': True,
        'defeated': False,
        'biome': 'sand'
    },
    'f5': {
        'monsters': {0: ('jatyglow', 15), 1: ('embercan', 20), 2: ('earthshroud', 24), 3: ('blazewhelp', 30)},
        'dialog': {
            'default': ['Este lugar parece meio quente...', 'luta!'],
            'defeated': ['Parabéns!']},
        'directions': ['left'],
        'look_around': True,
        'defeated': False,
        'biome': 'sand'
    },
    'f6': {
        'monsters': {0: ('jatyglow', 15), 1: ('embercan', 20), 2: ('earthshroud', 24), 3: ('blazewhelp', 30)},
        'dialog': {
            'default': ['Este lugar parece meio quente...', 'luta!'],
            'defeated': ['Parabéns!']},
        'directions': ['right'],
        'look_around': True,
        'defeated': False,
        'biome': 'sand'
    },
    # --- Chefe de Fogo (FX) ---
    'fx': {
        'monsters': {0: ('jatyglow', 15), 1: ('embercan', 20), 2: ('earthshroud', 24), 3: ('blazewhelp', 30)},
        'dialog': {
            'default': ['Hora de trazer o calor', 'luta!'],
            'defeated': ['Parabéns!']},
        'directions': ['down'],
        'look_around': False,
        'defeated': False,
        'biome': 'sand'
    },
    # --- Enfermeira (Cura) ---
    'Nurse': {
        'direction': 'down',
        'radius': 0, # Raio de interação (0 exige contato ou muito próximo)
        'look_around': False,
        'dialog': {
            'default': ['Bem-vindo ao hospital', 'Seus monstros foram curados'],
            'defeated': None # Enfermeira não batalha
        },
        'directions': ['down'],
        'defeated': False,
        'biome': None # Enfermeira não tem arena de batalha
    }
}

# ==============================================================================
# BANCO DE DADOS DE MONSTROS
# ==============================================================================
# Contém as estatísticas, caminhos de imagem e informações de evolução de cada criatura.
# A chave é o nome interno do monstro.
MONSTER_DATA = {
    # --------------------------------------------------------------------------
    # ELEMENTO: FOGO (Evolução: Embercan -> Blazewhelp -> Ignisblast)
    # --------------------------------------------------------------------------
    'embercan': {
        # 'stats': Atributos base.
        # recovery: Taxa de recuperação de energia. speed: Determina quem ataca primeiro.
        'stats': {'element': 'fire', 'max_health': 60, 'max_energy': 50, 'attack': 50, 'defense': 40, 'recovery': 1.0, 'speed': 60},
        
        # 'abilities': Habilidades disponíveis. A chave pode representar o nível de desbloqueio ou slot.
        'abilities': {0: 'scratch', 5: 'burn'},
        
        # 'exp': Experiência que o monstro concede ao ser derrotado.
        'exp': 60,
        
        # 'graphic_path': Localização da imagem do sprite.
        'graphic_path': 'graphics/monsters/embercan.png',
        
        # 'evolve': Nome do monstro para o qual ele evolui. None se não evoluir.
        'evolve': 'blazewhelp'
    },
    'blazewhelp': {
        'stats': {'element': 'fire', 'max_health': 100, 'max_energy': 70, 'attack': 80, 'defense': 60, 'recovery': 1.0, 'speed': 75},
        'abilities': {0: 'spark', 5: 'fire'},
        'exp': 140,
        'graphic_path': 'graphics/monsters/blazewhelp.png',
        'evolve': 'ignisblast'
    },
    'ignisblast': {
        'stats': {'element': 'fire', 'max_health': 150, 'max_energy': 100, 'attack': 120, 'defense': 90, 'recovery': 1.0, 'speed': 70},
        'abilities': {0: 'explosion', 5: 'annihilate'},
        'exp': 250,
        'graphic_path': 'graphics/monsters/ignisblast.png',
        'evolve': None # Estágio final
    },

    # --------------------------------------------------------------------------
    # ELEMENTO: PLANTA (Evolução: Sapling -> Wardensawi -> Primalsauim)
    # --------------------------------------------------------------------------
    'sapling': {
        'stats': {'element': 'grass', 'max_health': 70, 'max_energy': 60, 'attack': 45, 'defense': 50, 'recovery': 1.0, 'speed': 70},
        'abilities': {0: 'scratch', 5: 'heal'},
        'exp': 60,
        'graphic_path': 'graphics/monsters/sagreen.png',
        'evolve': 'wardensawi'
    },
    'wardensawi': {
        'stats': {'element': 'grass', 'max_health': 110, 'max_energy': 80, 'attack': 75, 'defense': 70, 'recovery': 1.0, 'speed': 85},
        'abilities': {0: 'battlecry', 5: 'scratch'},
        'exp': 140,
        'graphic_path': 'graphics/monsters/wardensawi.png',
        'evolve': 'primalsauim'
    },
    'primalsauim': {
        'stats': {'element': 'grass', 'max_health': 180, 'max_energy': 90, 'attack': 110, 'defense': 110, 'recovery': 1.0, 'speed': 60},
        'abilities': {0: 'scratch', 5: 'annihilate'},
        'exp': 250,
        'graphic_path': 'graphics/monsters/primalsauim.png',
        'evolve': None
    },

    # --------------------------------------------------------------------------
    # ELEMENTO: ÁGUA / TERRA (Evolução: Capiblu -> Earthshroud)
    # --------------------------------------------------------------------------
    'capiblu': {
        'stats': {'element': 'water', 'max_health': 90, 'max_energy': 50, 'attack': 40, 'defense': 60, 'recovery': 1.0, 'speed': 40},
        'abilities': {0: 'scratch', 5: 'splash'},
        'exp': 60,
        'graphic_path': 'graphics/monsters/capiblu.png',
        'evolve': 'earthshroud'
    },
    'earthshroud': {
        'stats': {'element': 'water', 'max_health': 200, 'max_energy': 80, 'attack': 90, 'defense': 130, 'recovery': 1.0, 'speed': 30},
        'abilities': {0: 'explosion', 5: 'splash'},
        'exp': 250,
        'graphic_path': 'graphics/monsters/earthshroud.png',
        'evolve': None
    },

    # --------------------------------------------------------------------------
    # ELEMENTO: VOADOR (Evoluções Variadas)
    # --------------------------------------------------------------------------
    # Linha: Araclaw -> Araguara -> Ararablair
    'araclaw': {
        'stats': {'element': 'flying', 'max_health': 50, 'max_energy': 50, 'attack': 60, 'defense': 30, 'recovery': 1.0, 'speed': 90},
        'abilities': {0: 'scratch', 5: 'battlecry'},
        'exp': 50,
        'graphic_path': 'graphics/monsters/araclaw.png',
        'evolve': 'araguara'
    },
    'araguara': {
        'stats': {'element': 'flying', 'max_health': 120, 'max_energy': 90, 'attack': 95, 'defense': 60, 'recovery': 1.0, 'speed': 110},
        'abilities': {0: 'scratch', 5: 'annihilate'},
        'exp': 180,
        'graphic_path': 'graphics/monsters/araguara.png',
        'evolve': 'ararablair'
    },
    'ararablair':{
        'stats': {'element': 'flying', 'max_health': 200, 'max_energy': 130, 'attack': 95, 'defense': 60, 'recovery': 1.0, 'speed': 135},
        'abilities': {0: 'scratch', 5: 'annihilate'},
        'exp': 180,
        'graphic_path': 'graphics/monsters/ararablair.png',
        'evolve': None
    },
    
    # Linha Reversa/Alternativa: Apexwing -> Carcalon -> Ibyracy
    'ibyracy': {
        'stats': {'element': 'flying', 'max_health': 130, 'max_energy': 80, 'attack': 110, 'defense': 70, 'recovery': 1.0, 'speed': 105},
        'abilities': {0: 'scratch', 5: 'battlecry'},
        'exp': 55,
        'graphic_path': 'graphics/monsters/ibyracy.png',
        'evolve': None
    },
    'carcalon': {
        'stats': {'element': 'flying', 'max_health': 90, 'max_energy': 70, 'attack': 90, 'defense': 55, 'recovery': 1.0, 'speed': 90},
        'abilities': {0: 'scratch', 5: 'ice'},
        'exp': 120,
        'graphic_path': 'graphics/monsters/carcalon.png',
        'evolve': 'ibyracy'
    },
    'apexwing': {
        'stats': {'element': 'flying', 'max_health': 60, 'max_energy': 60, 'attack': 70, 'defense': 40, 'recovery': 1.0, 'speed': 80},
        'abilities': {0: 'scratch', 5: 'fire'},
        'exp': 200,
        'graphic_path': 'graphics/monsters/apexwing.png',
        'evolve': 'carcalon'
    },

    # --------------------------------------------------------------------------
    # ELEMENTO: INSETO
    # --------------------------------------------------------------------------
    'jatyglow': {
        'stats': {'element': 'bug', 'max_health': 80, 'max_energy': 80, 'attack': 80, 'defense': 60, 'recovery': 1.0, 'speed': 100},
        'abilities': {0: 'scratch', 5: 'burn'},
        'exp': 150,
        'graphic_path': 'graphics/monsters/jatyglow.png',
        'evolve': '' # String vazia atua como None (sem evolução)
    },
}

# ==============================================================================
# DADOS DOS ATAQUES (Habilidades)
# ==============================================================================
# Define a lógica de cada habilidade usada nas batalhas.
# target: 'opponent' (dano inimigo) ou 'player' (afeta a si mesmo).
# amount: Multiplicador de dano ou valor base.
#         IMPORTANTE: Valores negativos em 'player' (ex: -1.2) geralmente indicam
#         cura ou buff na lógica deste jogo.
# cost: Custo de energia (mana) para usar.
ATTACK_DATA = {
    'burn':       {'target': 'opponent', 'amount': 2,    'cost': 15, 'element': 'fire',   'animation': 'fire'},
    'heal':       {'target': 'player',   'amount': -1.2, 'cost': 60, 'element': 'plant',  'animation': 'green'}, # Cura a si mesmo
    'battlecry':  {'target': 'player',   'amount': -1.4, 'cost': 20, 'element': 'normal', 'animation': 'green'}, # Buff em si mesmo
    'spark':      {'target': 'opponent', 'amount': 1.1,  'cost': 20, 'element': 'fire',   'animation': 'fire'},
    'scratch':    {'target': 'opponent', 'amount': 1.2,  'cost': 20, 'element': 'normal', 'animation': 'scratch'},
    'splash':     {'target': 'opponent', 'amount': 2,    'cost': 15, 'element': 'water',  'animation': 'splash'},
    'fire':       {'target': 'opponent', 'amount': 2,    'cost': 15, 'element': 'fire',   'animation': 'fire'},
    'explosion':  {'target': 'opponent', 'amount': 2,    'cost': 90, 'element': 'fire',   'animation': 'explosion'},
    'annihilate': {'target': 'opponent', 'amount': 3,    'cost': 30, 'element': 'fire',   'animation': 'explosion'},
    'ice':        {'target': 'opponent', 'amount': 2,    'cost': 15, 'element': 'water',  'animation': 'ice'},
}