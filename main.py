import socket
import threading
import pygame
import sys
import time


# =========================
# GAME SETUP
# =========================

pygame.init()

WIDTH = 400
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Local Network Game - SoloForge")

clock = pygame.time.Clock()


# =========================
# COLORS
# =========================

WHITE = (255, 255, 255)
RED = (220, 60, 60)
BLUE = (60, 60, 220)
BLACK = (20, 20, 20)
GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)
GREEN = (50, 180, 50)


# =========================
# FONTS
# =========================

font = pygame.font.Font(None, 26)
font_large = pygame.font.Font(None, 32)


# =========================
# GAME VARIABLES
# =========================

player_pos = [180, 250]
other_pos = [180, 250]

is_server = False
is_client = False

in_menu = True

found_servers = []

conn = None
client_socket = None

running_net = True

PORT = 5555
DISCOVERY_PORT = 5556


# =========================
# NETWORK DISCOVERY
# =========================

def start_server_discovery():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        udp_sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_BROADCAST,
            1
        )

        udp_sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        while running_net and is_server:

            udp_sock.sendto(
                b"SOLOFORGE_SERVER",
                ("255.255.255.255", DISCOVERY_PORT)
            )

            time.sleep(1)

    except Exception as e:
        print("Discovery broadcast error:", e)

    finally:
        udp_sock.close()


def listen_for_servers():

    global found_servers

    udp_sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:

        udp_sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        udp_sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_BROADCAST,
            1
        )

        udp_sock.bind((
            "",
            DISCOVERY_PORT
        ))

        udp_sock.settimeout(1)

        while running_net and in_menu:

            try:

                data, addr = udp_sock.recvfrom(1024)

                if data == b"SOLOFORGE_SERVER":

                    server_ip = addr[0]

                    if server_ip not in found_servers:
                        found_servers.append(server_ip)

                        print(
                            "Found server:",
                            server_ip
                        )

            except socket.timeout:
                continue

            except Exception as e:
                print(
                    "Discovery listener error:",
                    e
                )
                break

    finally:
        udp_sock.close()


# =========================
# SERVER
# =========================

def run_server(port):

    global conn
    global other_pos
    global running_net

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        # Listen on all network interfaces
        server.bind(("", port))

        server.listen(1)

        print("Server started on port:", port)

        # Start discovery broadcast
        threading.Thread(
            target=start_server_discovery,
            daemon=True
        ).start()

        print("Waiting for player...")

        conn, addr = server.accept()

        print(
            "Player connected:",
            addr
        )

        conn.settimeout(0.1)

        while running_net:

            try:

                # Send our player position
                message = (
                    f"{player_pos[0]},"
                    f"{player_pos[1]}\n"
                )

                conn.sendall(
                    message.encode()
                )

                try:

                    packet = conn.recv(1024)

                    if packet:

                        packet = (
                            packet
                            .decode()
                            .strip()
                        )

                        x, y = map(
                            int,
                            packet.split(",")
                        )

                        other_pos = [x, y]

                except socket.timeout:
                    pass

            except Exception as e:

                print(
                    "Server connection error:",
                    e
                )

                break

            time.sleep(0.02)

    except Exception as e:

        print(
            "Server error:",
            e
        )

    finally:

        if conn:
            try:
                conn.close()
            except:
                pass

        try:
            server.close()
        except:
            pass


# =========================
# CLIENT
# =========================

def run_client(server_ip, port):

    global client_socket
    global other_pos
    global running_net

    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        print(
            "Connecting to:",
            server_ip
        )

        client_socket.connect(
            (server_ip, port)
        )

        print(
            "Connected successfully!"
        )

        client_socket.settimeout(0.1)

        while running_net:

            try:

                # Send our player position
                message = (
                    f"{player_pos[0]},"
                    f"{player_pos[1]}\n"
                )

                client_socket.sendall(
                    message.encode()
                )

                try:

                    packet = client_socket.recv(1024)

                    if packet:

                        packet = (
                            packet
                            .decode()
                            .strip()
                        )

                        x, y = map(
                            int,
                            packet.split(",")
                        )

                        other_pos = [x, y]

                except socket.timeout:
                    pass

            except Exception as e:

                print(
                    "Client connection error:",
                    e
                )

                break

            time.sleep(0.02)

    except Exception as e:

        print(
            "Connection failed:",
            e
        )

    finally:

        if client_socket:
            try:
                client_socket.close()
            except:
                pass


# =========================
# MAIN MENU
# =========================

