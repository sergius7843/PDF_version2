# core/group_handler
from PyQt6.QtGui import QColor
import random  # Para colores random iniciales

class GroupHandler:
    def __init__(self):
        self.groups = []  # Lista de dicts: {'name': str, 'paths': [str], 'color': QColor}
        self.colors = [QColor("lightblue"), QColor("lightgreen"), QColor("lightyellow"), QColor("lightpink"), QColor("lightgray")]

    def create_group(self, paths: list[str], default_name: str = "Grupo"):
        if not paths:
            return None
        color = random.choice(self.colors)  # Asignar color random
        group = {'name': default_name, 'paths': paths, 'color': color}
        self.groups.append(group)
        return group

    def remove_group(self, group):
        if group in self.groups:
            self.groups.remove(group)

    def get_group_name(self, group):
        return group['name']

    def set_group_name(self, group, new_name: str):
        if new_name:
            group['name'] = new_name

    def get_group_paths(self, group):
        return group['paths']