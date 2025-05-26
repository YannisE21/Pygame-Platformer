import csv
import pygame

levels = {
    1: "./assets/levels/level1.csv",
    2: "./assets/levels/level2.csv"
}

def load_map(path):
    with open(path, newline='') as file:
        return [[int(tile) for tile in row] for row in csv.reader(file)]