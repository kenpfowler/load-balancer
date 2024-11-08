import socket
import time
import logging
import threading


def message_handler(message):
    print(message)


# GOAL - create a load balancing Server
# What is a load balancer and what does it need to do...
# A load balancer performs the following functions:

# Distributes client requests/network load efficiently across multiple servers
# Ensures high availability and reliability by sending requests only to servers that are online
# Provides the flexibility to add or subtract servers as demand dictates
# Therefore our goals for this project are to:

# Build a load balancer that can send traffic to two or more servers.
# Health check the servers.
# Handle a server going offline (failing a health check).
# Handle a server coming back online (passing a health check).

class LoadBalancer:
    def __init__(
        self, host="localhost", port=8080, servers=[], message_handler=message_handler
    ):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.message_handler = message_handler
        self.active_connections = set()
        self.servers = servers
        self.last_server_index = len(self.servers) - 1
        self.current_server = 0
        self.max_attempts = 10

        # Set up logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def health_check(self, index):
        """mark servers as active or inactive"""
        try:
            while True:
                health_check_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host, port, active = self.servers[index]
                self.logger.info(
                    f"performing health check on the following server {host}:{port}"
                )
                health_check_socket.connect((host, port))
                message = "GET /health-check HTTP/1.1\r\n\r\n"
                health_check_socket.send(message.encode())

                response = health_check_socket.recv(1024)

                if response:
                    self.logger.info(f"the following host is up {host}:{port}")
                    self.servers[index][2] = True
                    break
                else:
                    self.logger.info(f"the following host is down {host}:{port}")
                    self.servers[index][2] = False
                    break
        except Exception as e:
            self.servers[index][2] = False
            self.logger.info(f"the following host is down {host}:{port}")
            self.logger.error(f"error performing health check: {e}")
        finally:
            health_check_socket.close()

    def monitor_assets(self):
        """periodically monitor servers for availability"""
        while True:
            for index, server in enumerate(self.servers):
                health_check_tread = threading.Thread(
                    target=self.health_check, args=[index]
                )
                health_check_tread.daemon = True
                health_check_tread.start()

            time.sleep(10)

    def get_server(self):
        """returns the next available server in the round robin"""
        
        if self.current_server > self.last_server_index:
            self.current_server = 0
        
        if self.servers[self.current_server][2] == True:
            resource = self.servers[self.current_server]
            self.current_server += 1
            return resource

        self.current_server += 1
        return self.get_server()        


    # accept messages from client while the connection exists
    def handle_client(self, client_socket, address):
        """accept and respond to client messages. close connection"""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                host, port, active = self.get_server()
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((host, port))
                self.logger.info(f"connecting to resource {host}:{port}")
                server_socket.send(data)

                response = server_socket.recv(1024)

                if not response:
                    break

                client_socket.send(response)
        except Exception as e:
            self.logger.error(f"error handling client {address}: {e}")
        finally:
            self.active_connections.remove(client_socket)
            self.logger.info(f"connection closed from {address}")

    def start(self):
        """start the server process and listen for connections"""
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            self.logger.info(f"server listening on {self.host}:{self.port}")
            monitor_thread = threading.Thread(target=self.monitor_assets)
            monitor_thread.daemon = True
            monitor_thread.start()

            while True:
                client_socket, address = self.sock.accept()
                self.logger.info(f"client {address} has connected")
                self.active_connections.add(client_socket)
                client_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            self.logger.info("gracefully shutting down server")
        except Exception as e:
            self.logger.error(f"server error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """clean up all connections and close the server."""

        for connection in self.active_connections:
            connection.close()

        self.sock.close()
        self.logger.info("server shutdown complete")
