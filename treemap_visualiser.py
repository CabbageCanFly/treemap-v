"""Treemap Visualiser

=== Module Description ===
This module contains the code to run the treemap visualisation program.
It is responsible for initializing an instance of AbstractTree (using a
concrete subclass, of course), rendering it to the user using pygame,
and detecting user events like mouse clicks and key presses and responding
to them.
"""
import pygame
from tree_data import FileSystemTree
from population import PopulationTree


# Screen dimensions and coordinates
ORIGIN = (0, 0)
WIDTH = 1024
HEIGHT = 768

FONT_HEIGHT = 30                       # The height of the text display.
TREEMAP_HEIGHT = HEIGHT - FONT_HEIGHT  # The height of the treemap display.

# Font to use for the treemap program.
FONT_FAMILY = 'Consolas'


def run_visualisation(tree):
    """Display an interactive graphical display of the given tree's treemap.

    @type tree: AbstractTree
    @rtype: None
    """
    # Setup pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Render the initial display of the static treemap.
    render_display(screen, tree, '')

    # Start an event loop to respond to events.
    event_loop(screen, tree)


def render_display(screen, tree, text):
    """Render a treemap and text display to the given screen.

    Use the constants TREEMAP_HEIGHT and FONT_HEIGHT to divide the
    screen vertically into the treemap and text comments.

    @type screen: pygame.Surface
    @type tree: AbstractTree
    @type text: str
        The text to render.
    @rtype: None
    """
    # First, clear the screen
    pygame.draw.rect(screen, pygame.color.THECOLORS['black'],
                     (0, 0, WIDTH, HEIGHT))
    treemap = tree.generate_treemap((0, 0, WIDTH, TREEMAP_HEIGHT))

    for rect in treemap:
        screen.fill(rect[1], rect[0])

    _render_text(screen, text)

    # This must be called *after* all other pygame functions have run.
    pygame.display.flip()


def _render_text(screen, text):
    """Render text at the bottom of the display.

    @type screen: pygame.Surface
    @type text: str
    @rtype: None
    """
    # The font we want to use
    font = pygame.font.SysFont(FONT_FAMILY, FONT_HEIGHT - 8)
    text_surface = font.render(text, 1, pygame.color.THECOLORS['white'])

    # Where to render the text_surface
    text_pos = (0, HEIGHT - FONT_HEIGHT + 4)
    screen.blit(text_surface, text_pos)


def event_loop(screen, tree):
    """Respond to events (mouse clicks, key presses) and update the display.

    Note that the event loop is an *infinite loop*: it continually waits for
    the next event, determines the event's type, and then updates the state
    of the visualisation or the tree itself, updating the display if necessary.
    This loop ends when the user closes the window.

    @type screen: pygame.Surface
    @type tree: AbstractTree
    @rtype: None
    """
    # We strongly recommend using a variable to keep track of the currently-
    # selected leaf (type AbstractTree | None).
    # But feel free to remove it, and/or add new variables, to help keep
    # track of the state of the program.
    selected_leaf = None

    while True:
        # Wait for an event
        event = pygame.event.poll()
        # Get the states of what keys are pressed;
        # useful for quick interactions with the visualiser.
        pressed = pygame.key.get_pressed()

        if event.type == pygame.QUIT:
            return
        elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            return
        # ---------------------------------
        # --- Left-click: Select a leaf ---
        # ---------------------------------
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            new_leaf = tree.leaf_at(event.pos, (0, 0, WIDTH, TREEMAP_HEIGHT))

            # Either deselect a leaf or select a new leaf
            # -- if the user clicked on an area with no rectangles,
            #    there will be no visual changes.
            if selected_leaf == new_leaf:
                selected_leaf = None
                render_display(screen, tree, '')
            elif new_leaf:
                selected_leaf = new_leaf
                render_display(screen, tree, selected_leaf.get_separator()
                               + " | Size: " + str(selected_leaf.data_size))
        # ----------------------------------
        # --- Right-click: Delete a leaf ---
        # ----------------------------------
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            new_leaf = tree.leaf_at(event.pos, (0, 0, WIDTH, TREEMAP_HEIGHT))

            # If the user clicked on an area with no rectangles,
            # there will be no visual changes.
            if selected_leaf == new_leaf and new_leaf:
                selected_leaf = None
            if new_leaf:
                new_leaf.delete()

            if selected_leaf:
                render_display(screen, tree, selected_leaf.get_separator()
                               + " | Size: " + str(selected_leaf.data_size))
            else:
                render_display(screen, tree, '')

        # -----------------------------------------
        # --- Delete key pressed: Delete a leaf ---
        # -----------------------------------------
        # This is a faster alternative to delete a leaf
        elif pressed[pygame.K_DELETE]:
            new_leaf = tree.leaf_at(pygame.mouse.get_pos(),
                                    (0, 0, WIDTH, TREEMAP_HEIGHT))

            if selected_leaf == new_leaf and new_leaf:
                selected_leaf = None
            if new_leaf:
                new_leaf.delete()

            if selected_leaf:
                render_display(screen, tree, selected_leaf.get_separator()
                               + " | Size: " + str(selected_leaf.data_size))
            else:
                render_display(screen, tree, '')

        # --------------------------------------------------------------
        # --- Up key / Down key pressed: Enlarge or shrink rectangle ---
        # --------------------------------------------------------------
        elif event.type == pygame.KEYUP:
            if selected_leaf:
                sign = 1 * (event.key == pygame.K_UP) -\
                       1 * (event.key == pygame.K_DOWN)
                change = 0.01
                selected_leaf.change_prop(change * sign)
                render_display(screen, tree, selected_leaf.get_separator()
                               + " | Size: " + str(selected_leaf.data_size))
        # -----------------------------------------------------
        # --- Scroll Up / Down: Enlarge or shrink rectangle ---
        # -----------------------------------------------------
        # This is a faster alternative to changing the rectangle size.
        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_leaf:
                sign = 1 * (event.button == 4) -\
                       1 * (event.button == 5)
                change = 0.01
                selected_leaf.change_prop(change * sign)
                render_display(screen, tree, selected_leaf.get_separator()
                               + " | Size: " + str(selected_leaf.data_size))


def run_treemap_file_system(path):
    """Run a treemap visualisation for the given path's file structure.

    Precondition: <path> is a valid path to a file or folder.

    @type path: str
    @rtype: None
    """
    file_tree = FileSystemTree(path)
    run_visualisation(file_tree)


def run_treemap_population():
    """Run a treemap visualisation for World Bank population data.

    @rtype: None
    """
    pop_tree = PopulationTree(True)
    run_visualisation(pop_tree)


if __name__ == '__main__':
    # Sample directory pathway:
    #   'C:\\Users\\James\\Documents\\' (Windows) or
    #   '/Users/James/Documents/' (OSX)

    # run_treemap_file_system('C:\\Users\\James\\Documents\\')
    # run_treemap_population()
    run_treemap_file_system('/Users/Jumz/d')