"""Procedural dungeon floor generator."""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field

from .enemies import boss_for_floor, enemies_for_floor


# Room types
EMPTY = "."
WALL = "#"
ENEMY = "!"
TREASURE = "?"
REST = "+"
TRAP = "^"
STAIRS = ">"
ENTRANCE = "@"
BOSS = "B"

ROOM_DESCRIPTIONS = {
    EMPTY: [
        "An empty server rack hums quietly.",
        "Stale coffee and scattered printouts.",
        "The fluorescent lights flicker overhead.",
        "Keyboard clacking echoes in the distance.",
        "A whiteboard covered in faded diagrams.",
    ],
    TRAP: [
        "The floor crackles with undefined behavior!",
        "A wild segfault appears from the shadows!",
        "You step on a deprecated API endpoint!",
        "A hidden TODO: fix this later strikes!",
    ],
    REST: [
        "A cozy break room with a working coffee machine.",
        "A quiet corner with a beanbag chair.",
        "A rubber duck meditation corner.",
    ],
    TREASURE: [
        "A dusty package.json with something shiny inside.",
        "An old deploy artifact with valuables.",
        "A forgotten stash of dev tools.",
    ],
}


@dataclass
class Room:
    x: int
    y: int
    room_type: str = EMPTY
    explored: bool = False
    enemy: dict | None = None
    loot: dict | None = None
    description: str = ""
    cleared: bool = False

    def as_dict(self) -> dict:
        return {
            "x": self.x, "y": self.y,
            "room_type": self.room_type,
            "explored": self.explored,
            "enemy": self.enemy,
            "loot": self.loot,
            "description": self.description,
            "cleared": self.cleared,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Room:
        return cls(**data)


@dataclass
class Floor:
    number: int
    width: int = 5
    height: int = 5
    rooms: list[list[Room]] = field(default_factory=list)
    player_x: int = 0
    player_y: int = 0

    def generate(self, seed: int | None = None) -> None:
        rng = random.Random(seed)
        self.rooms = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(Room(x=x, y=y))
            self.rooms.append(row)

        # Carve a path from entrance to stairs
        # Start at top-left, stairs at bottom-right area
        self.rooms[0][0].room_type = ENTRANCE
        self.rooms[0][0].explored = True
        self.player_x = 0
        self.player_y = 0

        # Place stairs
        stair_x = rng.randint(self.width - 2, self.width - 1)
        stair_y = rng.randint(self.height - 2, self.height - 1)
        self.rooms[stair_y][stair_x].room_type = STAIRS

        # Create walls (~25% of remaining cells)
        available = [
            (x, y) for y in range(self.height) for x in range(self.width)
            if (x, y) not in ((0, 0), (stair_x, stair_y))
        ]
        rng.shuffle(available)

        num_walls = int(len(available) * 0.2)
        wall_candidates = available[:num_walls]
        remaining = available[num_walls:]

        # Only place walls if they don't block the path
        for wx, wy in wall_candidates:
            self.rooms[wy][wx].room_type = WALL

        # Verify path exists, remove walls if needed
        if not self._path_exists(0, 0, stair_x, stair_y):
            # Remove walls until path exists
            for wx, wy in wall_candidates:
                self.rooms[wy][wx].room_type = EMPTY
                remaining.append((wx, wy))
                if self._path_exists(0, 0, stair_x, stair_y):
                    break

        # Place content in remaining cells
        rng.shuffle(remaining)
        open_cells = [
            (x, y) for x, y in remaining
            if self.rooms[y][x].room_type == EMPTY
        ]

        # Place boss near stairs
        boss_placed = False
        for bx, by in [(stair_x - 1, stair_y), (stair_x, stair_y - 1)]:
            if 0 <= bx < self.width and 0 <= by < self.height:
                room = self.rooms[by][bx]
                if room.room_type == EMPTY:
                    room.room_type = BOSS
                    boss = boss_for_floor(self.number)
                    room.enemy = dict(boss)
                    room.description = f"The air crackles. {boss['name']} blocks your path!"
                    boss_placed = True
                    if (bx, by) in open_cells:
                        open_cells.remove((bx, by))
                    break

        if not boss_placed and open_cells:
            bx, by = open_cells.pop(0)
            room = self.rooms[by][bx]
            room.room_type = BOSS
            boss = boss_for_floor(self.number)
            room.enemy = dict(boss)
            room.description = f"The air crackles. {boss['name']} blocks your path!"

        # Enemies (3-5 per floor)
        enemies = enemies_for_floor(self.number)
        num_enemies = min(rng.randint(3, 5), len(open_cells))
        for i in range(num_enemies):
            if not open_cells:
                break
            x, y = open_cells.pop(0)
            room = self.rooms[y][x]
            room.room_type = ENEMY
            enemy = rng.choice(enemies)
            room.enemy = dict(enemy)
            room.description = f"{enemy['name']} appears! {enemy['description']}"

        # Treasures (1-2)
        num_treasure = min(rng.randint(1, 2), len(open_cells))
        for i in range(num_treasure):
            if not open_cells:
                break
            x, y = open_cells.pop(0)
            room = self.rooms[y][x]
            room.room_type = TREASURE
            room.description = rng.choice(ROOM_DESCRIPTIONS[TREASURE])

        # Rest point (1)
        if open_cells:
            x, y = open_cells.pop(0)
            room = self.rooms[y][x]
            room.room_type = REST
            room.description = rng.choice(ROOM_DESCRIPTIONS[REST])

        # Trap (1-2)
        num_traps = min(rng.randint(1, 2), len(open_cells))
        for i in range(num_traps):
            if not open_cells:
                break
            x, y = open_cells.pop(0)
            room = self.rooms[y][x]
            room.room_type = TRAP
            room.description = rng.choice(ROOM_DESCRIPTIONS[TRAP])

        # Fill remaining with descriptions
        for y in range(self.height):
            for x in range(self.width):
                room = self.rooms[y][x]
                if room.room_type == EMPTY and not room.description:
                    room.description = rng.choice(ROOM_DESCRIPTIONS[EMPTY])

    def _path_exists(self, sx: int, sy: int, ex: int, ey: int) -> bool:
        """BFS to check if a path exists between two points."""
        visited = set()
        queue = deque([(sx, sy)])
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == (ex, ey):
                return True
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.rooms[ny][nx].room_type != WALL:
                        queue.append((nx, ny))
        return False

    def get_room(self, x: int, y: int) -> Room | None:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.rooms[y][x]
        return None

    def current_room(self) -> Room:
        return self.rooms[self.player_y][self.player_x]

    def can_move(self, dx: int, dy: int) -> bool:
        nx, ny = self.player_x + dx, self.player_y + dy
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return False
        return self.rooms[ny][nx].room_type != WALL

    def move_player(self, dx: int, dy: int) -> Room | None:
        if not self.can_move(dx, dy):
            return None
        self.player_x += dx
        self.player_y += dy
        room = self.current_room()
        room.explored = True
        # Reveal adjacent rooms
        for adx, ady in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            adj = self.get_room(self.player_x + adx, self.player_y + ady)
            if adj and adj.room_type != WALL:
                adj.explored = True
        return room

    def render_map(self) -> str:
        """Render the floor as ASCII art."""
        lines = []
        # Top border
        lines.append("  " + "┌" + "───┬" * (self.width - 1) + "───┐")

        for y in range(self.height):
            row = "  │"
            for x in range(self.width):
                room = self.rooms[y][x]
                if x == self.player_x and y == self.player_y:
                    cell = "[bold #22c55e] @ [/]"
                elif not room.explored:
                    cell = "[dim] ░ [/]"
                elif room.room_type == WALL:
                    cell = "[dim] # [/]"
                elif room.cleared or room.room_type in (EMPTY, ENTRANCE):
                    cell = "[dim] . [/]"
                elif room.room_type == ENEMY:
                    cell = "[bold #ef4444] ! [/]"
                elif room.room_type == BOSS:
                    cell = "[bold #ef4444] B [/]"
                elif room.room_type == TREASURE:
                    cell = "[bold #facc15] ? [/]"
                elif room.room_type == REST:
                    cell = "[bold #06b6d4] + [/]"
                elif room.room_type == TRAP:
                    cell = "[bold #a78bfa] ^ [/]"
                elif room.room_type == STAIRS:
                    cell = "[bold #d946ef] > [/]"
                else:
                    cell = "   "
                row += cell + "│"
            lines.append(row)

            if y < self.height - 1:
                lines.append("  " + "├" + "───┼" * (self.width - 1) + "───┤")

        lines.append("  " + "└" + "───┴" * (self.width - 1) + "───┘")
        return "\n".join(lines)

    def as_dict(self) -> dict:
        return {
            "number": self.number,
            "width": self.width,
            "height": self.height,
            "rooms": [[r.as_dict() for r in row] for row in self.rooms],
            "player_x": self.player_x,
            "player_y": self.player_y,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Floor:
        f = cls(number=data["number"], width=data["width"], height=data["height"])
        f.rooms = [[Room.from_dict(r) for r in row] for row in data["rooms"]]
        f.player_x = data["player_x"]
        f.player_y = data["player_y"]
        return f
