"""
THE LIGHTHOUSE OF FORGOTTEN SOULS
A Sierra-style Adventure Game with EGA Graphics
By Claude - 2025

You are Morgan, a shipwrecked sailor who washes ashore on a mysterious island.
A ghostly lighthouse looms above, its light extinguished for centuries.
Restore the light and free the trapped souls to escape this cursed place.
"""

import pygame
import sys
import textwrap
import random
import math

# Initialize Pygame
pygame.init()

# EGA Color Palette (16 colors)
EGA_COLORS = {
    'black': (0, 0, 0),
    'blue': (0, 0, 170),
    'green': (0, 170, 0),
    'cyan': (0, 170, 170),
    'red': (170, 0, 0),
    'magenta': (170, 0, 170),
    'brown': (170, 85, 0),
    'light_gray': (170, 170, 170),
    'dark_gray': (85, 85, 85),
    'light_blue': (85, 85, 255),
    'light_green': (85, 255, 85),
    'light_cyan': (85, 255, 255),
    'light_red': (255, 85, 85),
    'light_magenta': (255, 85, 255),
    'yellow': (255, 255, 85),
    'white': (255, 255, 255)
}

# Screen setup (EGA-style 320x200 scaled up)
SCALE = 3
GAME_WIDTH = 320
GAME_HEIGHT = 200
SCREEN_WIDTH = GAME_WIDTH * SCALE
SCREEN_HEIGHT = GAME_HEIGHT * SCALE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Lighthouse of Forgotten Souls")
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

# Fonts
pygame.font.init()
font_small = pygame.font.Font(None, 16)
font_medium = pygame.font.Font(None, 20)

class GameState:
    def __init__(self):
        self.current_room = "beach"
        self.inventory = []
        self.flags = {
            'talked_to_ghost': False,
            'lighthouse_door_open': False,
            'lantern_lit': False,
            'mirror_placed': False,
            'lens_installed': False,
            'lighthouse_lit': False,
            'crab_moved': False,
            'found_secret_cave': False,
            'read_journal': False,
            'bell_rung': False,
            'game_won': False
        }
        self.message = "You awaken on a cold, misty beach. Waves crash nearby. A dark lighthouse looms to the north."
        self.message_timer = 0

    def add_to_inventory(self, item):
        if item not in self.inventory:
            self.inventory.append(item)
            return True
        return False

    def has_item(self, item):
        return item in self.inventory

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

