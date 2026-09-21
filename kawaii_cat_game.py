import pygame
import random
import math
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

W, H = 800, 400
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Kawaii Cat Runner")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24, bold=True)
big_font = pygame.font.SysFont("arial", 32, bold=True)
GROUND_Y = H - 70

shield = False
cookies_collected = 0

def make_meow_sound(type="cute"):
    sr = 44100
    if type == "cute":
        dur = 0.4; n = int(sr*dur); buf = np.zeros(n, dtype=np.float32)
        for i in range(n):
            t=i/sr; freq=400+t*1500 if t<0.2 else 700-(t-0.2)*1000
            buf[i]=math.sin(2*math.pi*freq*t)*math.sin(math.pi*t/dur)*0.6
    elif type == "power":
        dur=0.5; n=int(sr*dur); buf=np.zeros(n, dtype=np.float32)
        for i in range(n):
            t=i/sr; freq=500+300*math.sin(10*t)+t*200
            buf[i]=math.sin(2*math.pi*freq*t)*(1-t/dur)*0.7
    elif type == "boing":
        dur = 0.25; n = int(sr*dur); buf = np.zeros(n, dtype=np.float32)
        for i in range(n):
            t = i/sr
            freq = 200 + 800 * math.pow(t / dur, 0.5) + 30 * math.sin(60 * t)
            buf[i] = math.sin(2 * math.pi * freq * t) * (1 - t / dur) * 0.7
    elif type == "cookie":
        dur = 0.15; n = int(sr*dur); buf = np.zeros(n, dtype=np.float32)
        for i in range(n):
            t = i/sr
            freq = 900 + 400 * t
            buf[i] = math.sin(2 * math.pi * freq * t) * (1 - t / dur) * 0.5
    else:
        dur=0.6; n=int(sr*dur); buf=np.zeros(n, dtype=np.float32)
        for i in range(n):
            t=i/sr; freq=500-t*400
            buf[i]=math.sin(2*math.pi*freq*t)*(1-t/dur)*0.8
    buf=(buf*32767).astype(np.int16)
    stereo=np.column_stack((buf,buf))
    return pygame.sndarray.make_sound(stereo)

meow_start = make_meow_sound("cute")
meow_power = make_meow_sound("power")
meow_crash = make_meow_sound("sad")
boing_sound = make_meow_sound("boing")
cookie_sound = make_meow_sound("cookie")

CATS={
    "pink": {"body":(255,182,193),"dark":(255,105,180),"blush":(255,120,150)},
    "yellow": {"body":(255,235,120),"dark":(255,200,80),"blush":(255,180,100)},
    "brown": {"body":(222,184,135),"dark":(160,120,80),"blush":(220,150,120)}
}
selected_cat=None

def draw_kawaii_cat(sx,y,colors,show_shield=True):
    body_c=colors["body"]; dark_c=colors["dark"]; blush_c=colors["blush"]
    tail_x=sx-12+math.sin(pygame.time.get_ticks()/120)*6
    pygame.draw.ellipse(screen,dark_c,(tail_x,y+12,18,10))
    pygame.draw.ellipse(screen,body_c,(sx,y,52,32))
    pygame.draw.ellipse(screen,(255,255,255),(sx+8,y+5,15,10))
    pygame.draw.circle(screen,body_c,(sx+42,y-2),24)
    pygame.draw.polygon(screen,body_c,[(sx+24,y-12),(sx+28,y-32),(sx+42,y-18)])
    pygame.draw.polygon(screen,body_c,[(sx+48,y-18),(sx+54,y-33),(sx+62,y-12)])
    pygame.draw.polygon(screen,dark_c,[(sx+30,y-15),(sx+32,y-24),(sx+38,y-15)])
    pygame.draw.polygon(screen,dark_c,[(sx+52,y-15),(sx+56,y-24),(sx+58,y-15)])
    pygame.draw.circle(screen,(255,255,255),(sx+34,y-5),9)
    pygame.draw.circle(screen,(255,255,255),(sx+54,y-5),9)
    pygame.draw.circle(screen,(40,40,40),(sx+34,y-3),5)
    pygame.draw.circle(screen,(40,40,40),(sx+54,y-3),5)
    pygame.draw.circle(screen,(255,255,255),(sx+36,y-6),2)
    pygame.draw.circle(screen,(255,255,255),(sx+56,y-6),2)
    pygame.draw.circle(screen,(255,120,150),(sx+44,y+3),2)
    pygame.draw.ellipse(screen,blush_c,(sx+18,y+2,10,6))
    pygame.draw.ellipse(screen,blush_c,(sx+60,y+2,10,6))
    if show_shield and shield:
        pygame.draw.circle(screen,(100,200,255),(sx+25,y),48,3)

