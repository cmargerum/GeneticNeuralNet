from __future__ import division
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import math
import numpy as np
import neural
import copy

##############################################################################################################
# Constants
##############################################################################################################

TILE_SIZE = 40
BROWN = (204, 102, 0)
GREEN = (51, 204, 51)
BLUE = (0, 0, 255)
ROAD = 0
GRASS = 1

mutation_rates = [0.0000001, 0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.1, 0.5, 1]
mutation_rates_index = 6

breeding_on = False

colors = {
	ROAD : BROWN,
	GRASS : GREEN
}

NUM_CARS = 100
tile_map = []
map_file = open("map.txt", 'r')
for line in map_file:
	line_split = line.strip('\n').split(" ")
	line_split = [ int(x) for x in line_split ]
	tile_map.append(line_split)

pygame.init()
pygame.display.set_caption("Generation: 0" + " - Mutation Rate: " + str(neural.NeuralNetwork.mutation_rate))
CAR_IMAGE = pygame.image.load("sprites/Audi.png").convert(32, pygame.SRCALPHA)
window_width = 1280 
window_height = 720
window = pygame.display.set_mode((window_width, window_height)) #, pygame.FULLSCREEN)
window_tile_width = window_width // TILE_SIZE
window_tile_height = window_height // TILE_SIZE

##############################################################################################################
# Classes
##############################################################################################################