# Room definitions
ROOMS = {
    'beach': {
        'name': 'Shipwreck Beach',
        'description': 'A desolate beach littered with driftwood and ship debris. The skeleton of your ship lies half-buried in sand. To the north, a worn path leads uphill toward a lighthouse. Rocky cliffs stretch east.',
        'exits': {'north': 'path', 'east': 'cliffs'},
        'items': ['driftwood', 'rope'],
        'examine': {
            'ship': 'The wreckage of the "Maiden\'s Hope". Your crew... you hope they made it somewhere safe.',
            'driftwood': 'Weathered wood from countless shipwrecks. One piece looks sturdy enough to use.',
            'rope': 'A length of good rope, still strong despite the saltwater.',
            'sand': 'Cold, gray sand. Something glints beneath the surface near the waterline.',
            'water': 'The sea churns endlessly, gray and unforgiving.'
        }
    },
    'cliffs': {
        'name': 'Rocky Cliffs',
        'description': 'Jagged cliffs overlook the churning sea. A narrow ledge leads to a cave entrance, but a large aggressive crab blocks the way. Seagulls cry overhead.',
        'exits': {'west': 'beach', 'north': 'cave'},
        'items': [],
        'examine': {
            'crab': 'A massive red crab with claws that could snap bone. It snaps menacingly when you approach the cave.',
            'cave': 'A dark opening in the cliff face. You can\'t reach it with that crab there.',
            'ledge': 'A narrow ledge, slippery with sea spray.',
            'seagulls': 'They wheel and cry, as if warning you of something.'
        }
    },
    'cave': {
        'name': 'Sea Cave',
        'description': 'A damp cave filled with the sound of dripping water. Bioluminescent algae casts an eerie blue-green glow. Ancient carvings cover the walls.',
        'exits': {'south': 'cliffs'},
        'items': ['crystal_lens', 'ancient_coin'],
        'examine': {
            'carvings': 'Spiraling symbols and images of a lighthouse with souls rising from it. One phrase is readable: "LIGHT REUNITES WHAT DARKNESS DIVIDES"',
            'algae': 'Strange glowing algae. It pulses gently, almost like breathing.',
            'crystal_lens': 'A perfectly shaped crystal lens, clearly crafted by skilled hands. It must be for the lighthouse!',
            'ancient_coin': 'An old coin bearing the image of a lighthouse keeper.',
            'water': 'A small pool of seawater. Something shimmers at the bottom.'
        }
    },
    'path': {
        'name': 'Winding Path',
        'description': 'A weathered stone path winds up the hillside. Wild roses grow alongside, their sweet scent mixing with sea salt. A ghostly figure stands near a crumbling well.',
        'exits': {'south': 'beach', 'north': 'lighthouse_exterior', 'east': 'garden'},
        'items': [],
        'examine': {
            'ghost': 'A translucent woman in old-fashioned dress. She gazes toward the lighthouse with profound sadness.',
            'well': 'An old stone well. A rusty bucket hangs from a frayed rope. You hear water far below.',
            'roses': 'Beautiful wild roses. Their thorns are sharp.',
            'path': 'Worn smooth by countless footsteps over the centuries.'
        }
    },
    'garden': {
        'name': 'Overgrown Garden',
        'description': 'What was once a lovely garden is now wild and overgrown. A stone bench sits beneath a gnarled apple tree. An old shed stands nearby, its door hanging open.',
        'exits': {'west': 'path', 'north': 'shed'},
        'items': ['matches', 'apple'],
        'examine': {
            'bench': 'Carved with two names: "ELIZA & THOMAS - FOREVER"',
            'tree': 'A twisted apple tree. A few withered apples still cling to its branches.',
            'apple': 'A small apple, surprisingly fresh.',
            'shed': 'A weathered tool shed. The door creaks ominously.',
            'flowers': 'Flowers long gone wild, but still beautiful in their chaos.'
        }
    },
    'shed': {
        'name': 'Garden Shed',
        'description': 'A dusty shed filled with old tools and forgotten things. Cobwebs drape everything. A workbench holds various items.',
        'exits': {'south': 'garden'},
        'items': ['oil_can', 'small_key'],
        'examine': {
            'tools': 'Rusty gardening tools hang on the wall.',
            'workbench': 'A sturdy workbench. An oil can and a small key rest on its surface.',
            'oil_can': 'A can of lamp oil, still half full after all these years.',
            'small_key': 'A small brass key with a lighthouse emblem.',
            'cobwebs': 'Thick cobwebs everywhere. This place hasn\'t been used in ages.'
        }
    },
    'lighthouse_exterior': {
        'name': 'Lighthouse Base',
        'description': 'You stand before the imposing lighthouse. Its white-washed walls are cracked and weathered. A heavy iron door blocks the entrance. A bronze bell hangs in a small tower nearby.',
        'exits': {'south': 'path', 'north': 'lighthouse_interior'},
        'items': [],
        'examine': {
            'door': 'A heavy iron door, locked tight. There\'s a small keyhole.',
            'lighthouse': 'The lighthouse rises high above, its dark windows like hollow eyes. The light chamber at the top is dark.',
            'bell': 'An old bronze bell, green with patina. A pull rope dangles from it.',
            'walls': 'Cracks spider across the walls. Names and dates are carved here - lighthouse keepers of old.'
        }
    },
    'lighthouse_interior': {
        'name': 'Lighthouse Interior',
        'description': 'The ground floor of the lighthouse. A spiral staircase winds upward into darkness. An old desk holds a dusty journal. A lantern hangs on a hook by the stairs.',
        'exits': {'south': 'lighthouse_exterior', 'up': 'lighthouse_stairs'},
        'items': ['lantern', 'journal'],
        'examine': {
            'staircase': 'Iron stairs spiral upward. They look sturdy enough.',
            'desk': 'An old keeper\'s desk. A journal lies open upon it.',
            'journal': 'The journal of Thomas Blackwood, lighthouse keeper. The final entry reads: "The storm took my Eliza. I will keep the light burning until she returns. I will wait forever if I must."',
            'lantern': 'An old brass lantern. It needs oil to work.',
            'photographs': 'Faded photographs on the wall show a happy couple - the keeper and his wife.'
        }
    },
    'lighthouse_stairs': {
        'name': 'Spiral Staircase',
        'description': 'You climb the winding stairs. Windows offer glimpses of the island below. The steps groan under your weight. Almost to the top...',
        'exits': {'down': 'lighthouse_interior', 'up': 'light_chamber'},
        'items': [],
        'examine': {
            'windows': 'Small windows look out over the island. You can see the beach where you washed ashore.',
            'stairs': 'Iron stairs, rusty but holding.',
            'walls': 'More names carved here. Keepers marking their time.'
        }
    },
    'light_chamber': {
        'name': 'Light Chamber',
        'description': 'The top of the lighthouse. A massive Fresnel lens housing stands in the center, but the main lens is missing. Mirrors surround the chamber to amplify the light. One mirror bracket is empty.',
        'exits': {'down': 'lighthouse_stairs'},
        'items': [],
        'examine': {
            'lens_housing': 'The great lens housing. A crystal lens would fit perfectly in the center mount.',
            'mirrors': 'Arrangement of mirrors to cast the light far across the sea. One bracket is empty.',
            'bracket': 'An empty bracket where a mirror should be.',
            'view': 'From here you can see the entire island... and countless ghostly ships on the horizon, waiting.',
            'mechanism': 'The turning mechanism for the light. It seems functional if only there was light.'
        }
    }
}

def draw_pixel_rect(surface, color, x, y, w, h):
    """Draw a rectangle with EGA colors"""
    pygame.draw.rect(surface, EGA_COLORS[color], (x, y, w, h))

def draw_dithered_rect(surface, color1, color2, x, y, w, h):
    """Draw a dithered rectangle for EGA-style gradients"""
    for py in range(y, y + h):
        for px in range(x, x + w):
            if (px + py) % 2 == 0:
                surface.set_at((px, py), EGA_COLORS[color1])
            else:
                surface.set_at((px, py), EGA_COLORS[color2])

def draw_beach(surface, state):
    """Draw the beach scene"""
    # Sky gradient (dithered)
    draw_dithered_rect(surface, 'dark_gray', 'blue', 0, 0, 320, 60)
    draw_pixel_rect(surface, 'dark_gray', 0, 60, 320, 20)

    # Sea
    draw_dithered_rect(surface, 'blue', 'dark_gray', 0, 80, 320, 30)
    draw_pixel_rect(surface, 'blue', 0, 110, 320, 10)

    # Beach
    draw_dithered_rect(surface, 'brown', 'yellow', 0, 120, 320, 30)
    draw_pixel_rect(surface, 'brown', 0, 150, 320, 10)

    # Shipwreck
    draw_pixel_rect(surface, 'brown', 180, 125, 60, 25)
    draw_pixel_rect(surface, 'brown', 200, 110, 8, 20)  # Mast
    pygame.draw.polygon(surface, EGA_COLORS['light_gray'], [(200, 110), (240, 120), (200, 125)])  # Torn sail

    # Driftwood
    if 'driftwood' not in state.inventory:
        draw_pixel_rect(surface, 'brown', 50, 140, 25, 5)
        draw_pixel_rect(surface, 'brown', 55, 138, 15, 3)

    # Rope
    if 'rope' not in state.inventory:
        for i in range(8):
            draw_pixel_rect(surface, 'yellow', 100 + i*3, 142 + (i%2)*2, 3, 2)

    # Lighthouse in distance
    draw_pixel_rect(surface, 'light_gray', 150, 20, 20, 60)
    draw_pixel_rect(surface, 'red', 150, 20, 20, 10)
    draw_pixel_rect(surface, 'dark_gray', 155, 10, 10, 10)  # Light chamber

    # Waves
    for i in range(0, 320, 20):
        pygame.draw.arc(surface, EGA_COLORS['light_cyan'], (i, 105, 20, 10), 0, 3.14, 1)

    # Mist effect
    for i in range(0, 320, 40):
        draw_dithered_rect(surface, 'light_gray', 'dark_gray', i, 70 + (i%20), 30, 5)

