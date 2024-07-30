import pygame
from pygame.locals import *
from constants import *


class ScrollableList:
    def __init__(self, pos, size, font=None, font_color=(0, 0, 0), bg_color=(255, 255, 255)):
        self.rect = pygame.Rect(pos, size)
        self.font = pygame.font.Font(font, 60)
        self.font_color = font_color
        self.bg_color = bg_color
        self.items = []
        self.scroll_offset = 0
        self.max_visible_items = self.rect.height // self.font.get_height()
        
        self.scrollbar_width = 20
        self.scrollbar_color = (150, 150, 150)
        self.scrollbar_rect = pygame.Rect(self.rect.right - self.scrollbar_width, self.rect.top, 
                                          self.scrollbar_width, self.rect.height)
        self.scrollbar_dragging = False
        self.scrollbar_visible = False

    def add_item(self, item):
        self.items.append(item)
        self.update_scrollbar()

    def delete_item(self, index):
        if 0 <= index < len(self.items):
            del self.items[index]
            self.update_scrollbar()

    def delete_last_item(self):
        if len(self.items[-1]) == 2:
            del self.items[-1][1]    
        else:
            del self.items[-1]

    def edit_item(self, index, new_item):
        if 0 <= index < len(self.items):
            self.items[index] = new_item

    def clear_items(self):
        self.items = []
        self.update_scrollbar()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.scrollbar_visible and self.scrollbar_rect.collidepoint(event.pos):
                self.scrollbar_dragging = True
                self.scrollbar_drag_y = event.pos[1] - self.scrollbar_rect.y
        elif event.type == pygame.MOUSEBUTTONUP:
            self.scrollbar_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.scrollbar_dragging:
                new_y = event.pos[1] - self.scrollbar_drag_y
                self.scrollbar_rect.y = max(self.rect.top, min(new_y, self.rect.bottom - self.scrollbar_rect.height))
                self.scroll_offset = int((self.scrollbar_rect.y - self.rect.top) / (self.rect.height - self.scrollbar_rect.height) * (len(self.items) - self.max_visible_items))
                self.scroll_offset = max(0, min(self.scroll_offset, len(self.items) - self.max_visible_items))

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        
        visible_items = self.items[self.scroll_offset:self.scroll_offset + self.max_visible_items]
        column_width = self.rect.width // 2

        for i, item in enumerate(visible_items):
            for j, element in enumerate(item):
                text_surface = self.font.render(str(element), True, self.font_color)
                x = self.rect.x + j * column_width
                y = self.rect.y + i * self.font.get_height()
                screen.blit(text_surface, (x, y))

        if self.scrollbar_visible:
            self.update_scrollbar()
            pygame.draw.rect(screen, self.scrollbar_color, self.scrollbar_rect)

    def update_scrollbar(self):
        total_items = max(len(self.items), 1)
        if total_items > self.max_visible_items:
            self.scrollbar_visible = True
            self.scrollbar_rect.height = self.rect.height * (self.max_visible_items / total_items)
            self.scrollbar_rect.y = self.rect.top + (self.scroll_offset / (total_items - self.max_visible_items)) * (self.rect.height - self.scrollbar_rect.height)
        else:
            self.scrollbar_visible = False

    def update(self):
        pass



