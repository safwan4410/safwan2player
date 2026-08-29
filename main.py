import socket
import threading
import pygame
import sys

# Screen Setup
pygame.init()
WIDTH, HEIGHT = 400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Local Network Game - SoloForge")

# Colors
WHITE = (255, 255, 255)
RED = (220, 60, 60)
BLUE = (60, 60, 220)
BLACK = (20, 20, 20)
GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)
GREEN = (50, 180, 50)

font = pygame.font.SysFont(None, 26)
font_large = pygame.font.SysFont(None, 32)

# Game Variables
player_pos = [180, 250]
other_pos = [180, 250]
is_server = False
is_client = False
in_menu = True
found_servers = []
conn = None
client_socket = None
running_net = True
server_ip_target = None

PORT = 5555

# --- Network Discovery (UDP Broadcast) ---
def start_server_discovery(my_ip):
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while running_net and is_server:
        try:
            udp_sock.sendto(b"SOLOFORGE_SERVER", ('<broadcast>', 5556))
            pygame.time.wait(1000)
        except:
            break
    udp_sock.close()

def listen_for_servers():
    global found_servers
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        udp_sock.bind(('', 5556))
    except:
        return
    udp_sock.settimeout(1.0)
    
    while running_net and in_menu and not is_client:
        try:
            data, addr = udp_sock.recvfrom(1024)
            if data == b"SOLOFORGE_SERVER":
                server_ip = addr[0]
                if server_ip not in found_servers:
                    found_servers.append(server_ip)
        except socket.timeout:
            continue
        except:
            break
    udp_sock.close()

# --- Connection & Data Transfer ---
def run_server(ip, port):
    global conn, other_pos, running_net
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(1)
    
    threading.Thread(target=start_server_discovery, args=(ip,), daemon=True).start()
    
    conn, addr = server.accept()
    
    while running_net:
        try:
            data = f"{player_pos[0]},{player_pos[1]}\n".encode()
            conn.sendall(data)
            packet = conn.recv(1024).decode()
            if packet:
                x, y = map(int, packet.strip().split(','))
                other_pos = [x, y]
        except:
            break

def run_client(server_ip, port):
    global client_socket, other_pos, running_net
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, port))
    except Exception as e:
        return

    while running_net:
        try:
            data = f"{player_pos[0]},{player_pos[1]}\n".encode()
            client_socket.sendall(data)
            packet = client_socket.recv(1024).decode()
            if packet:
                x, y = map(int, packet.strip().split(','))
                other_pos = [x, y]
        except:
            break

# --- Main Menu ---
def main_menu():
    global is_server, is_client, in_menu, server_ip_target
    
    threading.Thread(target=listen_for_servers, daemon=True).start()
    
    btn_host = pygame.Rect(60, 100, 280, 50)
    
    while in_menu:
        screen.fill(WHITE)
        
        screen.blit(font_large.render("Local Network Game", True, BLACK), (75, 40))
        
        # Create World Button
        pygame.draw.rect(screen, GREEN, btn_host, border_radius=8)
        screen.blit(font.render("Create World (Host)", True, WHITE), (100, 113))
        
        # Section Header for Available Servers
        screen.blit(font.render("Available Worlds Nearby:", True, DARK_GRAY), (60, 180))
        
        if not found_servers:
            screen.blit(font.render("Searching for hosts...", True, DARK_GRAY), (60, 220))
        
        server_rects = []
        for i, s_ip in enumerate(found_servers):
            r = pygame.Rect(60, 215 + (i * 55), 280, 45)
            pygame.draw.rect(screen, GRAY, r, border_radius=8)
            screen.blit(font.render(f"Join Server: {s_ip}", True, BLACK), (75, 227))
            server_rects.append((r, s_ip))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if btn_host.collidepoint(pos):
                    is_server = True
                    in_menu = False
                    host_ip = socket.gethostbyname(socket.gethostname())
                    threading.Thread(target=run_server, args=(host_ip, PORT), daemon=True).start()
                
                for r, s_ip in server_rects:
                    if r.collidepoint(pos):
                        is_client = True
                        server_ip_target = s_ip
                        in_menu = False
                        threading.Thread(target=run_client, args=(server_ip_target, PORT), daemon=True).start()

        pygame.display.flip()

main_menu()

# --- Touch / Mouse D-Pad Controls ---
btn_up = pygame.Rect(160, 500, 80, 50)
btn_down = pygame.Rect(160, 620, 80, 50)
btn_left = pygame.Rect(70, 560, 80, 50)
btn_right = pygame.Rect(250, 560, 80, 50)

# Main Game Loop
clock = pygame.time.Clock()
while True:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running_net = False
            pygame.quit()
            sys.exit()

    # Keyboard Controls (PC)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: player_pos[0] -= 4
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_pos[0] += 4
    if keys[pygame.K_UP] or keys[pygame.K_w]: player_pos[1] -= 4
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: player_pos[1] += 4

    # Touch / Mouse Controls (On-Screen D-Pad)
    mouse_pressed = pygame.mouse.get_pressed()
    if mouse_pressed[0]:
        m_pos = pygame.mouse.get_pos()
        if btn_up.collidepoint(m_pos): player_pos[1] -= 4
        if btn_down.collidepoint(m_pos): player_pos[1] += 4
        if btn_left.collidepoint(m_pos): player_pos[0] -= 4
        if btn_right.collidepoint(m_pos): player_pos[0] += 4

    # Screen boundaries
    player_pos[0] = max(0, min(WIDTH - 40, player_pos[0]))
    player_pos[1] = max(0, min(450 - 40, player_pos[1]))

    my_color = RED if is_server else BLUE
    other_color = BLUE if is_server else RED

    # Draw Players
    pygame.draw.rect(screen, my_color, (player_pos[0], player_pos[1], 40, 40), border_radius=6)
    pygame.draw.rect(screen, other_color, (other_pos[0], other_pos[1], 40, 40), border_radius=6)

    pygame.draw.line(screen, DARK_GRAY, (0, 480), (WIDTH, 480), 2)

    # Draw D-Pad buttons
    pygame.draw.rect(screen, GRAY, btn_up, border_radius=6)
    pygame.draw.rect(screen, GRAY, btn_down, border_radius=6)
    pygame.draw.rect(screen, GRAY, btn_left, border_radius=6)
    pygame.draw.rect(screen, GRAY, btn_right, border_radius=6)

    screen.blit(font.render("▲", True, BLACK), (192, 513))
    screen.blit(font.render("▼", True, BLACK), (192, 633))
    screen.blit(font.render("◄", True, BLACK), (100, 573))
    screen.blit(font.render("►", True, BLACK), (280, 573))

    role_text = "Role: Host (Server)" if is_server else "Role: Client (Joined)"
    screen.blit(font.render(role_text, True, BLACK), (15, 15))

    pygame.display.flip()
    clock.tick(60)