def draw_cliffs(surface, state):
    """Draw the cliffs scene"""
    # Sky
    draw_dithered_rect(surface, 'dark_gray', 'blue', 0, 0, 320, 50)

    # Sea below
    draw_pixel_rect(surface, 'blue', 0, 120, 320, 40)
    draw_dithered_rect(surface, 'blue', 'light_blue', 0, 140, 320, 20)

    # Cliffs
    draw_pixel_rect(surface, 'dark_gray', 0, 50, 320, 70)
    draw_dithered_rect(surface, 'dark_gray', 'brown', 0, 80, 320, 40)

    # Cliff details
    for i in range(0, 320, 30):
        h = 20 + (i % 15)
        draw_pixel_rect(surface, 'brown', i, 60, 25, h)

    # Cave entrance
    draw_pixel_rect(surface, 'black', 200, 70, 40, 35)
    draw_pixel_rect(surface, 'dark_gray', 195, 65, 50, 8)  # Cave top

    # Crab (if not moved)
    if not state.flags['crab_moved']:
        # Crab body
        draw_pixel_rect(surface, 'red', 175, 95, 20, 12)
        draw_pixel_rect(surface, 'light_red', 178, 98, 14, 6)
        # Claws
        draw_pixel_rect(surface, 'red', 165, 90, 10, 8)
        draw_pixel_rect(surface, 'red', 195, 90, 10, 8)
        # Eyes
        draw_pixel_rect(surface, 'black', 180, 93, 2, 2)
        draw_pixel_rect(surface, 'black', 188, 93, 2, 2)

    # Ledge
    draw_pixel_rect(surface, 'brown', 150, 105, 90, 5)

    # Seagulls
    for pos in [(50, 30), (100, 20), (280, 35)]:
        pygame.draw.lines(surface, EGA_COLORS['white'], False,
                         [(pos[0]-5, pos[1]+3), (pos[0], pos[1]), (pos[0]+5, pos[1]+3)], 1)

def draw_cave(surface, state):
    """Draw the sea cave"""
    # Cave walls
    draw_pixel_rect(surface, 'black', 0, 0, 320, 160)

    # Bioluminescent glow
    for i in range(50):
        x = random.randint(0, 319)
        y = random.randint(0, 120)
        color = 'cyan' if random.random() > 0.5 else 'light_cyan'
        surface.set_at((x, y), EGA_COLORS[color])

    # Cave walls detail
    draw_dithered_rect(surface, 'dark_gray', 'black', 0, 0, 40, 160)
    draw_dithered_rect(surface, 'dark_gray', 'black', 280, 0, 40, 160)

    # Ancient carvings
    for y in range(20, 100, 15):
        draw_pixel_rect(surface, 'cyan', 15, y, 20, 2)
        draw_pixel_rect(surface, 'cyan', 285, y, 20, 2)

    # Lighthouse symbol carving
    draw_pixel_rect(surface, 'light_cyan', 20, 40, 8, 20)
    draw_pixel_rect(surface, 'yellow', 22, 38, 4, 4)

    # Floor
    draw_dithered_rect(surface, 'dark_gray', 'blue', 0, 130, 320, 30)

    # Water pool
    draw_pixel_rect(surface, 'blue', 100, 135, 60, 20)
    draw_dithered_rect(surface, 'light_blue', 'blue', 105, 140, 50, 10)

    # Crystal lens (if not taken)
    if 'crystal_lens' not in state.inventory:
        draw_pixel_rect(surface, 'light_cyan', 200, 125, 15, 15)
        draw_pixel_rect(surface, 'white', 205, 130, 5, 5)

    # Ancient coin (if not taken)
    if 'ancient_coin' not in state.inventory:
        draw_pixel_rect(surface, 'yellow', 250, 140, 8, 8)
        draw_pixel_rect(surface, 'brown', 252, 142, 4, 4)

    # Light rays
    pygame.draw.line(surface, EGA_COLORS['cyan'], (160, 0), (140, 130), 1)
    pygame.draw.line(surface, EGA_COLORS['cyan'], (160, 0), (180, 130), 1)

def draw_path(surface, state):
    """Draw the winding path"""
    # Sky
    draw_dithered_rect(surface, 'dark_gray', 'light_gray', 0, 0, 320, 40)

    # Hills
    draw_pixel_rect(surface, 'green', 0, 40, 320, 120)
    draw_dithered_rect(surface, 'green', 'light_green', 0, 60, 320, 40)

    # Path
    pygame.draw.polygon(surface, EGA_COLORS['brown'], [(140, 160), (180, 160), (170, 80), (150, 80)])
    pygame.draw.polygon(surface, EGA_COLORS['yellow'], [(145, 160), (175, 160), (168, 85), (152, 85)])

    # Well
    draw_pixel_rect(surface, 'dark_gray', 230, 90, 30, 25)
    draw_pixel_rect(surface, 'black', 235, 95, 20, 15)
    draw_pixel_rect(surface, 'brown', 230, 85, 30, 8)  # Well roof
    draw_pixel_rect(surface, 'brown', 243, 70, 4, 15)  # Post

    # Roses
    for x in [80, 95, 110, 200, 210]:
        draw_pixel_rect(surface, 'green', x, 100, 4, 15)
        draw_pixel_rect(surface, 'light_red', x-2, 95, 8, 8)

    # Ghost
    ghost_x = 190
    ghost_y = 70
    # Ghostly glow
    draw_dithered_rect(surface, 'light_cyan', 'green', ghost_x-5, ghost_y-5, 30, 50)
    # Ghost figure
    draw_pixel_rect(surface, 'light_cyan', ghost_x, ghost_y, 20, 35)
    draw_pixel_rect(surface, 'white', ghost_x+2, ghost_y+2, 16, 25)
    # Face
    draw_pixel_rect(surface, 'light_blue', ghost_x+5, ghost_y+5, 3, 3)
    draw_pixel_rect(surface, 'light_blue', ghost_x+12, ghost_y+5, 3, 3)

    # Lighthouse in distance
    draw_pixel_rect(surface, 'light_gray', 150, 10, 20, 35)
    draw_pixel_rect(surface, 'red', 150, 10, 20, 8)

