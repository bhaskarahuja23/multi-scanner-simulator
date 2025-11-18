# Multi-Scanner Radar/Sonar/LiDAR Simulator

A Python Tkinter application that simulates three types of sensors (Radar, Sonar, and LiDAR) detecting different objects in an ocean environment.

## Features

- **Three sensor types** with realistic detection capabilities:
  - **Radar**: Detects surface objects (Ships, Icebergs)
  - **Sonar**: Detects underwater objects (Whales, Submarines)
  - **LiDAR**: Detects close-range surface objects (Ships, Icebergs)

- **Interactive object placement**: Add Ships, Whales, Submarines, or Icebergs at random angles and distances
- **Real-time scanning**: Animated sweeping beams with fading blip detection
- **Visual feedback**: Live display showing last added object details

## Requirements

- Python 3.x
- tkinter (usually included with Python)

## Usage

Run the application:

```bash
python scanner_app.py
```

1. Select an object type (Ship, Whale, Submarine, or Iceberg)
2. Click "Add random object" to place it in the ocean
3. Watch the sensors detect objects based on their capabilities
4. Click "Clear objects" to reset

## How It Works

Each sensor has specific detection capabilities:
- Radar and LiDAR detect surface objects
- Sonar detects underwater objects
- LiDAR has a shorter range than Radar
- Objects are only detected when the sensor's sweep passes over them and the sensor is capable of detecting that object type
