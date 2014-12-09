"""
p - PAUS
hiireklikk - tulistamine
ASDW - liikumine

Autorid: Kaspar Kliimask, Madis Kariler ehehheheh
"""
import pygame, sys, random, math, time, os

from timer import Timer
from object_functions import *
from blokk import Blokk
from mees import Mees
from enemy import Enemy
from variables import *


class Game:
    def __init__(self, WIDTH, HEIGHT):
        """
        peaklass
        """
        global levelTime

        pygame.init()

        self.width = WIDTH
        self.height = HEIGHT
        self.screen = pygame.display.set_mode((self.width,self.height))



        self.background = pygame.transform.scale((pygame.image.load("spacev1.png").convert()), (1024,768))
        self.bg_imgRect = self.background.get_rect()



        #pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
        #pygame.mixer.music.load('madis.mp3') # <--------------------------------------------------------- SIIN TAUSTAMUSS 
        #pygame.mixer.music.play(-1)  # mitu korda m'ngib

        """
        kiirus - bloki kiirus
        maxw - maksimaalne laius
        maxh - maksimaaline pikkus
        lykkab - mitu pixlit lykkab eemale kokkuporkel
        dmg - mitu dmg teeb lykkamisega
        """
        self.blokityyp = {
            "tavaline" : {
                "maxKiirus" : 0.2, # bloki maksimaalne kiirus
                "w" : 50, # laius
                "h" : 50, # pikkus
                "lykkab" : 0, # lykkamistugevus
                "dmg" : 0, # dmg kokkuporkel
                "color" : (250, 100, 50)
                #"image" : "blokk1.png"
            },
            "lykkaja" : {
                "maxKiirus" : 0.5,
                "w" : 20,
                "h" : 70,
                "lykkab" : 200,
                "dmg" : 2,
                "color" : (50,40,10)
                #"image" : "blokk1.png"
            }


        }
        self.enemytype = {
            "tavaline" : {
                "elusi" : 1,
                "w": 15,
                "h": 15,
                "color" : (255,0,255),
                "speed" : 0.1,
                "dmg" : 1
            },
            "tulistaja" : {
                "elusi" : 2,
                "w" : 20,
                "h" : 20,
                "color" : (255,255,0),
                "speed" : 0.05,
                "dmg" : 2,
                "weapon" : 1,
                "delay" : 1
            }
        }

        self.blokid = []
        self.pahad = []

        self.font=pygame.font.Font(None,30)

        self.level = 1

        self.levelTimer = Timer(levelTime)

        self.run = True
        self.mouseHolding = False

    def update_logic(self):

        self.mees.update_logic() # uuendab meest

        if(self.mouseHolding): # kui hiirt hoitakse all->automaatne tulistamine
            self.mees.automatic()

        for blokk in self.blokid:

            blokk.update_logic() # uuendame bloki liikumist

            self.mees.check_collision(blokk) # vaatame kas blokk porkab kokku mehega

            for enemy in self.pahad:
                enemy.check_collision(blokk)

        self.check_bullets() # uuendab v2lja lastud kuulidega seotud loogikat

        for enemy in game.pahad:
            enemy.attack(self.mees) # lape

            if(collision(enemy.rect, self.mees.rect)): # kui paha puutub peameest
                if(self.mees.getRekt(enemy.dmg)):
                    # mang labi
                    pass
                self.pahad.remove(enemy) # paha ohverdas kahjuks end :(


    def update_display(self): # uuendab koike mida naidatakse

        self.screen.blit(self.background, self.bg_imgRect)
        self.mees.show(game.screen) # peavend
        
        for blokk in self.blokid: # joonistame koik blokid
            blokk.show(self.screen)
            
        for enemy in self.pahad: # joonistame koik pahad
            enemy.show(self.screen)

        # muu lape
        #pygame.draw.rect(self.screen, (0,0,0), (0,700,640,10)) # porand
        scoretext=self.font.render("Score:"+str(self.level), 1,(0,255,255))
        self.screen.blit(scoretext, (200, 500))
        pygame.display.flip()
        
    def Level(self):
        if(self.levelTimer.end == True):
            self.levelTimer.reset()
            self.next_level()
            self.del_bloks()
            self.del_enemies()
            self.create_bloks(self.level*3)
            self.create_enemies(self.level*10)

    def next_level(self):
        self.level += 1 # uuendame levelit
        time.sleep(1)
        self.mees.relvad[self.mees.relv]["kokku"] += 20
        
    def create_bloks(self,count): # loob uusi blokke
        for i in range(count):
            if(random.randint(1,3) > 1): # yks kolmele et tuleb ull blokk
                temp = Blokk(self.blokityyp["tavaline"])
            else:
                temp = Blokk(self.blokityyp["lykkaja"])

            self.blokid.append(temp)

    def create_enemies(self,count): # loob uusi vastaseid
        for i in range(count):
            if(random.randint(1,5) > 1): # 20% et tulistaja
                temp = Enemy(self.enemytype["tavaline"])
            else:
                temp = Enemy(self.enemytype["tulistaja"])
            self.pahad.append(temp)

    def del_bloks(self):
        self.blokid = []

    def del_enemies(self):
        self.pahad = []

    def check_bullets(self): #
        for bullet in self.mees.bullets: # vaatame millega kuulid kokku porkavad :

            if not(rect_in_map(bullet.rect)): # kustutame kuuli kui see poel enam mapi piires.wd
                if(bullet in self.mees.bullets): # mingi lamp
                    self.mees.bullets.remove(bullet)
                    continue # kuul eemaldatud, ehk votame jargmise ette

            for blokk in self.blokid: # blokiga?
                if(collision(bullet.rect, blokk.rect)):
                    if(bullet in self.mees.bullets):
                        self.mees.bullets.remove(bullet) # kui jah siis kustutame kuuli.
                    break

            for enemy in self.pahad: # pahade poistega ?
                if(collision(bullet.rect, enemy.rect)):
                    if (enemy.getRekt(bullet.dmg)):
                        self.pahad.remove(enemy)
                    if(bullet in self.mees.bullets): # mingi lamp
                        self.mees.bullets.remove(bullet)

        for enemy in self.pahad:

            if(enemy.shooter):

                for bullet in enemy.bullets:
                    if not(rect_in_map(bullet.rect)): # kui kuul mapist valjas
                        if(bullet in enemy.bullets):
                            enemy.bullets.remove(bullet)
                            continue

                    for blokk in self.blokid: # blokiga?
                        if(collision(bullet.rect, blokk.rect)):
                            if(bullet in enemy.bullets):
                                enemy.bullets.remove(bullet) # kui jah siis kustutame kuuli.
                                break

                    if(collision(bullet.rect,self.mees.rect)):
                        self.mees.getRekt(bullet.dmg)
                        enemy.bullets.remove(bullet) # kui jah siis kustutame kuuli.