def draw_garden(surface, state):
    """Draw the overgrown garden"""
    # Sky
    draw_dithered_rect(surface, 'dark_gray', 'light_gray', 0, 0, 320, 30)

    # Background
    draw_pixel_rect(surface, 'green', 0, 30, 320, 130)

    # Overgrown plants everywhere
    for i in range(0, 320, 15):
        h = 20 + random.randint(0, 20)
        draw_pixel_rect(surface, 'light_green', i, 80, 10, h)
        if i % 30 == 0:
            draw_pixel_rect(surface, 'light_magenta', i+2, 75, 6, 6)  # Flowers

    # Apple tree
    draw_pixel_rect(surface, 'brown', 200, 60, 15, 50)  # Trunk
    draw_pixel_rect(surface, 'green', 170, 30, 60, 40)  # Foliage
    draw_pixel_rect(surface, 'light_green', 180, 40, 40, 25)
    # Apples
    if 'apple' not in state.inventory:
        draw_pixel_rect(surface, 'red', 185, 45, 6, 6)
    draw_pixel_rect(surface, 'red', 210, 50, 6, 6)

    # Stone bench
    draw_pixel_rect(surface, 'light_gray', 60, 100, 50, 10)
    draw_pixel_rect(surface, 'dark_gray', 65, 110, 10, 15)
    draw_pixel_rect(surface, 'dark_gray', 95, 110, 10, 15)

    # Shed
    draw_pixel_rect(surface, 'brown', 260, 60, 50, 50)
    draw_pixel_rect(surface, 'dark_gray', 260, 50, 50, 15)  # Roof
    draw_pixel_rect(surface, 'black', 275, 80, 15, 30)  # Door

    # Matches on ground
    if 'matches' not in state.inventory:
        draw_pixel_rect(surface, 'red', 120, 120, 10, 4)
        draw_pixel_rect(surface, 'brown', 122, 121, 6, 2)

def draw_shed(surface, state):
    """Draw inside the shed"""
    # Walls
    draw_pixel_rect(surface, 'brown', 0, 0, 320, 160)
    draw_dithered_rect(surface, 'brown', 'dark_gray', 0, 0, 320, 160)

    # Floor
    draw_pixel_rect(surface, 'dark_gray', 0, 130, 320, 30)

    # Workbench
    draw_pixel_rect(surface, 'brown', 80, 90, 160, 10)
    draw_pixel_rect(surface, 'brown', 90, 100, 10, 40)
    draw_pixel_rect(surface, 'brown', 220, 100, 10, 40)

    # Tools on wall
    draw_pixel_rect(surface, 'dark_gray', 50, 40, 5, 40)  # Shovel
    draw_pixel_rect(surface, 'brown', 48, 35, 9, 8)
    draw_pixel_rect(surface, 'dark_gray', 70, 50, 3, 30)  # Rake
    draw_pixel_rect(surface, 'brown', 65, 45, 13, 5)

    # Oil can (if not taken)
    if 'oil_can' not in state.inventory:
        draw_pixel_rect(surface, 'dark_gray', 120, 80, 15, 12)
        draw_pixel_rect(surface, 'yellow', 130, 75, 8, 8)  # Spout

    # Small key (if not taken)
    if 'small_key' not in state.inventory:
        draw_pixel_rect(surface, 'yellow', 180, 85, 12, 5)
        draw_pixel_rect(surface, 'yellow', 175, 83, 8, 8)

    # Cobwebs
    pygame.draw.lines(surface, EGA_COLORS['light_gray'], False,
                     [(0, 0), (40, 30), (20, 50), (50, 40)], 1)
    pygame.draw.lines(surface, EGA_COLORS['light_gray'], False,
                     [(320, 0), (280, 30), (300, 50), (270, 40)], 1)

    # Door (exit)
    draw_pixel_rect(surface, 'light_gray', 145, 100, 30, 50)
    draw_pixel_rect(surface, 'green', 150, 110, 20, 35)  # Light from outside

def draw_lighthouse_exterior(surface, state):
    """Draw the lighthouse exterior"""
    # Sky
    draw_dithered_rect(surface, 'dark_gray', 'blue', 0, 0, 320, 50)

    # Ground
    draw_pixel_rect(surface, 'green', 0, 120, 320, 40)
    draw_dithered_rect(surface, 'green', 'brown', 0, 140, 320, 20)

    # Lighthouse
    draw_pixel_rect(surface, 'light_gray', 120, 20, 80, 100)
    draw_pixel_rect(surface, 'white', 130, 30, 60, 80)
    # Red stripes
    for y in range(30, 110, 20):
        draw_pixel_rect(surface, 'red', 130, y, 60, 8)
    # Light chamber
    draw_pixel_rect(surface, 'dark_gray', 135, 10, 50, 15)
    draw_pixel_rect(surface, 'black', 140, 12, 40, 10)

    # If lighthouse is lit, show light!
    if state.flags['lighthouse_lit']:
        draw_pixel_rect(surface, 'yellow', 145, 13, 30, 8)
        # Light beams
        pygame.draw.polygon(surface, EGA_COLORS['yellow'],
                          [(160, 15), (0, 0), (0, 30)])
        pygame.draw.polygon(surface, EGA_COLORS['yellow'],
                          [(160, 15), (320, 0), (320, 30)])

    # Door
    if state.flags['lighthouse_door_open']:
        draw_pixel_rect(surface, 'black', 145, 90, 30, 35)
    else:
        draw_pixel_rect(surface, 'dark_gray', 145, 90, 30, 35)
        draw_pixel_rect(surface, 'brown', 148, 93, 24, 29)
        draw_pixel_rect(surface, 'yellow', 165, 108, 4, 4)  # Keyhole

    # Bell tower
    draw_pixel_rect(surface, 'brown', 50, 80, 30, 40)
    draw_pixel_rect(surface, 'brown', 45, 75, 40, 8)  # Roof
    draw_pixel_rect(surface, 'yellow', 58, 90, 14, 16)  # Bell
    draw_pixel_rect(surface, 'brown', 64, 106, 2, 15)  # Rope

    # Path
    draw_pixel_rect(surface, 'brown', 140, 120, 40, 40)