def main_menu():

    global is_server
    global is_client
    global in_menu

    # Start searching for servers
    threading.Thread(
        target=listen_for_servers,
        daemon=True
    ).start()

    btn_host = pygame.Rect(
        60,
        100,
        280,
        50
    )

    while in_menu:

        screen.fill(WHITE)

        # Title
        title = font_large.render(
            "Local Network Game",
            True,
            BLACK
        )

        screen.blit(
            title,
            (75, 40)
        )

        # Host button
        pygame.draw.rect(
            screen,
            GREEN,
            btn_host,
            border_radius=8
        )

        text = font.render(
            "Create World (Host)",
            True,
            WHITE
        )

        screen.blit(
            text,
            (100, 113)
        )

        # Server list title
        label = font.render(
            "Available Worlds Nearby:",
            True,
            DARK_GRAY
        )

        screen.blit(
            label,
            (60, 180)
        )

        if not found_servers:

            searching = font.render(
                "Searching for hosts...",
                True,
                DARK_GRAY
            )

            screen.blit(
                searching,
                (60, 220)
            )

        # Create server buttons
        server_rects = []

        for i, s_ip in enumerate(
            found_servers
        ):

            r = pygame.Rect(
                60,
                215 + (i * 55),
                280,
                45
            )

            pygame.draw.rect(
                screen,
                GRAY,
                r,
                border_radius=8
            )

            server_text = font.render(
                f"Join Server: {s_ip}",
                True,
                BLACK
            )

            screen.blit(
                server_text,
                (75, 227 + (i * 55))
            )

            server_rects.append(
                (r, s_ip)
            )

        # Events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                pos = pygame.mouse.get_pos()

                # Host
                if btn_host.collidepoint(pos):

                    is_server = True
                    in_menu = False

                    threading.Thread(
                        target=run_server,
                        args=(PORT,),
                        daemon=True
                    ).start()

                # Join server
                for r, s_ip in server_rects:

                    if r.collidepoint(pos):

                        is_client = True
                        in_menu = False

                        threading.Thread(
                            target=run_client,
                            args=(
                                s_ip,
                                PORT
                            ),
                            daemon=True
                        ).start()

        pygame.display.flip()

        clock.tick(60)


# =========================
# START MENU
# =========================

main_menu()


# =========================
# TOUCH CONTROLS
# =========================

btn_up = pygame.Rect(
    160,
    500,
    80,
    50
)

btn_down = pygame.Rect(
    160,
    620,
    80,
    50
)

btn_left = pygame.Rect(
    70,
    560,
    80,
    50
)

btn_right = pygame.Rect(
    250,
    560,
    80,
    50
)


# =========================
# MAIN GAME LOOP
# =========================

while True:

    screen.fill(WHITE)

    # Events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running_net = False

            pygame.quit()
            sys.exit()


    # =========================
    # KEYBOARD CONTROLS
    # =========================

    keys = pygame.key.get_pressed()

    if (
        keys[pygame.K_LEFT]
        or keys[pygame.K_a]
    ):
        player_pos[0] -= 4

    if (
        keys[pygame.K_RIGHT]
        or keys[pygame.K_d]
    ):
        player_pos[0] += 4

    if (
        keys[pygame.K_UP]
        or keys[pygame.K_w]
    ):
        player_pos[1] -= 4

    if (
        keys[pygame.K_DOWN]
        or keys[pygame.K_s]
    ):
        player_pos[1] += 4


    # =========================
    # TOUCH CONTROLS
    # =========================

    mouse_pressed = pygame.mouse.get_pressed()

    if mouse_pressed[0]:

        m_pos = pygame.mouse.get_pos()

        if btn_up.collidepoint(m_pos):
            player_pos[1] -= 4

        if btn_down.collidepoint(m_pos):
            player_pos[1] += 4

        if btn_left.collidepoint(m_pos):
            player_pos[0] -= 4

        if btn_right.collidepoint(m_pos):
            player_pos[0] += 4


    # =========================
    # SCREEN BOUNDARIES
    # =========================

    player_pos[0] = max(
        0,
        min(
            WIDTH - 40,
            player_pos[0]
        )
    )

    player_pos[1] = max(
        0,
        min(
            450 - 40,
            player_pos[1]
        )
    )


    # =========================
    # PLAYER COLORS
    # =========================

    my_color = (
        RED
        if is_server
        else BLUE
    )

    other_color = (
        BLUE
        if is_server
        else RED
    )


    # =========================
    # DRAW PLAYERS
    # =========================

    pygame.draw.rect(
        screen,
        my_color,
        (
            player_pos[0],
            player_pos[1],
            40,
            40
        ),
        border_radius=6
    )

    pygame.draw.rect(
        screen,
        other_color,
        (
            other_pos[0],
            other_pos[1],
            40,
            40
        ),
        border_radius=6
    )


    # =========================
    # DIVIDER
    # =========================

    pygame.draw.line(
        screen,
        DARK_GRAY,
        (0, 480),
        (WIDTH, 480),
        2
    )


    # =========================
    # D-PAD
    # =========================

    pygame.draw.rect(
        screen,
        GRAY,
        btn_up,
        border_radius=6
    )

    pygame.draw.rect(
        screen,
        GRAY,
        btn_down,
        border_radius=6
    )

    pygame.draw.rect(
        screen,
        GRAY,
        btn_left,
        border_radius=6
    )

    pygame.draw.rect(
        screen,
        GRAY,
        btn_right,
        border_radius=6
    )


    screen.blit(
        font.render(
            "UP",
            True,
            BLACK
        ),
        (185, 515)
    )

    screen.blit(
        font.render(
            "DOWN",
            True,
            BLACK
        ),
        (178, 635)
    )

    screen.blit(
        font.render(
            "LEFT",
            True,
            BLACK
        ),
        (90, 575)
    )

    screen.blit(
        font.render(
            "RIGHT",
            True,
            BLACK
        ),
        (265, 575)
    )


    # =========================
    # ROLE TEXT
    # =========================

    if is_server:

        role_text = (
            "Role: Host (Server)"
        )

    else:

        role_text = (
            "Role: Client (Joined)"
        )

    role_surface = font.render(
        role_text,
        True,
        BLACK
    )

    screen.blit(
        role_surface,
        (15, 15)
    )


    # =========================
    # UPDATE SCREEN
    # =========================

    pygame.display.flip()

    clock.tick(60)
