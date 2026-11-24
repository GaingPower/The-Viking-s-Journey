def movement(player_rect, player_image, VENTANA):
    clock = pygame.time.Clock()
    running = True
    while running:
        screen.blit(player_image, player_rect)
        square.draw(VENTANA)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    player_rect.x -= 100
                elif event.key == pygame.K_d:
                    player_rect.x += 100
                elif event.key == pygame.K_w:
                    player_rect.y -= 100
                elif event.key == pygame.K_s:
                    player_rect.y += 100

        pygame.display.flip()
        clock.tick(10)