def draw_lighthouse_interior(surface, state):
    """Draw inside the lighthouse ground floor"""
    # Walls
    draw_pixel_rect(surface, 'light_gray', 0, 0, 320, 160)
    draw_dithered_rect(surface, 'light_gray', 'white', 20, 10, 280, 140)

    # Floor
    draw_pixel_rect(surface, 'brown', 0, 140, 320, 20)

    # Spiral staircase
    draw_pixel_rect(surface, 'dark_gray', 200, 40, 60, 100)
    for y in range(50, 130, 15):
        draw_pixel_rect(surface, 'brown', 205, y, 50, 8)
    draw_pixel_rect(surface, 'black', 200, 30, 60, 15)  # Opening above

    # Desk
    draw_pixel_rect(surface, 'brown', 40, 100, 80, 10)
    draw_pixel_rect(surface, 'brown', 50, 110, 10, 30)
    draw_pixel_rect(surface, 'brown', 100, 110, 10, 30)

    # Journal on desk
    if 'journal' not in state.inventory:
        draw_pixel_rect(surface, 'light_gray', 60, 92, 20, 12)
        draw_pixel_rect(surface, 'brown', 62, 94, 16, 8)

    # Lantern hook
    draw_pixel_rect(surface, 'dark_gray', 180, 60, 3, 20)
    if 'lantern' not in state.inventory:
        draw_pixel_rect(surface, 'yellow', 175, 75, 12, 15)
        draw_pixel_rect(surface, 'dark_gray', 178, 72, 6, 5)

    # Photos on wall
    draw_pixel_rect(surface, 'brown', 50, 50, 25, 20)
    draw_pixel_rect(surface, 'light_gray', 52, 52, 21, 16)
    draw_pixel_rect(surface, 'brown', 90, 50, 25, 20)
    draw_pixel_rect(surface, 'light_gray', 92, 52, 21, 16)

    # Door to outside
    draw_pixel_rect(surface, 'brown', 145, 100, 30, 50)
    draw_pixel_rect(surface, 'light_gray', 150, 110, 20, 35)

def draw_lighthouse_stairs(surface, state):
    """Draw the spiral staircase"""
    # Dark interior
    draw_pixel_rect(surface, 'dark_gray', 0, 0, 320, 160)

    # Curved wall effect
    draw_dithered_rect(surface, 'dark_gray', 'light_gray', 0, 0, 60, 160)
    draw_dithered_rect(surface, 'dark_gray', 'light_gray', 260, 0, 60, 160)

    # Stairs
    for i, y in enumerate(range(130, 30, -20)):
        x_offset = 30 * math.sin(i * 0.8)
        draw_pixel_rect(surface, 'brown', int(100 + x_offset), y, 80, 12)
        draw_pixel_rect(surface, 'dark_gray', int(100 + x_offset), y-3, 80, 4)

    # Railing
    draw_pixel_rect(surface, 'dark_gray', 90, 30, 5, 120)

    # Window
    draw_pixel_rect(surface, 'light_gray', 270, 60, 30, 40)
    draw_pixel_rect(surface, 'light_blue', 275, 65, 20, 30)
    draw_pixel_rect(surface, 'dark_gray', 284, 65, 2, 30)

    # Light from above
    pygame.draw.polygon(surface, EGA_COLORS['light_gray'],
                       [(160, 0), (120, 30), (200, 30)])

def draw_light_chamber(surface, state):
    """Draw the light chamber at top of lighthouse"""
    # Glass walls (view outside)
    draw_dithered_rect(surface, 'light_blue', 'blue', 0, 0, 320, 100)

    # Distant sea and ghost ships
    draw_pixel_rect(surface, 'blue', 0, 70, 320, 30)
    # Ghost ships on horizon
    for x in [30, 100, 200, 280]:
        draw_dithered_rect(surface, 'light_gray', 'light_blue', x, 60, 20, 15)

    # Floor
    draw_pixel_rect(surface, 'dark_gray', 0, 100, 320, 60)
    draw_dithered_rect(surface, 'dark_gray', 'brown', 0, 120, 320, 40)

    # Lens housing (center)
    draw_pixel_rect(surface, 'dark_gray', 130, 80, 60, 50)
    draw_pixel_rect(surface, 'brown', 135, 85, 50, 40)

    # Lens spot
    if state.flags['lens_installed']:
        draw_pixel_rect(surface, 'light_cyan', 150, 95, 20, 20)
        draw_pixel_rect(surface, 'white', 155, 100, 10, 10)
        if state.flags['lighthouse_lit']:
            # Glowing!
            draw_pixel_rect(surface, 'yellow', 145, 90, 30, 30)
            draw_pixel_rect(surface, 'white', 155, 100, 10, 10)
    else:
        draw_pixel_rect(surface, 'black', 150, 95, 20, 20)

    # Mirror brackets
    draw_pixel_rect(surface, 'dark_gray', 60, 90, 20, 25)
    draw_pixel_rect(surface, 'dark_gray', 240, 90, 20, 25)

    # Left mirror (always there)
    draw_pixel_rect(surface, 'light_cyan', 63, 93, 14, 19)

    # Right mirror (player must place)
    if state.flags['mirror_placed']:
        draw_pixel_rect(surface, 'light_cyan', 243, 93, 14, 19)
    else:
        draw_pixel_rect(surface, 'black', 243, 93, 14, 19)

    # Frame/ceiling
    draw_pixel_rect(surface, 'brown', 0, 0, 320, 10)
    draw_pixel_rect(surface, 'dark_gray', 0, 0, 10, 100)
    draw_pixel_rect(surface, 'dark_gray', 310, 0, 10, 100)

