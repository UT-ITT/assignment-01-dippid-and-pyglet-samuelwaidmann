"""2d game using pyglet and DIPPID for input.
Code adapted from https://talstra.net/docs/templates/python/py-brake-out-game/"""

import pyglet
from pyglet.window import key
from pyglet.shapes import Rectangle

# Game window setup
window = pyglet.window.Window(width=800, height=600, caption="Breakout Game")
batch = pyglet.graphics.Batch()

# Game elements
paddle = Rectangle(
    x=window.width // 2, y=30, width=120, height=20, color=(200, 200, 200), batch=batch
)
ball = Rectangle(
    x=window.width // 2, y=400, width=20, height=20, color=(255, 0, 0), batch=batch
)
ball.dx, ball.dy = 3, 3  # ball movement speed
bricks = []
score = 0

# Score display
score_label = pyglet.text.Label(
    f"Score: {score}", x=10, y=window.height - 30, batch=batch
)

# Create bricks
for i in range(5):
    for j in range(10):
        brick = Rectangle(
            x=10 + j * 77,
            y=window.height - 50 - i * 30,
            width=70,
            height=20,
            color=(50, 50, 255),
            batch=batch,
        )
        brick.visible = True  # Add a visibility attribute
        bricks.append(brick)


# Event to handle keyboard input
@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.LEFT:
        paddle.x = max(0, paddle.x - 40)
    elif symbol == key.RIGHT:
        paddle.x = min(window.width - paddle.width, paddle.x + 40)


# Update the game state
def update(dt):
    global score

    # Move the ball
    ball.x += ball.dx
    ball.y += ball.dy

    # Check for collision with walls
    if ball.x <= 0 or ball.x + ball.width >= window.width:
        ball.dx *= -1
    if ball.y + ball.height >= window.height:
        ball.dy *= -1

    # Check for collision with the paddle
    if (
        paddle.x < ball.x + ball.width
        and paddle.x + paddle.width > ball.x
        and paddle.y < ball.y + ball.height
        and paddle.y + paddle.height > ball.y
    ):
        ball.dy *= -1

    # Check for collision with bricks
    for brick in bricks:
        if brick.visible:
            if (
                brick.x < ball.x + ball.width
                and brick.x + brick.width > ball.x
                and brick.y < ball.y + ball.height
                and brick.y + brick.height > ball.y
            ):
                brick.visible = False  # Set the brick to not visible
                ball.dy *= -1
                score += 1
                score_label.text = f"Score: {score}"

    # Check for game over
    if ball.y < 0:
        pyglet.app.exit()


# Schedule game updates
pyglet.clock.schedule_interval(update, 1 / 60.0)


# Event to draw the game window
@window.event
def on_draw():
    window.clear()
    batch.draw()


# Run the game
pyglet.app.run()
