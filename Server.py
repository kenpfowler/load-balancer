import socket
import logging
import threading
from models.response import Response
from models.request import Request

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

class Server:
    def __init__(
        self, host="localhost", port=8080, message_handler=message_handler
    ):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.active_connections = set()
        self.message_handler = message_handler

        # Set up logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    # accept messages from client while the connection exists
    def handle_client(self, client_socket, address):
        """accept and respond to client messages. close connection"""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                client_socket.send(self.message_handler(data.decode()).encoded())
        except Exception as e:
            self.logger.error(f"error handling client {address}: {e}")
        finally:
            self.active_connections.remove(client_socket)
            client_socket.close()
            self.logger.info(f"connection closed from {address}")

    def start(self):
        """start the server process and listen for connections"""
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            self.logger.info(f"server listening on {self.host}:{self.port}")

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