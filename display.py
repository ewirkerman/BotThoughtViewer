import pygame
import logging
from shapely.geometry import Point

logger = logging.getLogger("display")
logger.setLevel(logging.DEBUG)


class Display():
    def __init__(self, game_map):
        self.game_map = game_map
        game_map.display = self
        pygame.font.init()

        # It won't create any folders for you
        # It'll plug in the turn number for you when it saves it
        # Expects self.game.turn_num to have the current turn number to plug in here
        self.FILENAME_FORMAT = "stats/botthought%s.jpeg"

        # Width of the pygame window, height is proportioned to match that of the game_map
        self.displayx = 1200
        self.ratio = game_map.height / game_map.width
        self.displayy = self.displayx * self.ratio

        # Comes with a minimap while zoomed in.
        self.minimapx = self.displayx / 4
        self.minimapy = self.displayy / 4
        size = [self.displayx, int(self.displayy)]
        self.screen = pygame.display.set_mode(size)
        self.clear()

        # Fill in a ship id of yours here and it will zoom and track that ship while it's alive
        self.ship_id = 591
        focus_ship = game_map.get_me()._ships.get(self.ship_id, None)
        self.zoom = focus_ship

        # The size of the zoom in game units
        self.focus_box = 30
        if focus_ship:
            logger.debug("Found focus ship")
            self.focus = (focus_ship.x, focus_ship.y)
        else:
            # Or if you want to focus on a certain game_map spot, enter that here
            self.focus = (117.0626, 67.3018)

    def _get_screen(self):
        return self.screen

    # Space pauses, ESCAPE, control+C or closing the pygame windows kill your bot
    def check_for_input(self):
        paused = False
        entering = True
        while paused or entering:
            entering = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise Exception("Quitting via pygame")
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_ESCAPE:
                        raise Exception("Quitting via pygame")
                    elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CONTROL:
                        raise Exception("Quitting via pygame")

    def get_color(self, ent):
        if not ent.owner:
            color = (0, 0, 0)
        elif getattr(ent.owner, "color", None) is None:
            if ent.owner == self.game_map.get_me():
                color = (0, 0, 255)
            else:
                color = (255, 64 * ent.owner.id, 255 - 64 * ent.owner.id)
        else:
            color = ent.owner.color
        return color

    def show(self):
        # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
        myfont = pygame.font.SysFont("monospace", 15)
        self.check_for_input()
        for p in self.game_map.all_planets():
            color = self.get_color(p)
            self.draw_poly(Point(p.x, p.y).buffer(p.radius).exterior.coords, color=color)
            label = myfont.render(str(p.id), 1, (0, 0, 0))
            self.screen.blit(label, self._scale_point((p.x, p.y)))

        for player in self.game_map.all_players():
            for p in player.all_ships():
                color = self.get_color(p)
                self.draw_poly(Point(p.x, p.y).buffer(p.radius).exterior.coords, color=color)
                label = myfont.render(str(p.id), 1, color)
                self.screen.blit(label, self._scale_point((p.x, p.y - 3)))

        if self.zoom:
            pygame.draw.line(self.screen, (0, 0, 0), (0, self.minimapy), (self.minimapx, self.minimapy), 1)
            pygame.draw.line(self.screen, (0, 0, 0), (self.minimapx, 0), (self.minimapx, self.minimapy), 1)

        pygame.display.flip()

        pygame.image.save(self.screen, self.FILENAME_FORMAT % self.game_map.turn_num)
        self.check_for_input()

    def clear(self):
        self.screen.fill((255, 255, 255))

    def _scale_point(self, tup):
        x, y = tup
        if not self.zoom:
            scale = self.displayx / self.game_map.width
            return x * scale, y * scale
        else:
            low_x = self.focus[0] - self.focus_box
            low_y = self.focus[1] - self.focus_box * self.ratio
            scale = self.displayx / (2 * self.focus_box)
            return (x - low_x) * scale, (y - low_y) * scale

    def _scale_mini(self, tup):
        x, y = tup
        scale = self.minimapx / self.game_map.width
        return x * scale, y * scale

    def draw_line(self, start, end, color=(0, 0, 0), width=1, scale_func=None):
        if scale_func is None:
            scale_func = self._scale_point
        pygame.draw.line(self.screen, color, scale_func(start), scale_func(end), width)
        if self.zoom and scale_func != self._scale_mini:
            self.draw_line(start, end, color, width, self._scale_mini)

    def draw_poly(self, point_list, color=(0, 0, 0), width=1, scale_func=None):
        if scale_func is None:
            scale_func = self._scale_point
        points = []
        for point in point_list:
            points.append(scale_func(point))
        pygame.draw.polygon(self.screen, color, points, width)
        if self.zoom and scale_func != self._scale_mini:
            self.draw_poly(point_list, color, width, self._scale_mini)

    def draw_point(self, point, color=(0, 0, 0), size=.5, width=0, scale_func=None):
        if scale_func is None:
            scale_func = self._scale_point
        p = scale_func(point)
        x, y = p
        p = Point(x, y)
        self.draw_poly(p.buffer(size).exterior.coords, color, width)
        if self.zoom and scale_func != self._scale_mini:
            self.draw_point(point, color, size, width, self._scale_mini)
