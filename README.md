# Coding challenge: Load Balancer

The challenge here is to build a load balancer. Thanks to [Coding Challenges](https://codingchallenges.fyi/challenges/challenge-load-balancer) for the inspiration.

This load balancer distributes incoming requests to servers using a [round robin](https://www.vmware.com/topics/round-robin-load-balancing) scheduling algorithm.

# Getting Started

## Requirements

- installation of python (3.12.3^)

## Steps

### 1. Setup your resource servers

The load balancer is configured to check if the servers it's coordinating are up by periodically sending the following http request to each server:

```
GET /health-check HTTP/1.1\r\n\r\n"
```

Your server will need to respond to the `/health-check` route in order for the load balancer to recognize it as being online.

You can [clone this repo](https://github.com/kenpfowler/coding-challenge-web-server) for a server that already responds to health-check or configure your own to respond.

### 2. Setup the load balancer

Suppose you're running 3 servers on localhost:8081,8082,8083

You can use the following command to configure the load balancer to monitor these servers and distribute traffic amongst them:

```sh
python ./program.py --servers localhost:8081,localhost:8082,localhost:8083
```

It should respond with the following:

```
2024-11-08 18:19:41,497 - INFO - server listening on localhost:8080
2024-11-08 18:19:41,498 - INFO - performing health check on the following server localhost:8081
2024-11-08 18:19:41,498 - INFO - performing health check on the following server localhost:8082
2024-11-08 18:19:41,498 - INFO - performing health check on the following server localhost:8083
2024-11-08 18:19:41,498 - INFO - the following host is up localhost:8081
2024-11-08 18:19:41,499 - INFO - the following host is up localhost:8082
2024-11-08 18:19:41,499 - INFO - the following host is up localhost:8083
```

### 3. Send a request to the load balancer

Use the curl or your browser to send a request. The request will be handled by one of your servers in a [round robin](https://www.vmware.com/topics/round-robin-load-balancing).

```sh
curl http://localhost:8080
```

### 4. shut down the load balancer

Press Control + C to shut down the load balancing server. It should respond with the following:

```
2024-11-08 18:18:43,697 - INFO - gracefully shutting down server
2024-11-08 18:18:43,697 - INFO - server shutdown complete
```
