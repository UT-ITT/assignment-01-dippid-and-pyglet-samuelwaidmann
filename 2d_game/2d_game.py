"""2d game using pyglet and DIPPID for input.
Game code adapted from https://talstra.net/docs/templates/python/py-brake-out-game/

Run this python file to start the game. Use the DIPPID sender to control the paddle with accelerometer and gyroscope data.

How the game works:
- Move the paddle left and right by tilting the device to the left or right. The more you tilt, the faster the paddle moves.
- The ball will bounce off the paddle and the walls. Try to keep it from falling below the paddle.
- When the ball hits a brick, the brick will be destroyed and you earn points.
- The game ends when the ball falls below the paddle or all bricks are destroyed. Try to get the highest score possible!

"""

from __future__ import annotations
import pyglet
from pyglet.shapes import Rectangle
from dippid_controller import DippidTiltController

PORT = 5700


class Paddle(Rectangle):
    """Player paddle controlled by keyboard or external input."""

    def move(self, dx: float, window_width: int) -> None:
        """Move paddle horizontally within window bounds."""
        new_x = self.x + dx
        self.x = max(0, min(window_width - self.width, new_x))


class Ball(Rectangle):
    """Ball with simple velocity-based movement."""

    dx: float
    dy: float

    def update(self) -> None:
        """Move the ball according to its velocity."""
        self.x += self.dx
        self.y += self.dy


class Brick(Rectangle):
    """A brick that disappears when hit."""

    alive: bool = True

    def destroy(self) -> None:
        """Mark brick as destroyed."""
        self.alive = False
        self.delete()


class GameState:
    """Encapsulates all game objects and update logic."""

    def __init__(self, window: pyglet.window.Window) -> None:
        self.window = window
        self.batch = pyglet.graphics.Batch()

        # Paddle
        self.paddle = Paddle(
            x=window.width // 2 - 60,
            y=30,
            width=120,
            height=20,
            color=(200, 200, 200),
            batch=self.batch,
        )

        # Ball
        self.ball = Ball(
            x=window.width // 2,
            y=300,
            width=20,
            height=20,
            color=(255, 0, 0),
            batch=self.batch,
        )
        self.ball.dx = 3
        self.ball.dy = 3

        # Bricks
        self.bricks: list[Brick] = []
        self._create_bricks()

        # Score
        self.score = 0
        self.score_label = pyglet.text.Label(
            f"Score: {self.score}",
            x=10,
            y=window.height - 30,
            batch=self.batch,
        )

        self.paused = False
        self.game_over = False

        # Info text at bottom (button behaviors)
        self.info_label = pyglet.text.Label(
            "button_1 = pause/resume   |   button_2 = restart   |   button_3 = quit",
            x=window.width // 2,
            y=10,
            anchor_x="center",
            batch=self.batch,
        )

    def _create_bricks(self) -> None:
        """Create a grid of bricks."""
        for row in range(5):
            for col in range(10):
                brick = Brick(
                    x=10 + col * 77,
                    y=self.window.height - 50 - row * 30,
                    width=70,
                    height=20,
                    color=(50, 50, 255),
                    batch=self.batch,
                )
                self.bricks.append(brick)

    def toggle_pause(self) -> None:
        """Pause or resume the game."""
        if not self.game_over:
            self.paused = not self.paused

    def restart(self) -> None:
        """Restart the game from scratch."""
        self.__init__(self.window)

    def quit(self):
        """Quit the game."""
        self.window.close()
        pyglet.app.exit()

    def update(self, dt: float) -> None:
        """Update game state each frame."""
        if self.paused or self.game_over:
            return

        self.ball.update()
        self._handle_wall_collisions()
        self._handle_paddle_collision()
        self._handle_brick_collisions()

        if self.ball.y < 0:
            self.game_over = True

    def _handle_wall_collisions(self) -> None:
        """Bounce ball off window edges."""
        if self.ball.x <= 0 or self.ball.x + self.ball.width >= self.window.width:
            self.ball.dx *= -1
        if self.ball.y + self.ball.height >= self.window.height:
            self.ball.dy *= -1

    def _handle_paddle_collision(self) -> None:
        """Bounce ball off paddle."""
        if (
            self.paddle.x < self.ball.x + self.ball.width
            and self.paddle.x + self.paddle.width > self.ball.x
            and self.paddle.y < self.ball.y + self.ball.height
            and self.paddle.y + self.paddle.height > self.ball.y
        ):
            self.ball.dy *= -1

    def _handle_brick_collisions(self) -> None:
        """Destroy bricks on collision."""
        for brick in self.bricks:
            if not brick.alive:
                continue

            if (
                brick.x < self.ball.x + self.ball.width
                and brick.x + brick.width > self.ball.x
                and brick.y < self.ball.y + self.ball.height
                and brick.y + brick.height > self.ball.y
            ):
                brick.destroy()
                self.ball.dy *= -1
                self.score += 1
                self.score_label.text = f"Score: {self.score}"


def main() -> None:
    window = pyglet.window.Window(width=800, height=600, caption="Breakout Game")
    game = GameState(window)
    controller = DippidTiltController(port=5700)

    @window.event
    def on_draw() -> None:
        window.clear()
        game.batch.draw()

    def update_with_dippid(dt: float) -> None:
        # BUTTON 1: Pause / Resume
        if controller.was_pressed("button_1"):
            if game.game_over:
                pass  # ignore pause when game is over
            else:
                game.toggle_pause()

        # BUTTON 2: Restart
        if controller.was_pressed("button_2"):
            game.restart()
            return  # avoid updating old state in same frame

        # BUTTON 3: Quit
        if controller.was_pressed("button_3"):
            game.quit()
            return

        # Move paddle only when active
        if not game.paused and not game.game_over:
            dx = controller.get_paddle_dx(window.width)
            game.paddle.move(dx=dx, window_width=window.width)

        game.update(dt)

    pyglet.clock.schedule_interval(update_with_dippid, 1 / 60.0)
    pyglet.app.run()


if __name__ == "__main__":
    main()
