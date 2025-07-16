# Frox Game

A frog endless runner game where you collect fruit, avoid bombs, and rack up your score! Supports both keyboard and Arduino-based controls.

## Controls
The longer you hold each down the furthur the frog will jump.

- **Keyboard** (default):

  - Left Leg: `A`
  - Right Leg: `D`
  - Jump (both legs): `Space`

- **Arduino** (optional):
  - Use your custom Arduino controller to trigger left, right, or both legs for jumping.

Install dependencies:

```bash
pip install pygame pyserial
```

or install pygame and pyserial separately

## Running the Game

```bash
python main.py
```

- To use Arduino, set `arduino = True` at the top of `main.py` and ensure your Arduino is connected and sending serial data.

## Credits

Made by Karla Sahin and Dingning Cao for Jiaji Li and Mingming Li
