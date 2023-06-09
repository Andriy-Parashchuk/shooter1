from random import randint
from time import time as timer
from pygame import *

mixer.init()
font.init()

game = True

WIDTH = 1200
HEIGHT = 700
ASPECT_RATIO = WIDTH / HEIGHT

FPS = 60

window = display.set_mode((WIDTH, HEIGHT), RESIZABLE)

display.set_caption("Shooter")
display.set_icon(image.load("images/asteroid.png"))

background = transform.scale(image.load("images/galaxy.jpg"), (WIDTH, HEIGHT))
clock = time.Clock()

virtual_surface = Surface((WIDTH, HEIGHT))
current_size = window.get_size()

mixer.music.load("sounds/space.ogg")
mixer.music.set_volume(0.1)
mixer.music.play()

shoot_sound = mixer.Sound("sounds/fire.ogg")
shoot_sound.set_volume(0.1)

font_interface = font.Font(None, 30)
font_finish = font.Font(None, 150)

lost = 0
text_lost = font_interface.render("Пропущено: " + str(lost), True, (255, 255, 255))

score = 0
text_score = font_interface.render("Рахунок: " + str(score), True, (255, 255, 255))

text_win = font_finish.render("You WIN!", True, (55, 255, 55))
text_lose = font_finish.render("You LOSE!", True, (255, 55, 55))


