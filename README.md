# GeneticNeuralNet

This project was inspired by a youtube video I found (https://www.youtube.com/watch?v=wL7tSgUpy8w). It aims to accomplish the same thing as the video. I wrote all of my code from scratch and didn't use anything else provided from the video besides the assest for the car.

The base game is written with pygame, and the map is hand crafted with tile blocks of size 40x40 pixels. For every iteration of the game loop, the neural network takes in the car's speed and distances to the walls at 0, 45, 90, 270, and 315 degree angles (from the direction the car is facing). There is one layer of 5 hidden nodes, and two output nodes. The output nodes are accelerate or brake, and turn left or turn right. 

With the current implementation, 100 cars are initially created with random weighs and biases. This is generation 0. The car that travels the furthest distance out of all cars in generation 0 is then picked to be the parent of generation 1. The parent and 99 more cars are spawned that have slight, random changes to the parent, and this process is repeated indefinitely. 