def draw_kawaii_cactus(sx,h):
    pygame.draw.rect(screen,(120,200,120),(sx,GROUND_Y-h,22,h),border_radius=10)
    pygame.draw.rect(screen,(120,200,120),(sx-10,GROUND_Y-h+15,12,18),border_radius=6)
    pygame.draw.rect(screen,(120,200,120),(sx+20,GROUND_Y-h+25,12,18),border_radius=6)
    eye_y=GROUND_Y-h+15
    pygame.draw.circle(screen,(40,40,40),(sx+5,eye_y),3)
    pygame.draw.circle(screen,(40,40,40),(sx+15,eye_y),3)
    pygame.draw.ellipse(screen,(255,120,150),(sx+4,eye_y+6,4,3))
    pygame.draw.ellipse(screen,(255,120,150),(sx+14,eye_y+6,4,3))

def draw_powerup(sx, sy):
    pygame.draw.circle(screen, (100, 200, 255), (int(sx), int(sy)), 18)
    pygame.draw.circle(screen, (255, 255, 255), (int(sx), int(sy)), 14, 2)
    pygame.draw.circle(screen, (255, 230, 80), (int(sx), int(sy)), 6)

def draw_cookie(sx, sy):
    pygame.draw.circle(screen, (210, 150, 90), (int(sx), int(sy)), 14)
    pygame.draw.circle(screen, (130, 80, 40), (int(sx) - 4, int(sy) - 4), 3)
    pygame.draw.circle(screen, (130, 80, 40), (int(sx) + 4, int(sy) - 2), 3)
    pygame.draw.circle(screen, (130, 80, 40), (int(sx) - 1, int(sy) + 4), 3)