class TextBox:
    def __init__(self, center, width, height, callback=None, font_size=30, font_color=(0, 0, 0), bg_color=(255, 255, 255), border_color=(0, 0, 0), 
                 border_width=2, border_radius=5, padding=BUTTON_PADDING, shadow_color=BUTTON_SHADOW_COLOR):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = center
        self.font = pygame.font.Font(None, font_size)
        self.font_color = font_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.padding = padding
        self.text = ""
        self.text_surface = self.font.render(self.text, True, self.font_color)
        self.active = False
        self.cursor_visible = True
        self.cursor_counter = 0
        self.cursor_position = len(self.text)
        self.backspace_held = False
        self.backspace_counter = 0
        self.start_deleting = False
        self.shadow_color = shadow_color
        self.callback = callback

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        if event.type == KEYDOWN:
            if self.active:
                if event.key == K_RETURN:
                    if self.callback:
                        self.callback(self.text)

                elif event.key == K_BACKSPACE:
                    self.backspace_held = True
                    self.backspace_counter = 0
                    if self.cursor_position > 0:
                        self.text = self.text[:self.cursor_position-1] + self.text[self.cursor_position:]
                        self.cursor_position -= 1
                else:
                    self.text = self.text[:self.cursor_position] + event.unicode + self.text[self.cursor_position:]
                    self.cursor_position += 1
                self.text_surface = self.font.render(self.text, True, self.font_color)
        if event.type == KEYUP:
            if event.key == K_BACKSPACE:
                self.backspace_held = False
                self.start_deleting = False

    def update(self):
        self.cursor_counter += 1
        if self.cursor_counter >= FRAME_RATE // 2:
            self.cursor_visible = not self.cursor_visible
            self.cursor_counter = 0
        if self.backspace_held:
            self.backspace_counter += 1
            if self.backspace_counter >= FRAME_RATE // 3:
                self.start_deleting = True
            if self.start_deleting and self.backspace_counter >= FRAME_RATE // 30: 
                if self.start_deleting:
                    if self.cursor_position > 0:
                        self.text = self.text[:self.cursor_position-1] + self.text[self.cursor_position:]
                        self.cursor_position -= 1
                    self.backspace_counter = 0
            self.text_surface = self.font.render(self.text, True, self.font_color)

    def draw(self, screen):
        shadow_rect = self.rect.move(3, 3)
        pygame.draw.rect(screen, self.shadow_color, shadow_rect, border_radius=self.border_radius)

        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width, border_radius=self.border_radius)

        text_rect = self.text_surface.get_rect(center=(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2))
        screen.blit(self.text_surface, text_rect.topleft)

        if self.active and self.cursor_visible:
            cursor_y = text_rect.y
            cursor_x = text_rect.x + self.font.size(self.text[:self.cursor_position])[0]
            pygame.draw.line(screen, self.font_color, (cursor_x, cursor_y), (cursor_x, cursor_y + self.font.get_height()), 2)
    
    def set_text(self, text):
        self.text = text
        self.text_surface = self.font.render(self.text, True, self.font_color)


class Text:
    def __init__(self, text, position, font_name=FONT, font_size=FONT_SIZE, text_color=(0, 0, 0), bg_color=None, bold=False, italic=False):
        self.text = text
        self.position = position
        self.font_name = font_name
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        self.bold = bold
        self.italic = italic
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.bold, self.italic)
        self.rendered_text = self.font.render(self.text, True, self.text_color, self.bg_color)
        self.text_rect = self.rendered_text.get_rect(center=self.position)

    def draw(self, screen):
        screen.blit(self.rendered_text, self.text_rect)

    def update(self):
        pass

    def handle_event(self, event):
        pass

    def set_text(self, new_text):
        self.text = new_text
        self.rendered_text = self.font.render(self.text, True, self.text_color, self.bg_color)
        self.text_rect = self.rendered_text.get_rect(center=self.position)

    def set_position(self, new_position):
        self.position = new_position
        self.text_rect.center = self.position

    def set_font(self, font_name, font_size, bold=False, italic=False):
        self.font_name = font_name
        self.font_size = font_size
        self.bold = bold
        self.italic = italic
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.bold, self.italic)
        self.rendered_text = self.font.render(self.text, True, self.text_color, self.bg_color)
        self.text_rect = self.rendered_text.get_rect(center=self.position)

    def set_color(self, text_color, bg_color=None):
        self.text_color = text_color
        self.bg_color = bg_color
        self.rendered_text = self.font.render(self.text, True, self.text_color, self.bg_color)
        self.text_rect = self.rendered_text.get_rect(center=self.position)


class Icon:
    def __init__(self, image_path, center, size):
        if image_path:
            image = pygame.image.load(image_path).convert_alpha()
            self.image_surf = pygame.transform.scale(image, size)
        else:
            self.image_surf = pygame.Surface((0, 0))

        self.size = size
        self.rect = self.image_surf.get_rect()
        self.rect.center = center

    def draw(self, screen):
        screen.blit(self.image_surf, self.rect)

    def update(self):
        pass

    def handle_event(self, event):
        pass

    def set_icon(self, image_path):
        image = pygame.image.load(image_path).convert_alpha()
        self.image_surf = pygame.transform.scale(image, self.size)


