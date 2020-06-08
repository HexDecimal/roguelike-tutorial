from __future__ import annotations

import sys

import lzma
import pickle
import pickletools
import traceback
from typing import Optional

import tcod

import procgen.dungeon
from model import Model
import states.ingame


class MainMenu(states.State[None]):
    def __init__(self) -> None:
        super().__init__()
        self.model: Optional[Model] = None
        self.continue_msg = "No save file."
        try:
            with open("save.sav.xz", "rb") as f:
                self.model = pickle.loads(lzma.decompress(f.read()))
            self.continue_msg = str(self.model)
        except Exception:
            traceback.print_exc(file=sys.stderr)
            self.continue_msg = "Error loading save."

    def on_draw(self, console: tcod.console.Console) -> None:
        console.clear()
        console.print(5, 5, f"c: Continue ({self.continue_msg})")
        console.print(5, 6, "n: New Game")
        console.print(5, 7, "q: Quit")

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.K_c and self.model:
            self.start()
        elif event.sym == tcod.event.K_n:
            self.new_game()
        elif event.sym == tcod.event.K_q:
            self.cmd_quit()
        else:
            super().ev_keydown(event)

    def new_game(self) -> None:
        self.model = Model()
        self.model.active_map = procgen.dungeon.generate()
        self.model.active_map.model = self.model
        self.start()

    def start(self) -> None:
        assert self.model
        try:
            self.model.loop()
        except states.SaveAndQuit:
            # Save and return to the main menu.
            self.save()
        except SystemExit:
            # Save and exit immediately.
            self.save()
            raise
        except Exception:
            # Try to save on an error.
            self.save()
            raise
        self.continue_msg = str(self.model)

    def save(self) -> None:
        data = pickle.dumps(self.model, protocol=4)
        debug = f"Raw: {len(data)} bytes, "
        data = pickletools.optimize(data)
        debug += f"Optimized: {len(data)} bytes, "
        data = lzma.compress(data)
        debug += f"Compressed: {len(data)} bytes."
        print(debug)
        print("Game saved.")
        with open("save.sav.xz", "wb") as f:
            f.write(data)