class GameSprite(sprite.Sprite):
    def __init__(self, sprite_image, x, y, width, height, speed):
        super().__init__()
        self.image = transform.scale(image.load(sprite_image), (width, height))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        virtual_surface.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def __init__(self, x, y):
        super().__init__("images/rocket.png", x, y, 100, 150, 10)
        self.kd = 0
        self.hp = 3
        self.clip = 10
        self.delay = 8
        self.reload = False
        self.start_reload = 0

    def update(self):
        global interface_ammo
        global ammo
        keys_pressed = key.get_pressed()

        if keys_pressed[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys_pressed[K_d] and self.rect.x < WIDTH - self.rect.width:
            self.rect.x += self.speed
        if keys_pressed[K_SPACE] and self.kd <= 0 and self.clip >= 0:
            self.fire()
            self.kd = self.delay
        else:
            self.kd -= 1

        if self.clip == 0:
            self.reload = True
            self.start_reload = timer()

        if self.reload:
            current_time = timer()
            if current_time - self.start_reload >= 1.3:
                self.reload = False
                self.clip = 10
                interface_ammo = ammo

    def fire(self):
        global interface_ammo
        shoot_sound.play()
        self.clip -= 1
        interface_ammo = interface_ammo[:-1]
        bullet = Bullet(self.rect.centerx - 10, self.rect.top)
        bullets.add(bullet)


class Ufo(GameSprite):
    def __init__(self):
        self.chance_drop_hp = 3
        self.chance_drop_fire_speed = 3
        super().__init__("images/ufo.png", randint(0, WIDTH - 140), randint(-HEIGHT, - 70), 140, 70, 2)

    def update(self):
        global lost
        global text_lost
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            lost += 1
            self.spawn()
            text_lost = font_interface.render("Пропущено: " + str(lost), True, (255, 255, 255))

    def spawn(self):
        self.rect.y = randint(-HEIGHT, - 70)
        self.rect.x = randint(0, WIDTH - 140)


class BossUfo(GameSprite):
    def __init__(self):
        self.x = randint(0, WIDTH - 200)
        self.y = -100
        self.direction = "left"
        self.speed_x = 2
        self.hp = 5
        self.chance_drop_hp = 50
        self.chance_drop_fire_speed = 25
        super().__init__("images/ufo.png", self.x, self.y, 200, 100, 1)

    def update(self):
        global lost
        global text_lost

        if self.rect.x > self.x + 100:
            self.direction = "left"
        if self.rect.x < self.x - 100:
            self.direction = "right"

        if self.direction == "left":
            self.rect.x -= self.speed_x
        else:
            self.rect.x += self.speed_x

        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            lost += 3
            text_lost = font_interface.render("Пропущено: " + str(lost), True, (255, 255, 255))
            self.rect.y = 100
            self.kill()

    def spawn(self):
        self.x = randint(0, WIDTH - 200)
        self.y = - 100
        self.rect.y = self.x
        self.rect.x = self.y


class Bullet(GameSprite):
    def __init__(self, x, y):
        super().__init__("images/bullet.png", x, y, 20, 40, 15)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < -self.rect.width:
            self.kill()


class Bonus(GameSprite):
    def __init__(self, sprite_image, x, y):
        super().__init__(sprite_image, x, y, 20, 20, 4)


class HealthBonus(Bonus):
    def __init__(self, x, y):
        super().__init__("images/heart.png", x, y)

    def update(self):
        global heart_x
        self.rect.y += self.speed
        if self.rect.colliderect(player.rect):
            heart_x = WIDTH - 70 - (60 * player.hp)
            heart = GameSprite("images/heart.png", heart_x, 20, 50, 50, 0)
            player.hp += 1
            health.append(heart)
            self.kill()

        if self.rect.y >= HEIGHT:
            self.kill()


class FireSpeedBonus(Bonus):
    def __init__(self, x, y):
        super().__init__("images/speed_up.png", x, y)

    def update(self):
        self.rect.y += self.speed
        if self.rect.colliderect(player.rect):
            player.delay -= 1
            self.kill()


class Asteroid(GameSprite):
    def __init__(self):
        self.x = randint(0, WIDTH - 140)
        self.y = randint(-HEIGHT, - 70)
        self.size = randint(30, 70)
        super().__init__("images/asteroid.png", self.x, self.y, self.size, self.size, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            self.spawn()

    def spawn(self):
        self.size = randint(30, 70)
        self.image = transform.scale(image.load("images/asteroid.png"), (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.x = randint(0, WIDTH - 140)
        self.rect.y = randint(-HEIGHT, - 70)


player = Player(550, 530)

monsters = sprite.Group()
for i in range(10):
    monster = Ufo()
    monsters.add(monster)

bosses = sprite.Group()

bullets = sprite.Group()

health = []
heart_x = WIDTH - 70
for i in range(player.hp):
    heart = GameSprite("images/heart.png", heart_x, 20, 50, 50, 0)
    health.append(heart)
    heart_x -= 60

bonuses = sprite.Group()

possible_boss_spawn = True

finish = False

asteroids = sprite.Group()
for i in range(3):
    asteroid = Asteroid()
    asteroids.add(asteroid)

ammo = []
cartridge_x = 20
for i in range(player.clip):
    cartridge = GameSprite("images/bullet.png", cartridge_x, HEIGHT - 60, 20, 40, 0)
    ammo.append(cartridge)
    cartridge_x += 20

interface_ammo = ammo

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                game = False
        if e.type == VIDEORESIZE:
            new_width = e.w
            new_height = int(new_width / ASPECT_RATIO)
            window = display.set_mode((new_width, new_height), RESIZABLE)
            current_size = window.get_size()

    if not finish:
        virtual_surface.blit(background, (0, 0))

        player.update()
        player.reset()

        bullets.update()
        bullets.draw(virtual_surface)

        monsters.update()
        monsters.draw(virtual_surface)

        bosses.update()
        bosses.draw(virtual_surface)

        bonuses.update()
        bonuses.draw(virtual_surface)

        asteroids.update()
        asteroids.draw(virtual_surface)

        crush_list_ufos = sprite.spritecollide(player, monsters, False)

        if len(crush_list_ufos) != 0 :
            for monster in crush_list_ufos:
                monster.spawn()
                player.hp -= 1
                health = health[: -1]

        crush_list_asteroids = sprite.spritecollide(player, asteroids, False)

        if len(crush_list_asteroids) != 0 :
            for asteroid in crush_list_asteroids:
                asteroid.spawn()
                player.hp -= 1
                health = health[: -1]

        crush_list_bosses = sprite.spritecollide(player, bosses, True)

        if len(crush_list_bosses) != 0:
            for monster in crush_list_bosses:
                player.hp -= 2
                health = health[: -2]

        hits_ufos_list = sprite.groupcollide(monsters, bullets, False, True)

        if len(hits_ufos_list) != 0:
            for monster in hits_ufos_list:
                score += 1
                text_score = font_interface.render("Рахунок: " + str(score), True, (255, 255, 255))
                number_chance = randint(0, 100)
                if number_chance < monster.chance_drop_hp:
                    bonus_hp = HealthBonus(monster.rect.centerx, monster.rect.centery)
                    bonuses.add(bonus_hp)
                number_chance = randint(0, 100)
                if number_chance < monster.chance_drop_fire_speed:
                    bonus_speed = FireSpeedBonus(monster.rect.centerx, monster.rect.centery)
                    bonuses.add(bonus_speed)
                monster.spawn()

        hits_bosses_list = sprite.groupcollide(bosses, bullets, False, True)

        if len(hits_bosses_list) != 0:
            for boss in hits_bosses_list:
                boss.hp -= 1
                if boss.hp <= 0:
                    score += 3
                    text_score = font_interface.render("Рахунок: " + str(score), True, (255, 255, 255))
                    number_chance = randint(0, 100)
                    if number_chance < boss.chance_drop_hp:
                        bonus_hp = HealthBonus(boss.rect.centerx, boss.rect.centery)
                        bonuses.add(bonus_hp)
                    number_chance = randint(0, 100)
                    if number_chance < boss.chance_drop_fire_speed:
                        bonus_speed = FireSpeedBonus(boss.rect.centerx, boss.rect.centery)
                        bonuses.add(bonus_speed)
                    boss.kill()
                    possible_boss_spawn = True

        sprite.groupcollide(asteroids, bullets, False, True)

        if score != 0 and score % 20 == 0 and possible_boss_spawn:
            boss = BossUfo()
            bosses.add(boss)
            possible_boss_spawn = False

        for heart in health:
            heart.reset()

        for cartridge in interface_ammo:
            cartridge.reset()

        if score >= 100:
            finish = True
            virtual_surface.blit(text_win, (380, 300))

        if lost >= 10 or player.hp <= 0:
            finish = True
            virtual_surface.blit(text_lose, (360, 300))

        virtual_surface.blit(text_lost, (30, 30))
        virtual_surface.blit(text_score, (30, 60))

    scaled_surface = transform.scale(virtual_surface, current_size)
    window.blit(scaled_surface, (0, 0))

    display.update()
    clock.tick(FPS)