game = Game(SCREEN_WIDTH, SCREEN_HEIGHT) # peamaang
game.mees = Mees() # peavend

""" level 1 """
game.create_bloks(10) # viis vastast
game.create_enemies(35) # kaks vastast, viisakas
"""         """


while game.run == True: # main loop
    game.levelTimer.update()
    #EVENT
    for evt in pygame.event.get(): # koik eventid
        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_p:
                game.levelTimer.pauseChange()
            elif evt.key == pygame.K_1:
                game.mees.switchWeapon("handgun")
            elif evt.key == pygame.K_2:
                game.mees.switchWeapon("pump")
            elif evt.key == pygame.K_3:
                game.mees.switchWeapon("machinegun")
            elif evt.key == pygame.K_4:
                game.mees.switchWeapon("")
            elif evt.key == pygame.K_5:
                game.mees.switchWeapon("")
            elif evt.key == pygame.K_6:
                game.mees.drinkPotion("defense")
            elif evt.key == pygame.K_7:
                game.mees.drinkPotion("speed")
        elif evt.type == pygame.QUIT: # kasutaja soovib lahkuda
            game.run = False
        elif evt.type == pygame.MOUSEBUTTONDOWN:
            if(game.levelTimer.paused == -1):
                game.mees.shoot((game.mees.rect.x,game.mees.rect.y),pygame.mouse.get_pos(),pygame.mouse.get_pressed())
                game.mouseHolding = True
        elif evt.type == pygame.MOUSEBUTTONUP:
            if(game.levelTimer.paused == -1):
                game.mouseHolding = False
        
    if(game.levelTimer.paused == 1):
        continue
    keys = pygame.key.get_pressed()
    if(keys[pygame.K_a]):
        game.mees.rect.x -= game.mees.speed
    if(keys[pygame.K_d]):
        game.mees.rect.x += game.mees.speed
    if(keys[pygame.K_w]):
        game.mees.rect.y -= game.mees.speed
    if(keys[pygame.K_s]):
        game.mees.rect.y += game.mees.speed

            
    #LOGIC
    
    game.update_logic()
    
    game.Level()
        
    #DISPLAY
        
    game.update_display()
           
pygame.quit()

