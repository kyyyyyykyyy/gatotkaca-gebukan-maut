import pygame
import sys
import os
import random
import math # Kita butuh 'math' untuk animasi denyutan

# --- 1. Inisialisasi Pygame ---
pygame.init()

# --- 2. Pengaturan Layar ---
SCREEN_WIDTH = 1000  # Lebar layar
SCREEN_HEIGHT = 600 # Tinggi layar
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GATOTKACA: GEBUKAN MAUT (Estetik Update)")

# --- 3. Warna (Disesuaikan dengan background) ---
WARNA_HITAM = (0, 0, 0)
WARNA_PUTIH = (255, 255, 255)
WARNA_ABU_GELAP = (50, 50, 50)
WARNA_MERAH = (255, 0, 0)
WARNA_HIJAU_CERAH = (0, 255, 0)

# Warna Teks Menu (Biar Estetik)
WARNA_TEKS_JUDUL = (255, 220, 150) # Krem Emas (BUAT PARTIKEL & SINAR GOA)
WARNA_TEKS_TOMBOL = (200, 200, 200) # Putih Abu
WARNA_TEKS_TOMBOL_HOVER = (255, 255, 255) # Putih Terang
WARNA_BAYANGAN_TEKS = (50, 30, 0) # Cokelat Gelap

# --- 4. Game State ---
game_state = "menu" # Awalnya di menu (SEKARANG ADA "settings" JUGA)

# --- 5. Font (Menggunakan font custom) ---
# GANTI 'font_gahar.ttf' DENGAN NAMA FILE FONT KAMU
FONT_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'font', 'font_gahar.ttf')

try:
    font_judul = pygame.font.Font(FONT_PATH, 90)
    font_tombol = pygame.font.Font(FONT_PATH, 40)
    font_skor = pygame.font.Font(FONT_PATH, 30)
    font_game_over = pygame.font.Font(FONT_PATH, 70)
except Exception as e:
    print(f"ERROR: Tidak bisa memuat font custom: {e}. Menggunakan font default.")
    font_judul = pygame.font.SysFont(None, 100)
    font_tombol = pygame.font.SysFont(None, 50)
    font_skor = pygame.font.SysFont(None, 40)
    font_game_over = pygame.font.SysFont(None, 80)


# --- 6. Path Aset Gambar ---
ASSET_PATH_IMAGE = os.path.join(os.path.dirname(__file__), 'assets', 'image')

# Fungsi untuk memuat gambar dengan error handling
def load_image(name, scale=1):
    fullname = os.path.join(ASSET_PATH_IMAGE, name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
        if scale != 1:
            size = image.get_size()
            image = pygame.transform.scale(image, (int(size[0]*scale), int(size[1]*scale)))
        return image
    except pygame.error as message:
        print(f"ERROR: Tidak bisa memuat gambar: {name}")
        print(f"Pastikan file '{name}' ada di folder '{ASSET_PATH_IMAGE}'")
        raise SystemExit(message)

# --- 7. FUNGSI DRAW TEXT DENGAN BAYANGAN ---
def draw_text_with_shadow(text, font, color, shadow_color, x, y, center=False):
    shadow_surf = font.render(text, True, shadow_color)
    shadow_rect = shadow_surf.get_rect()
    if center:
        shadow_rect.center = (x + 2, y + 2)
    else:
        shadow_rect.topleft = (x + 2, y + 2)
    screen.blit(shadow_surf, shadow_rect)
    
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surf, text_rect)
    return text_rect # Kembalikan rect untuk deteksi klik


