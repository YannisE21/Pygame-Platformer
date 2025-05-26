import csv
import pygame

levels = {
    1: "level1.csv",
    2: "level2.csv"
}

def load_map(path):
    with open(path, newline='') as file:
        return [[int(tile) for tile in row] for row in csv.reader(file)]