class Button:
    def __init__(self, text, callback, center, size, 
                 idle_color=BUTTON_IDLE_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                 pressed_color=BUTTON_PRESSED_COLOR, inactive_color=BUTTON_INACTIVE_COLOR, 
                 shadow_color=BUTTON_SHADOW_COLOR, font=FONT, font_size=FONT_SIZE, 
                 font_color=FONT_COLOR, padding=BUTTON_PADDING, is_active=True):

        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = center
        self.button_rect = self.rect.move(-padding, -padding)
        self.text = text
        self.callback = callback

        self.idle_color = idle_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.inactive_color = inactive_color
        self.active_shadow_color = shadow_color

        self.font = pygame.font.Font(font, font_size)
        self.font_color = font_color

        if is_active:
            self.color = idle_color
            self.shadow_color = shadow_color
        else:
            self.color = inactive_color
            self.shadow_color = BUTTON_SHADOW_COLOR

        self.hover = False
        self.active = is_active
        self.pressed = False
        self.padding = padding

    def draw(self, screen):
        text_surface = self.font.render(self.text, True, self.font_color)
        text_rect = text_surface.get_rect(center=self.button_rect.center)

        if self.pressed:
            text_rect = text_rect.move(self.padding, self.padding)
            pygame.draw.rect(screen, self.color, self.rect, border_radius=BUTTON_BORDER_RADIUS)
        else:
            pygame.draw.rect(screen, self.shadow_color, self.rect, border_radius=BUTTON_BORDER_RADIUS)
            pygame.draw.rect(screen, self.color, self.button_rect, border_radius=BUTTON_BORDER_RADIUS)
        
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if not self.active:
            self.color = BUTTON_INACTIVE_COLOR
            self.shadow_color = BUTTON_SHADOW_COLOR
            return
        else:
            self.shadow_color = self.active_shadow_color

        if event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.pressed = True
            self.color = self.pressed_color

        elif event.type == MOUSEBUTTONUP:
            if self.pressed:
                self.pressed = False
                self.color = self.idle_color
                if self.rect.collidepoint(event.pos):
                    self.callback()

        elif event.type == MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.color = self.hover_color
            else:
                self.color = self.idle_color

    def update(self):
        pass

    def set_active(self, active):
        self.active = active
        if not self.active:
            self.color = self.inactive_color
            self.shadow_color = BUTTON_SHADOW_COLOR
        else:
            self.color = self.idle_color
            self.shadow_color = self.active_shadow_color


class IconButton:
    def __init__(self, image_path, callback, center, size, 
                 idle_color=BUTTON_IDLE_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                 pressed_color=BUTTON_PRESSED_COLOR, inactive_color=BUTTON_INACTIVE_COLOR, 
                 shadow_color=BUTTON_SHADOW_COLOR, padding=BUTTON_PADDING, is_active=True):

        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = center
        self.button_rect = self.rect.move(-padding, -padding)
        image = pygame.image.load(image_path).convert_alpha()
        self.image_surf = pygame.transform.scale(image, size)
        self.callback = callback

        self.idle_color = idle_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.inactive_color = inactive_color
        self.active_shadow_color = shadow_color

        if is_active:
            self.color = idle_color
            self.shadow_color = shadow_color
        else:
            self.color = inactive_color
            self.shadow_color = BUTTON_SHADOW_COLOR

        self.hover = False
        self.active = is_active
        self.pressed = False
        self.padding = padding

    def draw(self, screen):
        image_rect = self.image_surf.get_rect(center=self.button_rect.center)

        if self.pressed:
            image_rect = image_rect.move(self.padding, self.padding)
            pygame.draw.rect(screen, self.color, self.rect, border_radius=BUTTON_BORDER_RADIUS)
        else:
            pygame.draw.rect(screen, self.shadow_color, self.rect, border_radius=BUTTON_BORDER_RADIUS)
            pygame.draw.rect(screen, self.color, self.button_rect, border_radius=BUTTON_BORDER_RADIUS)
        
        screen.blit(self.image_surf, image_rect)

    def handle_event(self, event):
        if not self.active:
            self.color = BUTTON_INACTIVE_COLOR
            self.shadow_color = BUTTON_SHADOW_COLOR
            return
        else:
            self.shadow_color = self.active_shadow_color

        if event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.pressed = True
            self.color = self.pressed_color

        elif event.type == MOUSEBUTTONUP:
            if self.pressed:
                self.pressed = False
                self.color = self.idle_color
                if self.rect.collidepoint(event.pos):
                    self.callback()

        elif event.type == MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.color = self.hover_color
            else:
                self.color = self.idle_color

    def update(self):
        pass

    def set_active(self, active):
        self.active = active
        if not self.active:
            self.color = self.inactive_color
            self.shadow_color = BUTTON_SHADOW_COLOR
        else:
            self.color = self.idle_color
            self.shadow_color = self.active_shadow_color