def draw_scene(surface, state):
    """Draw the current room"""
    room = state.current_room

    if room == 'beach':
        draw_beach(surface, state)
    elif room == 'cliffs':
        draw_cliffs(surface, state)
    elif room == 'cave':
        draw_cave(surface, state)
    elif room == 'path':
        draw_path(surface, state)
    elif room == 'garden':
        draw_garden(surface, state)
    elif room == 'shed':
        draw_shed(surface, state)
    elif room == 'lighthouse_exterior':
        draw_lighthouse_exterior(surface, state)
    elif room == 'lighthouse_interior':
        draw_lighthouse_interior(surface, state)
    elif room == 'lighthouse_stairs':
        draw_lighthouse_stairs(surface, state)
    elif room == 'light_chamber':
        draw_light_chamber(surface, state)

def draw_ui(surface, state, input_text):
    """Draw the UI elements"""
    # Bottom panel
    draw_pixel_rect(surface, 'blue', 0, 160, 320, 40)
    draw_pixel_rect(surface, 'black', 2, 162, 316, 36)

    # Room name
    room_data = ROOMS[state.current_room]
    name_surface = font_small.render(room_data['name'], True, EGA_COLORS['yellow'])
    surface.blit(name_surface, (5, 163))

    # Message text (wrapped)
    if state.message:
        wrapped = textwrap.wrap(state.message, width=60)
        for i, line in enumerate(wrapped[:2]):
            text_surface = font_small.render(line, True, EGA_COLORS['light_cyan'])
            surface.blit(text_surface, (5, 175 + i * 10))

    # Input line
    input_surface = font_small.render("> " + input_text + "_", True, EGA_COLORS['white'])
    surface.blit(input_surface, (5, 195))

    # Inventory display (right side)
    inv_x = 240
    draw_pixel_rect(surface, 'dark_gray', inv_x, 0, 80, 12)
    inv_label = font_small.render("INVENTORY", True, EGA_COLORS['yellow'])
    surface.blit(inv_label, (inv_x + 10, 1))

    # Show inventory items as icons
    for i, item in enumerate(state.inventory[:6]):
        ix = inv_x + (i % 3) * 25 + 5
        iy = 15 + (i // 3) * 15
        # Draw simple item icon
        if item == 'driftwood':
            draw_pixel_rect(surface, 'brown', ix, iy, 20, 4)
        elif item == 'rope':
            draw_pixel_rect(surface, 'yellow', ix, iy, 15, 3)
        elif item == 'crystal_lens':
            draw_pixel_rect(surface, 'light_cyan', ix, iy, 10, 10)
        elif item == 'ancient_coin':
            draw_pixel_rect(surface, 'yellow', ix, iy, 8, 8)
        elif item == 'matches':
            draw_pixel_rect(surface, 'red', ix, iy, 12, 4)
        elif item == 'apple':
            draw_pixel_rect(surface, 'red', ix, iy, 8, 8)
        elif item == 'oil_can':
            draw_pixel_rect(surface, 'dark_gray', ix, iy, 10, 12)
        elif item == 'small_key':
            draw_pixel_rect(surface, 'yellow', ix, iy, 12, 5)
        elif item == 'lantern':
            draw_pixel_rect(surface, 'yellow', ix, iy, 10, 12)
        elif item == 'journal':
            draw_pixel_rect(surface, 'brown', ix, iy, 12, 10)
        elif item == 'mirror_shard':
            draw_pixel_rect(surface, 'light_cyan', ix, iy, 8, 12)

def parse_command(command, state):
    """Parse and execute player command"""
    command = command.lower().strip()
    words = command.split()

    if not words:
        return "What would you like to do?"

    verb = words[0]
    obj = ' '.join(words[1:]) if len(words) > 1 else ''
    obj = obj.replace('the ', '').replace('a ', '').replace('an ', '')

    room = ROOMS[state.current_room]

    # Movement commands
    if verb in ['go', 'walk', 'move', 'head', 'n', 's', 'e', 'w', 'u', 'd', 'north', 'south', 'east', 'west', 'up', 'down', 'enter']:
        direction = obj if obj else verb
        direction_map = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west', 'u': 'up', 'd': 'down'}
        direction = direction_map.get(direction, direction)

        # Special case: entering lighthouse
        if direction in ['enter', 'door', 'lighthouse'] and state.current_room == 'lighthouse_exterior':
            direction = 'north'

        # Check for special movement conditions
        if state.current_room == 'cliffs' and direction == 'north':
            if not state.flags['crab_moved']:
                return "The giant crab blocks your path, snapping its claws menacingly!"

        if state.current_room == 'lighthouse_exterior' and direction == 'north':
            if not state.flags['lighthouse_door_open']:
                return "The lighthouse door is locked. You'll need a key."

        if direction in room['exits']:
            state.current_room = room['exits'][direction]
            new_room = ROOMS[state.current_room]
            return new_room['description']
        else:
            return "You can't go that way."

    # Look command
    if verb in ['look', 'l', 'examine', 'x', 'inspect', 'read']:
        if not obj or obj in ['around', 'room']:
            return room['description']

        # Check examine dictionary
        obj_key = obj.replace(' ', '_')
        if obj_key in room.get('examine', {}):
            if obj_key == 'journal':
                state.flags['read_journal'] = True
            return room['examine'][obj_key]

        # Check inventory items
        for item in state.inventory:
            if obj in item.replace('_', ' '):
                item_descs = {
                    'driftwood': 'A sturdy piece of driftwood. Could be useful for something.',
                    'rope': 'Strong rope, about 20 feet long.',
                    'crystal_lens': 'A beautiful crystal lens, perfectly shaped to focus light.',
                    'ancient_coin': 'An old coin showing a lighthouse. Perhaps an offering?',
                    'matches': 'A box of matches, still dry.',
                    'apple': 'A small but fresh apple. It looks delicious.',
                    'oil_can': 'A can of lamp oil.',
                    'small_key': 'A brass key with a lighthouse emblem.',
                    'lantern': 'A brass lantern. ' + ('It glows with a warm flame.' if state.flags['lantern_lit'] else 'It needs oil and a flame.'),
                    'journal': 'Thomas Blackwood\'s journal. It tells of his eternal vigil for his lost wife Eliza.',
                    'mirror_shard': 'A perfectly polished mirror shard from the well.'
                }
                return item_descs.get(item, f"It's a {item.replace('_', ' ')}.")

        return f"You don't see any {obj} here."

    # Get/take command
    if verb in ['get', 'take', 'grab', 'pick', 'pickup']:
        obj_key = obj.replace(' ', '_')

        # Special: dig in sand
        if obj in ['sand', 'mirror', 'shard', 'mirror shard'] and state.current_room == 'beach':
            if 'mirror_shard' not in state.inventory:
                state.add_to_inventory('mirror_shard')
                return "You dig in the sand near the waterline and find a perfectly polished mirror shard!"

        # Check room items
        if obj_key in room.get('items', []):
            state.add_to_inventory(obj_key)
            room['items'].remove(obj_key)
            return f"You take the {obj.replace('_', ' ')}."

        # Item aliases
        aliases = {
            'lens': 'crystal_lens',
            'crystal': 'crystal_lens',
            'coin': 'ancient_coin',
            'key': 'small_key',
            'oil': 'oil_can',
            'can': 'oil_can',
            'wood': 'driftwood',
            'book': 'journal'
        }
        if obj in aliases and aliases[obj] in room.get('items', []):
            item = aliases[obj]
            state.add_to_inventory(item)
            room['items'].remove(item)
            return f"You take the {item.replace('_', ' ')}."

        return f"You can't take that."

    # Use/put command
    if verb in ['use', 'put', 'place', 'insert', 'install', 'combine', 'give', 'throw', 'feed']:
        # Use key on door
        if ('key' in obj or 'small_key' in obj) and state.current_room == 'lighthouse_exterior':
            if state.has_item('small_key'):
                state.flags['lighthouse_door_open'] = True
                return "The key fits! The heavy door swings open with a groan, revealing the dark interior."
            return "You don't have a key."

        # Use oil on lantern
        if 'oil' in obj and 'lantern' in obj:
            if state.has_item('oil_can') and state.has_item('lantern'):
                state.remove_item('oil_can')
                return "You fill the lantern with oil. Now you just need to light it."
            return "You need both the oil can and the lantern."

        if 'oil' in obj and state.has_item('oil_can') and state.has_item('lantern'):
            state.remove_item('oil_can')
            return "You fill the lantern with oil. Now you just need to light it."

        # Light lantern with matches
        if ('match' in obj or 'light' in verb) and ('lantern' in obj or state.has_item('lantern')):
            if state.has_item('matches') and state.has_item('lantern'):
                if not state.flags.get('lantern_has_oil', False) and state.has_item('oil_can'):
                    return "The lantern needs oil first."
                state.flags['lantern_lit'] = True
                state.remove_item('matches')
                return "You strike a match and light the lantern. It casts a warm, steady glow."
            return "You need matches and a lantern."

        # Throw driftwood/apple at crab
        if state.current_room == 'cliffs' and ('crab' in obj or obj in ['driftwood', 'wood', 'apple']):
            if state.has_item('apple'):
                state.remove_item('apple')
                state.flags['crab_moved'] = True
                return "You toss the apple away from the cave. The crab scuttles after it eagerly! The path to the cave is now clear."
            if state.has_item('driftwood'):
                return "You wave the driftwood at the crab but it just snaps at it angrily. Maybe food would work better?"
            return "You have nothing to distract the crab with."

        # Place lens in housing
        if ('lens' in obj or 'crystal' in obj) and state.current_room == 'light_chamber':
            if state.has_item('crystal_lens'):
                state.remove_item('crystal_lens')
                state.flags['lens_installed'] = True
                return "You carefully place the crystal lens into the housing. It fits perfectly! Now if only there was light to focus..."
            return "You don't have the crystal lens."

        # Place mirror in bracket
        if ('mirror' in obj or 'shard' in obj) and state.current_room == 'light_chamber':
            if state.has_item('mirror_shard'):
                state.remove_item('mirror_shard')
                state.flags['mirror_placed'] = True
                return "You place the mirror shard in the empty bracket. It fits perfectly, as if it was always meant to be here."
            return "You don't have the mirror shard."

        # Light the lighthouse
        if 'lantern' in obj and state.current_room == 'light_chamber':
            if state.has_item('lantern') and state.flags['lantern_lit']:
                if state.flags['lens_installed'] and state.flags['mirror_placed']:
                    state.flags['lighthouse_lit'] = True
                    return light_the_lighthouse(state)
                elif not state.flags['lens_installed']:
                    return "You hold the lantern up but without a lens, the light won't focus properly."
                else:
                    return "You hold the lantern up but one of the mirror brackets is empty. The light won't reach far enough."
            return "You need a lit lantern to light the lighthouse."

        # Give coin to ghost
        if ('coin' in obj or 'ghost' in obj) and state.current_room == 'path':
            if state.has_item('ancient_coin'):
                state.remove_item('ancient_coin')
                state.flags['talked_to_ghost'] = True
                return "You offer the ancient coin to the ghost. She takes it, and for a moment becomes solid. 'Thank you, kind sailor. My husband Thomas kept this lighthouse for me. Find the lens in the sea cave, the mirror where you woke, and reunite us.' She fades, but you feel her gratitude."
            return "You have nothing to give."

        return f"You can't use that here."

    # Talk command
    if verb in ['talk', 'speak', 'ask', 'greet', 'hello', 'hi']:
        if state.current_room == 'path':
            if not state.flags['talked_to_ghost']:
                return "The ghost turns to you, her eyes filled with centuries of sorrow. 'Please... help us. My husband waits above, the light waits to shine again. Do you have an offering?'"
            else:
                return "'Light reunites what darkness divides. Please, restore the lighthouse.'"
        return "There's no one here to talk to."

    # Ring bell
    if verb in ['ring', 'pull'] and state.current_room == 'lighthouse_exterior':
        if 'bell' in obj or 'rope' in obj:
            state.flags['bell_rung'] = True
            return "You pull the rope and the bell rings out across the island. BONG... BONG... BONG... The sound echoes hauntingly. For a moment, you hear distant voices carried on the wind."

    # Dig command
    if verb in ['dig', 'search']:
        if state.current_room == 'beach' and 'mirror_shard' not in state.inventory:
            state.add_to_inventory('mirror_shard')
            return "You dig in the sand near the waterline and discover a perfectly polished mirror shard, glinting in the dim light!"
        return "You find nothing of interest."

    # Inventory
    if verb in ['inventory', 'inv', 'i']:
        if state.inventory:
            items = [i.replace('_', ' ') for i in state.inventory]
            return "You are carrying: " + ', '.join(items)
        return "You aren't carrying anything."

    # Help
    if verb in ['help', 'h', '?']:
        return "Commands: LOOK, GET, USE, TALK, GO (N/S/E/W/UP/DOWN), INVENTORY. Type LOOK <object> to examine things."

    # Quit
    if verb in ['quit', 'exit', 'q']:
        pygame.quit()
        sys.exit()

    return f"I don't understand '{command}'. Type HELP for commands."

def light_the_lighthouse(state):
    """The winning sequence"""
    state.flags['game_won'] = True
    return """You hold up the lit lantern before the crystal lens. The light catches, refracts,
and BLAZES outward through the mirrors! The entire chamber fills with brilliant golden light!

Through the windows, you see the ghost ships on the horizon begin to glow. One by one,
spirits rise from the waves - sailors lost for centuries, finally free.

The ghost of Eliza appears beside you, radiant now, no longer sad. 'Thank you,' she whispers.
Another spirit joins her - Thomas, the lighthouse keeper, reunited with his love at last.

'The light will guide you home now,' they say together, and fade into the brilliant beams.

As dawn breaks, you see a ship on the horizon - a REAL ship, drawn by the lighthouse beam.
You are saved.

*** CONGRATULATIONS! YOU HAVE COMPLETED THE LIGHTHOUSE OF FORGOTTEN SOULS! ***

(Press ESC to exit)"""

def draw_win_screen(surface, state):
    """Draw the winning screen"""
    # Golden sky
    draw_dithered_rect(surface, 'yellow', 'brown', 0, 0, 320, 80)

    # Sea with golden light
    draw_dithered_rect(surface, 'blue', 'yellow', 0, 80, 320, 40)

    # Lighthouse with brilliant light
    draw_pixel_rect(surface, 'white', 130, 20, 60, 80)
    draw_pixel_rect(surface, 'red', 130, 20, 60, 15)
    draw_pixel_rect(surface, 'yellow', 140, 5, 40, 20)

    # Light beams everywhere
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        end_x = 160 + int(math.cos(rad) * 160)
        end_y = 15 + int(math.sin(rad) * 80)
        pygame.draw.line(surface, EGA_COLORS['yellow'], (160, 15), (end_x, max(0, end_y)), 2)

    # Rising spirits
    for i, x in enumerate([50, 100, 150, 200, 250]):
        y = 70 - i * 5
        draw_dithered_rect(surface, 'white', 'light_cyan', x, y, 15, 25)

    # Ship approaching
    draw_pixel_rect(surface, 'brown', 270, 90, 30, 15)
    draw_pixel_rect(surface, 'white', 280, 70, 5, 20)
    pygame.draw.polygon(surface, EGA_COLORS['white'], [(280, 70), (300, 80), (280, 85)])

    # Ground
    draw_pixel_rect(surface, 'green', 0, 120, 320, 40)

def main():
    """Main game loop"""
    clock = pygame.time.Clock()
    state = GameState()
    input_text = ""

    # Title screen
    showing_title = True
    title_timer = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if showing_title:
                    showing_title = False
                    continue

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_RETURN:
                    if input_text:
                        state.message = parse_command(input_text, state)
                        input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode and len(input_text) < 50:
                    input_text += event.unicode

        # Clear game surface
        game_surface.fill(EGA_COLORS['black'])

        if showing_title:
            # Draw title screen
            draw_pixel_rect(game_surface, 'black', 0, 0, 320, 200)

            # Lighthouse silhouette
            draw_pixel_rect(game_surface, 'dark_gray', 135, 60, 50, 100)
            draw_pixel_rect(game_surface, 'yellow', 150, 50, 20, 15)

            # Light beams
            title_timer += 1
            if title_timer % 30 < 15:
                pygame.draw.line(game_surface, EGA_COLORS['yellow'], (160, 55), (80, 20), 2)
                pygame.draw.line(game_surface, EGA_COLORS['yellow'], (160, 55), (240, 20), 2)

            # Title text
            title1 = font_medium.render("THE LIGHTHOUSE", True, EGA_COLORS['light_cyan'])
            title2 = font_medium.render("OF FORGOTTEN SOULS", True, EGA_COLORS['light_cyan'])
            game_surface.blit(title1, (95, 10))
            game_surface.blit(title2, (80, 28))

            # Instructions
            inst1 = font_small.render("A Sierra-Style Adventure", True, EGA_COLORS['white'])
            inst2 = font_small.render("Press any key to begin...", True, EGA_COLORS['yellow'])
            game_surface.blit(inst1, (95, 170))
            game_surface.blit(inst2, (95, 185))

            # Stars
            for i in range(30):
                x = (i * 37 + title_timer) % 320
                y = (i * 13) % 50
                game_surface.set_at((x, y), EGA_COLORS['white'])

        elif state.flags['game_won']:
            draw_win_screen(game_surface, state)
            draw_ui(game_surface, state, input_text)
        else:
            # Draw current scene
            draw_scene(game_surface, state)
            draw_ui(game_surface, state, input_text)

        # Scale up to screen
        scaled = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  THE LIGHTHOUSE OF FORGOTTEN SOULS")
    print("  A Sierra-Style Adventure Game")
    print("="*60)
    print("\nYou are Morgan, a shipwrecked sailor on a mysterious island.")
    print("Restore the lighthouse and free the trapped souls!")
    print("\nCommands: LOOK, GET, USE, TALK, GO (N/S/E/W), INVENTORY")
    print("Type LOOK <object> to examine things closely.")
    print("="*60 + "\n")
    main()
