"""2d game using pyglet and DIPPID for input.
Code adapted from https://talstra.net/docs/templates/python/py-brake-out-game/"""

from __future__ import annotations
import pyglet
from pyglet.shapes import Rectangle
from pyglet.window import key


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

    def update(self, dt: float) -> None:
        """Update game state each frame."""
        self.ball.update()
        self._handle_wall_collisions()
        self._handle_paddle_collision()
        self._handle_brick_collisions()

        if self.ball.y < 0:
            pyglet.app.exit()

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
    """Create window and run game."""
    window = pyglet.window.Window(width=800, height=600, caption="Breakout Game")
    game = GameState(window)

    @window.event
    def on_key_press(symbol: int, modifiers: int) -> None:
        if symbol == key.LEFT:
            game.paddle.move(dx=-40, window_width=window.width)
        elif symbol == key.RIGHT:
            game.paddle.move(dx=40, window_width=window.width)

    @window.event
    def on_draw() -> None:
        window.clear()
        game.batch.draw()

    pyglet.clock.schedule_interval(game.update, 1 / 60.0)
    pyglet.app.run()


if __name__ == "__main__":
    main()
