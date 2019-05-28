"""
	if keys[pygame.K_UP]:
		car.increase_speed()

	if keys[pygame.K_DOWN]:
		car.decrease_speed()

	if keys[pygame.K_LEFT]:
		if car.speed > 0:
			car.turn_angle = (5 * car.speed / 15) + 3
			car.angle = (car.angle + car.turn_angle) % 360 
			car.rotate(car.angle)

	if keys[pygame.K_RIGHT]:
		if car.speed > 0:
			car.turn_angle = (5 * car.speed / 15) + 3
			car.angle = car.angle - car.turn_angle if car.angle - car.turn_angle > 0 else 360 - (car.turn_angle - car.angle)
			car.rotate(car.angle)
"""