# --- 8. Muat Semua Aset Gambar ---
try:
    # Latar Belakang
    raw_bg_menu = load_image('bg_menu.png')
    raw_bg_game = load_image('bg_game.png')
    bg_menu_img = pygame.transform.scale(raw_bg_menu, (SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_game_img = pygame.transform.scale(raw_bg_game, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Karakter & Objek
    gatotkaca_img = load_image('gatotkaca.png', scale=0.3)
    buto_ijo_img = load_image('buto_ijo.png', scale=0.3)
    goa_img = load_image('goa.png', scale=0.8) # Goa diperbesar
    petir_img = load_image('petir.png', scale=0.3)
    jimat_img = load_image('jimat.png', scale=0.2)

except SystemExit:
    pygame.quit()
    sys.exit()


# --- 9. Pengaturan Game & Variabel ---
clock = pygame.time.Clock()
FPS = 60
global_tick = 0 

# Variabel Player
player_rect = gatotkaca_img.get_rect(midbottom=(100, SCREEN_HEIGHT - 40))
player_speed = 5
player_health = 100 
MAX_HEALTH = 100

# Variabel Serangan Gatotkaca
is_attacking = False
attack_timer = 0
ATTACK_DURATION = 15
petir_rect = petir_img.get_rect()

# Variabel Musuh
musuh_list = []
MUSUH_SPAWN_INTERVAL = 90 
musuh_spawn_timer = 0
musuh_speed = 3
MUSUH_DAMAGE = 10 

# Variabel Jimat
jimat_list = [] 
jimat_speed = 3

# Skor & Win Condition (Logika 15 Musuh & 7 Jimat)
skor = 0
kill_count = 0
WIN_TARGET_KILLS = 15 
total_musuh_spawned = 0 
jimat_drop_schedule = [] 

# Variabel Partikel (BUATAN KODE)
particle_list = []

# Variabel Game Over / Winner
overlay_alpha = 0 
final_text_alpha = 0 
final_text_speed = 5 

# --- Fungsi Reset Game ---
def reset_game():
    global player_health, skor, kill_count, musuh_list, jimat_list, game_state, is_attacking
    global overlay_alpha, final_text_alpha, total_musuh_spawned, jimat_drop_schedule
    player_health = MAX_HEALTH
    skor = 0
    kill_count = 0
    musuh_list = []
    jimat_list = []
    is_attacking = False
    overlay_alpha = 0 
    final_text_alpha = 0 
    player_rect.midbottom=(100, SCREEN_HEIGHT - 40)
    
    # Reset Logika 15 Musuh & 7 Jimat
    total_musuh_spawned = 0 
    jimat_drop_schedule = [True] * 7 + [False] * (WIN_TARGET_KILLS - 7)
    random.shuffle(jimat_drop_schedule) 

    game_state = "game" 

# --- Fungsi untuk men-spawn Musuh ---
def spawn_musuh():
    y_pos_bottom = SCREEN_HEIGHT - random.randint(30, 50) 
    musuh_rect = buto_ijo_img.get_rect(midbottom=(SCREEN_WIDTH + 50, y_pos_bottom)) 
    musuh_list.append(musuh_rect)

# --- Fungsi untuk men-spawn Jimat ---
def spawn_jimat(x, y):
    jimat_rect = jimat_img.get_rect(center=(x, y))
    jimat_list.append(jimat_rect)

# --- Fungsi untuk men-spawn Partikel ---
def spawn_particle():
    p_x = random.randint(0, SCREEN_WIDTH) 
    p_y = -20 
    p_speed = random.uniform(0.5, 2.0) 
    p_radius = random.randint(1, 4) 
    particle_list.append([p_x, p_y, p_speed, p_radius])


# --- Game Loop Utama ---
running = True
while running:
    global_tick += 1 
    mouse_pos = pygame.mouse.get_pos() 

    # --- 1. Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit() 
            sys.exit() 

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "menu":
                if tombol_mulai_rect.collidepoint(event.pos):
                    reset_game() 
                if tombol_pengaturan_rect.collidepoint(event.pos):
                    game_state = "settings"
            
            elif game_state == "settings":
                if tombol_kembali_rect.collidepoint(event.pos):
                    game_state = "menu"

            elif game_state in ["game_over", "winner"]:
                game_state = "menu"

        if event.type == pygame.KEYDOWN:
            if game_state == "game":
                if event.key == pygame.K_SPACE and not is_attacking:
                    is_attacking = True
                    attack_timer = ATTACK_DURATION
                    petir_rect.midleft = (player_rect.right, player_rect.centery + 20)


    # --- 2. Game Logic (Update State) ---
    if game_state == "menu" or game_state == "settings":
        # Spawn partikel baru secara acak
        if random.randint(1, 10) == 1:
            spawn_particle()
        
        # Update posisi partikel yang ada
        for p in particle_list[:]:
            p[1] += p[2] 
            if p[1] > SCREEN_HEIGHT: 
                particle_list.remove(p)

    elif game_state == "game":
        # Gerakan Player (Gatotkaca)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_rect.x += player_speed
        
        if player_rect.left < 0: player_rect.left = 0
        if player_rect.right > SCREEN_WIDTH // 2: player_rect.right = SCREEN_WIDTH // 2 

        # Update Animasi Serangan Petir
        if is_attacking:
            attack_timer -= 1
            if attack_timer <= 0:
                is_attacking = False
        
        # Spawn Musuh (HANYA JIKA BELUM 15)
        if total_musuh_spawned < WIN_TARGET_KILLS:
            musuh_spawn_timer += 1
            if musuh_spawn_timer >= MUSUH_SPAWN_INTERVAL:
                spawn_musuh()
                total_musuh_spawned += 1 
                musuh_spawn_timer = 0
        
        # Update Posisi Musuh
        for musuh in musuh_list[:]: 
            musuh.x -= musuh_speed
            if musuh.right < 0:
                musuh_list.remove(musuh)
                continue

            # ==============================================================
            # === INI DIA FIX ANTI-ERROR-NYA, BRO! ===
            # ==============================================================
            # Deteksi Tabrakan Gatotkaca vs Musuh
            if player_rect.colliderect(musuh):
                player_health -= MUSUH_DAMAGE
                musuh_list.remove(musuh)
                if player_health <= 0:
                    player_health = 0 
                    game_state = "game_over" 
                continue # <-- KATA SAKTI ANTI-ERROR
            # ==============================================================

            # Deteksi Tabrakan Petir vs Musuh
            if is_attacking and petir_rect.colliderect(musuh):
                skor += 10 
                kill_count += 1 
                
                # Logika 7 Jimat Pasti
                if jimat_drop_schedule: 
                    will_drop = jimat_drop_schedule.pop() 
                    if will_drop:
                        spawn_jimat(musuh.centerx, musuh.centery)
                
                musuh_list.remove(musuh)
        
        # Update Posisi Jimat
        for jimat in jimat_list[:]:
            jimat.x -= jimat_speed
            if jimat.right < 0:
                jimat_list.remove(jimat)
                continue
            
            if player_rect.colliderect(jimat):
                skor += 25 
                jimat_list.remove(jimat)

        # Cek Kondisi Menang (Logika baru)
        if total_musuh_spawned >= WIN_TARGET_KILLS and len(musuh_list) == 0:
            game_state = "winner"

    elif game_state in ["game_over", "winner"]:
        if overlay_alpha < 150:
            overlay_alpha += 5
        if final_text_alpha < 255:
            final_text_alpha += final_text_speed


    # --- 3. Rendering (Menggambar ke Layar) ---
    screen.fill(WARNA_HITAM) 
    
    denyut_judul = 1.0 + (abs(math.sin(global_tick * 0.05)) * 0.05)
    denyut_tombol = 1.0 + (abs(math.sin(global_tick * 0.08)) * 0.03)

    if game_state == "menu":
        screen.blit(bg_menu_img, (0, 0)) 
        
        for p in particle_list:
            pygame.draw.circle(screen, WARNA_TEKS_JUDUL, (p[0], p[1]), p[3])
        
        # Judul Game
        judul_surf = font_judul.render("GATOTKACA", True, WARNA_TEKS_JUDUL)
        judul_scaled = pygame.transform.scale(judul_surf, (int(judul_surf.get_width() * denyut_judul), int(judul_surf.get_height() * denyut_judul)))
        judul_shadow_surf = font_judul.render("GATOTKACA", True, WARNA_BAYANGAN_TEKS)
        judul_shadow_scaled = pygame.transform.scale(judul_shadow_surf, (int(judul_surf.get_width() * denyut_judul), int(judul_surf.get_height() * denyut_judul)))
        screen.blit(judul_shadow_scaled, judul_shadow_scaled.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT * 0.3 + 3)))
        screen.blit(judul_scaled, judul_scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.3)))

        subjudul_surf = font_judul.render("GEBUKAN MAUT", True, WARNA_TEKS_JUDUL)
        subjudul_scaled = pygame.transform.scale(subjudul_surf, (int(subjudul_surf.get_width() * denyut_judul), int(subjudul_surf.get_height() * denyut_judul)))
        subjudul_shadow_surf = font_judul.render("GEBUKAN MAUT", True, WARNA_BAYANGAN_TEKS)
        subjudul_shadow_scaled = pygame.transform.scale(subjudul_shadow_surf, (int(subjudul_surf.get_width() * denyut_judul), int(subjudul_surf.get_height() * denyut_judul)))
        screen.blit(subjudul_shadow_scaled, subjudul_shadow_scaled.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT * 0.3 + 83)))
        screen.blit(subjudul_scaled, subjudul_scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.3 + 80)))

        # Tombol-tombol
        warna_mulai = WARNA_TEKS_TOMBOL_HOVER if 'tombol_mulai_rect' in locals() and tombol_mulai_rect.collidepoint(mouse_pos) else WARNA_TEKS_TOMBOL
        tombol_mulai_rect = draw_text_with_shadow("MULAI", font_tombol, warna_mulai, WARNA_BAYANGAN_TEKS, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.7, center=True)
        
        warna_pengaturan = WARNA_TEKS_TOMBOL_HOVER if 'tombol_pengaturan_rect' in locals() and tombol_pengaturan_rect.collidepoint(mouse_pos) else WARNA_TEKS_TOMBOL
        tombol_pengaturan_rect = draw_text_with_shadow("Pengaturan", font_tombol, warna_pengaturan, WARNA_BAYANGAN_TEKS, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.8, center=True)
    
    elif game_state == "settings":
        screen.blit(bg_menu_img, (0, 0)) 
        
        for p in particle_list:
            pygame.draw.circle(screen, WARNA_TEKS_JUDUL, (p[0], p[1]), p[3])
            
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        draw_text_with_shadow("PENGATURAN", font_judul, WARNA_TEKS_TOMBOL_HOVER, WARNA_BAYANGAN_TEKS, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.3, center=True)
        draw_text_with_shadow("(Default)", font_skor, WARNA_PUTIH, WARNA_BAYANGAN_TEKS, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.45, center=True)
        
        warna_kembali = WARNA_TEKS_TOMBOL_HOVER if 'tombol_kembali_rect' in locals() and tombol_kembali_rect.collidepoint(mouse_pos) else WARNA_PUTIH
        tombol_kembali_rect = draw_text_with_shadow("Kembali", font_tombol, warna_kembali, WARNA_BAYANGAN_TEKS, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.7, center=True)

    elif game_state == "game":
        screen.blit(bg_game_img, (0, 0)) 
        
        # Posisi Goa & Sinar Estetik
        goa_rect = goa_img.get_rect(bottomright=(SCREEN_WIDTH + 15, SCREEN_HEIGHT + 20))
        goa_light_alpha = 100 + (math.sin(global_tick * 0.1) * 50) 
        light_color = (255, 255, 150, goa_light_alpha) 
        light_rect = pygame.Rect(goa_rect.centerx - 100, goa_rect.centery - 60, 90, 70) 
        light_surf = pygame.Surface(light_rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(light_surf, light_color, (0, 0, light_rect.width, light_rect.height))
        screen.blit(light_surf, light_rect)
        screen.blit(goa_img, goa_rect)

        # Gambar Jimat, Musuh, Gatotkaca
        for jimat in jimat_list:
            screen.blit(jimat_img, jimat)
        for musuh in musuh_list:
            screen.blit(buto_ijo_img, musuh)
        screen.blit(gatotkaca_img, player_rect)
        if is_attacking:
            screen.blit(petir_img, petir_rect)

        # Gambar Health Bar
        health_bar_width = 200
        health_bar_height = 25
        health_bar_x = 10
        health_bar_y = 10
        pygame.draw.rect(screen, WARNA_ABU_GELAP, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        current_health_width = (player_health / MAX_HEALTH) * health_bar_width
        pygame.draw.rect(screen, WARNA_MERAH, (health_bar_x, health_bar_y, current_health_width, health_bar_height))
        
        # Teks Skor (update ke /15)
        skor_teks = f"Skor: {skor} | Kills: {kill_count}/{WIN_TARGET_KILLS}"
        skor_rect = font_skor.render(skor_teks, True, WARNA_PUTIH).get_rect(topright=(SCREEN_WIDTH - 10, 10))
        draw_text_with_shadow(skor_teks, font_skor, WARNA_PUTIH, WARNA_BAYANGAN_TEKS, skor_rect.x, skor_rect.y)

    elif game_state in ["game_over", "winner"]:
        screen.blit(bg_game_img, (0,0))
        goa_rect = goa_img.get_rect(bottomright=(SCREEN_WIDTH + 15, SCREEN_HEIGHT + 20))
        screen.blit(goa_img, goa_rect)
        screen.blit(gatotkaca_img, player_rect) 
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, overlay_alpha))
        screen.blit(overlay, (0, 0))
        
        if game_state == "game_over":
            final_text = "GAME OVER"
            final_color = WARNA_MERAH
        else: # winner
            final_text = "KAMU MENANG!"
            final_color = WARNA_HIJAU_CERAH
        
        # Teks Final
        text_surf = font_game_over.render(final_text, True, final_color)
        text_surf.set_alpha(final_text_alpha) 
        text_shadow_surf = font_game_over.render(final_text, True, WARNA_BAYANGAN_TEKS)
        text_shadow_surf.set_alpha(final_text_alpha)
        screen.blit(text_shadow_surf, text_shadow_surf.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT // 2 + 3)))
        screen.blit(text_surf, text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

        # Teks Klik untuk Menu
        menu_surf = font_tombol.render("Klik untuk ke Menu", True, WARNA_PUTIH)
        menu_surf.set_alpha(final_text_alpha)
        menu_shadow_surf = font_tombol.render("Klik untuk ke Menu", True, WARNA_BAYANGAN_TEKS)
        menu_shadow_surf.set_alpha(final_text_alpha)
        screen.blit(menu_shadow_surf, menu_shadow_surf.get_rect(center=(SCREEN_WIDTH // 2 + 2, SCREEN_HEIGHT // 2 + 82)))
        screen.blit(menu_surf, menu_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)))


    # --- 4. Update Layar ---
    pygame.display.flip()
    
    # --- 5. Atur FPS ---
    clock.tick(FPS)

pygame.quit()
sys.exit()