class Car(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = CAR_IMAGE
		self.size = self.image.get_size()
		self.scaled_image = pygame.transform.scale(self.image, (int(self.size[0] * 0.2), int(self.size[1] * 0.2)))
		self.scaled_rec = self.scaled_image.get_rect()
		self.rect = self.scaled_image.get_rect()
		self.rect.center = (80, 450)
		self.angle = 0
		self.speed = 0.0
		self.turn_angle = 0
		self.can_move = True
		self.selected = False
		self.distance_traveled = 0

	def rotate(self, degrees):
		self.scaled_image = pygame.transform.rotate(self.image, degrees)
		rotated_rec = self.scaled_image.get_rect()
		x_scale_factor = (rotated_rec[2] / self.scaled_rec[2]) * .04
		y_scale_factor = (rotated_rec[3] / self.scaled_rec[3]) * .04
		width = int(self.size[0] * x_scale_factor)
		height = int(self.size[1] * y_scale_factor)
		self.scaled_image = pygame.transform.scale(self.scaled_image, (width, height))
		x, y = self.rect.center 
		self.rect = self.scaled_image.get_rect()
		self.rect.center = (x, y)  

	def update_position(self):
		if self.can_move: # Move this logic into a different function for car status
			self.speed -= 1 if self.speed > 1 else self.speed
			x = self.rect[0] + (self.rect[2] / 2) - (self.speed * math.sin(math.pi * self.angle / 180))
			y = self.rect[1] + (self.rect[3] / 2) - (self.speed * math.cos(math.pi * self.angle / 180))
			self.rect.center = (x, y)
			self.distance_traveled += self.speed

	def increase_speed(self):
		if self.speed < 15 and self.can_move:
			self.speed += 3

	def decrease_speed(self):
		self.speed -= 3 if self.speed > 3 else self.speed


##############################################################################################################
# Game Loop
##############################################################################################################

def get_reference_point(window, car, degree):
	car_center = car.rect.center
	
	x, y = car_center
	scale = 1
	while True:
		x = int(car_center[0] - (scale * math.sin(math.pi * ((degree + car.angle) % 360) / 180)))
		y = int(car_center[1] - (scale * math.cos(math.pi * ((degree + car.angle) % 360) / 180)))
		broken = False
		if x <= 0:
			x = 0
			broken = True

		if x >= window_width:
			x = window_width - 1
			broken = True

		if y <= 0:
			y = 0
			broken = True

		if y >= window_height:
			y = window_height - 1
			broken = True

		if broken:
			break

		if window.get_at((x, y)) == GREEN:
			break
		scale += 1

	return (x, y)

def get_reference_points(window, car):
	reference_points = []

	reference_points.append(get_reference_point(window, car, 0))
	reference_points.append(get_reference_point(window, car, 45))
	reference_points.append(get_reference_point(window, car, 90))
	reference_points.append(get_reference_point(window, car, 270))
	reference_points.append(get_reference_point(window, car, 315))

	return reference_points

def get_reference_distances(window, car):
	distances = []
	points = get_reference_points(window, car)
	car_center = car.rect.center
	for point in points:
		distances.append(math.sqrt(math.pow((point[0] - car_center[0]), 2) + math.pow((point[1] - car_center[1]), 2)))
	return distances


def draw_map(window):
	for row in range(window_tile_height):
		for col in range(window_tile_width):
			color = colors[tile_map[row][col]]
			x, y = (col * TILE_SIZE, row * TILE_SIZE)
			w, h = (TILE_SIZE, TILE_SIZE)
			pygame.draw.rect(window, color, (x, y, w, h))

def check_collision(window, car):
	car_center = car.rect.center
	car_box_top = car_center[0] - 10
	car_box_bottom = car_center[0] + 10
	car_box_left = car_center[1] - 10
	car_box_right = car_center[1] + 10

	for row in range(car_box_top, car_box_bottom):
		for col in range(car_box_left, car_box_right):
			if window.get_at((row, col)) == GREEN:
				car.can_move = False
				car.speed = 0

def draw_line(window, car, degree):
	car_center = car.rect.center
	
	x, y = car_center
	scale = 1
	while True:
		x = int(car_center[0] - (scale * math.sin(math.pi * ((degree + car.angle) % 360) / 180)))
		y = int(car_center[1] - (scale * math.cos(math.pi * ((degree + car.angle) % 360) / 180)))
		if window.get_at((x, y)) == GREEN:
			break
		scale += 1
	pygame.draw.line(window, BLUE, car_center, (x, y), 3)

	return (x, y)

def draw_lines(window, car):
	draw_line(window, car, 0)
	draw_line(window, car, 45)
	draw_line(window, car, 90)
	draw_line(window, car, 270)
	draw_line(window, car, 315)


networks = []
cars = []
auto = True
paused = False
generation = 0

def get_display_caption():
	return "Generation: " + str(generation) + " - Mutation Rate: " + str(neural.NeuralNetwork.mutation_rate)


def new_gen():
	global cars, networks, generation
	selected_cars = []
	selected_networks = []
	if auto:
		max_dist = 0
		index = 0
		for i in range(len(cars)):
			if cars[i].distance_traveled > max_dist:
				max_dist = cars[i].distance_traveled
				index = i

		selected_cars = [Car()]
		selected_networks = [networks[index]]

	else:
		for car, network in zip(cars, networks):
				if car.selected == True:
					selected_cars += [Car()]
					selected_networks += [network]

	if len(selected_networks) > 0:
		generation += 1
		pygame.display.set_caption(get_display_caption())
		new_cars = selected_cars
		new_networks = selected_networks
		if breeding_on:
			num_iter = min(len(selected_networks), (NUM_CARS - len(selected_networks)) // 4)
			for i in range(num_iter):
				i = (np.random.random_integers(0, len(selected_networks) - 1))
				j = (np.random.random_integers(0, len(selected_networks) - 1))
				net1, net2, net3, net4 = neural.NeuralNetwork.breed(selected_networks[i], selected_networks[j])
				net1.mutate()
				net2.mutate()
				net3.mutate()
				net4.mutate()
				new_cars += [Car(), Car(), Car(), Car()]
				new_networks += [net1, net2, net3, net4]

		i = 0
		while len(new_cars) < NUM_CARS:
			new_cars += [Car()]
			new_network = copy.deepcopy(new_networks[i])
			new_network.mutate()
			new_networks += [new_network]
			i = (np.random.random_integers(0, len(new_networks) - 1))

		cars = new_cars
		networks = new_networks
		selected_cars = []
		selected_networks = []

def select_car():
	mouse_loc = pygame.mouse.get_pos()
	found_car = False
	for car in cars:
		if car.selected:
			continue
		car_center = car.rect.center
		car_box_top = car_center[0] - 10
		car_box_bottom = car_center[0] + 10
		car_box_left = car_center[1] - 10
		car_box_right = car_center[1] + 10

		for row in range(car_box_top, car_box_bottom):
			if found_car:
				break
			for col in range(car_box_left, car_box_right):
				if (row, col) == mouse_loc:
					car.selected = True

					car.scaled_image = pygame.transform.rotate(car.image, car.angle)
					rotated_rec = car.scaled_image.get_rect()
					x_scale_factor = (rotated_rec[2] / car.scaled_rec[2]) * .06
					y_scale_factor = (rotated_rec[3] / car.scaled_rec[3]) * .06
					width = int(car.size[0] * x_scale_factor)
					height = int(car.size[1] * y_scale_factor)
					car.scaled_image = pygame.transform.scale(car.scaled_image, (width, height))
					x, y = car.rect.center 
					car.rect = car.scaled_image.get_rect()
					car.rect.center = (x, y)  

					window.blit(car.scaled_image, car.rect)
					pygame.display.update()
					found_car = True
					break

for i in range(NUM_CARS):
	networks.append(neural.NeuralNetwork())
	cars.append(Car())

clock = pygame.time.Clock()

running = True
first_run = True
while running:
	clock.tick(10)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.MOUSEMOTION:
			if pygame.mouse.get_pressed()[0] == 1:
				select_car()

	keys = pygame.key.get_pressed()

	if keys[pygame.K_q] and keys[pygame.K_LMETA]:
		running = False

	if keys[pygame.K_s]:
		for car, net in zip(cars, networks):
			if car.selected == True:
				net.save()

	if keys[pygame.K_a]:
		auto = False if auto else True

	if auto and not first_run:
		cars_stopped = True
		for car in cars:
			if car.speed > 0.1: 
				cars_stopped = False
		if cars_stopped:
			new_gen()

	if keys[pygame.K_p]:
		paused = False if paused else True

	if paused:
		pygame.time.delay(100)
		continue

	if keys[pygame.K_UP]:
		neural.NeuralNetwork.mutation_rate = mutation_rates[(mutation_rates_index + 1) % len(mutation_rates)]
		mutation_rates_index = (mutation_rates_index + 1) % len(mutation_rates)
		pygame.display.set_caption(get_display_caption())

	if keys[pygame.K_DOWN]:
		if mutation_rates_index != 0:
			neural.NeuralNetwork.mutation_rate = mutation_rates[mutation_rates_index - 1]
			mutation_rates_index -= 1
		else:
			neural.NeuralNetwork.mutation_rate = mutation_rates[len(mutation_rates) - 1]
			mutation_rates_index = len(mutation_rates) - 1
		pygame.display.set_caption(get_display_caption())

	if keys[pygame.K_q] and keys[pygame.K_SPACE]:
		generation = 0
		pygame.display.set_caption(get_display_caption())
		cars = []
		networks = []
		for i in range(NUM_CARS):
			networks.append(neural.NeuralNetwork())
			cars.append(Car())

	if keys[pygame.K_SPACE]:
		new_gen()

	draw_map(window)
	for car, network in zip(cars, networks):
		check_collision(window, car)
		if car.can_move:
			reference_distances = get_reference_distances(window, car)
			network_inputs = np.array([car.speed] + reference_distances)
			actions = network.run_network(network_inputs)

			if actions[0] == 1:
				car.increase_speed()
			else:
				car.decrease_speed()

			if actions[1] == 1:
				if car.speed > 0:
					car.turn_angle = (5 * car.speed / 15) + 3
					car.angle = (car.angle + car.turn_angle) % 360 
					car.rotate(car.angle)
			else:
				if car.speed > 0:
					car.turn_angle = (5 * car.speed / 15) + 3
					car.angle = car.angle - car.turn_angle if car.angle - car.turn_angle > 0 else 360 - (car.turn_angle - car.angle)
					car.rotate(car.angle)

			car.update_position()

		window.blit(car.scaled_image, car.rect)

	pygame.display.update()
	
	if first_run:
		first_run = False

pygame.quit()