def color_select_screen():
    global selected_cat
    picking=True
    while picking:
        screen.fill((255,240,245))
        title=big_font.render("Choose Your Kawaii Cat!",True,(80,60,80))
        screen.blit(title,(W//2-title.get_width()//2,30))
        boxes=[]
        for i,(name,col) in enumerate(CATS.items()):
            x=120+i*220; y=120
            box=pygame.Rect(x-20,y-20,160,160)
            boxes.append((box,name))
            pygame.draw.rect(screen,(255,255,255),box,border_radius=20)
            pygame.draw.rect(screen,col["dark"],box,3,border_radius=20)
            draw_kawaii_cat(x,y+30,col,show_shield=False)
            screen.blit(font.render(name.upper(),True,(80,60,80)),(x+20,y+100))
            screen.blit(font.render(f"Press {i+1}",True,(150,150,150)),(x+30,y+125))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_1: selected_cat="pink"; picking=False
                if event.key==pygame.K_2: selected_cat="yellow"; picking=False
                if event.key==pygame.K_3: selected_cat="brown"; picking=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                for box,name in boxes:
                    if box.collidepoint(event.pos): selected_cat=name; picking=False
    meow_start.play()

color_select_screen()
cat_colors=CATS[selected_cat]

# GAME STATE
def reset_world():
    global next_cactus_x, cactuses, powerups, cookies, cactus_counter, cookies_collected
    next_cactus_x = 600
    cactuses = []
    powerups = []
    cookies = []
    cactus_counter = 0
    cookies_collected = 0

    for i in range(50):
        c_x = next_cactus_x
        c_h = random.randint(40, 62)
        cactuses.append([c_x, c_h])
        
        # 45% chance to spawn a stationary air cookie
        if random.random() < 0.45:
            cookies.append([c_x - random.randint(100, 200), GROUND_Y - random.randint(110, 150)])
            
        # 25% chance to spawn a shield powerup on the ground
        if random.random() < 0.25:
            powerups.append([c_x - random.randint(150, 220), GROUND_Y - 30])
            
        next_cactus_x += random.randint(350, 550)

cat_world_x=100; cat_y=GROUND_Y-50; cat_vy=0; gravity=1; jumping=False
base_speed=5; speed=base_speed; camera_x=0; score=0; high_score=0; game_over=False
shield_timer=0; start_time=pygame.time.get_ticks()
next_cactus_x=0; cactuses=[]; powerups=[]; cookies=[]; cactus_counter=0
reset_world()

running=True
while running:
    clock.tick(60)
    screen.fill((255,250,240))
    pygame.draw.rect(screen,(255,230,235),(0,GROUND_Y,W,70))
    pygame.draw.line(screen,(200,150,160),(0,GROUND_Y),(W,GROUND_Y),3)

    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        if event.type==pygame.KEYDOWN and event.key==pygame.K_SPACE:
            if not game_over and not jumping:
                cat_vy=-18; jumping=True
                boing_sound.play()
            if game_over:
                if score > high_score: high_score = score
                cat_world_x=100; cat_y=GROUND_Y-50; cat_vy=0; score=0
                game_over=False; shield=False
                start_time=pygame.time.get_ticks(); speed=base_speed
                reset_world()
                meow_start.play()

    if not game_over:
        elapsed=(pygame.time.get_ticks()-start_time)/1000
        speed=base_speed + elapsed*0.12
        if speed>14: speed=14
        cat_world_x+=speed; camera_x=cat_world_x-100
        cat_y+=cat_vy; cat_vy+=gravity
        if cat_y>=GROUND_Y-50: cat_y=GROUND_Y-50; cat_vy=0; jumping=False
        if shield and pygame.time.get_ticks()-shield_timer>5000: shield=False

    cat_screen_x=cat_world_x-camera_x

    # Render & Check Obstacles
    for c in cactuses:
        world_x,h=c; screen_x=world_x-camera_x
        if -50<screen_x<W+50:
            draw_kawaii_cactus(screen_x,h)
            if not game_over and abs(cat_world_x-world_x)<32 and cat_y+38>GROUND_Y-h:
                if shield: 
                    c[0]=-10000; shield=False
                else:
                    if score > high_score: high_score = score
                    meow_crash.play()
                    game_over=True
        if world_x < camera_x-150:
            c[0]=next_cactus_x; c[1]=random.randint(40,62)
            cactus_counter+=1; score+=1
            
            # Randomized generation with moderate spawn rates
            if random.random() < 0.45:
                cookies.append([next_cactus_x - random.randint(100, 200), GROUND_Y - random.randint(110, 150)])
            if random.random() < 0.25:
                powerups.append([next_cactus_x - random.randint(150, 220), GROUND_Y - 30])
                
            next_cactus_x+=random.randint(350,550)

    # Render & Handle Shield Power-ups
    for p in powerups[:]:
        sx = p[0] - camera_x
        if -60 < sx < W + 60:
            draw_powerup(sx, p[1])
            if not game_over and abs(cat_world_x - p[0]) < 35 and abs(cat_y - p[1]) < 45:
                shield = True
                shield_timer = pygame.time.get_ticks()
                meow_power.play()
                powerups.remove(p)
        if p[0] < camera_x - 200:
            powerups.remove(p)

    # Render & Handle Stationary Air Cookies
    for ck in cookies[:]:
        sx = ck[0] - camera_x
        if -60 < sx < W + 60:
            draw_cookie(sx, ck[1])
            if not game_over and abs(cat_world_x - ck[0]) < 35 and abs(cat_y - ck[1]) < 40:
                score += 3
                cookies_collected += 1  # Increment cookie counter
                cookie_sound.play()
                cookies.remove(ck)
        if ck[0] < camera_x - 200:
            cookies.remove(ck)

    draw_kawaii_cat(cat_screen_x,cat_y,cat_colors,show_shield=True)

    # UI Elements (Score, Cookies, High Score)
    screen.blit(font.render(f"Score: {score}",True,(80,60,80)),(20,15))
    screen.blit(font.render(f"Cookies: {cookies_collected}",True,(210,120,40)),(160,15))
    screen.blit(font.render(f"High Score: {high_score}",True,(80,60,80)),(W-200,15))

    if shield:
        s = font.render("SHIELD ACTIVE!",True,(0,120,255))
        screen.blit(s,(W//2 - s.get_width()//2, 15))

    if game_over:
        over=big_font.render("Meow... Press SPACE!",True,(200,0,80))
        screen.blit(over,(W//2-over.get_width()//2,H//2))

    pygame.display.flip()

pygame.quit()
