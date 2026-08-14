class GateArray:
    def __init__(self, width=80, height=25):
        self.width = width
        self.height = height
        self.screen = [[' ' for _ in range(width)] for _ in range(height)]
        self.colors = [['#FFFFFF' for _ in range(width)] for _ in range(height)]
        self.mode = 1
        self.cursor_x = 0
        self.cursor_y = 0
        
    def reset(self):
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [['#FFFFFF' for _ in range(self.width)] for _ in range(self.height)]
        self.cursor_x = 0
        self.cursor_y = 0
        
    def set_char(self, x, y, char, color='#FFFFFF'):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.screen[y][x] = char
            self.colors[y][x] = color
            
    def get_screen_buffer(self):
        return {
            'chars': self.screen,
            'colors': self.colors,
            'cursor_x': self.cursor_x,
            'cursor_y': self.cursor_y,
            'mode': self.mode,
            'width': self.width,
            'height': self.height,
        }