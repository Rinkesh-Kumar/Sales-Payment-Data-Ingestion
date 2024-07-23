# GCP Pub/Sub and Cassandra Integration Project

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)


## Overview
This project demonstrates the integration between GCP Pub/Sub and Apache Cassandra using Python. It involves reading and writing data to Pub/Sub topics (`sales` and `payment`), processing this data, and storing it in Cassandra. If a `payment` record does not have a corresponding `sales` record in Cassandra, it is moved to a Dead Letter Queue (DLQ) Pub/Sub topic.

## Architecture
- **GCP Pub/Sub**: Manages real-time data streams for `sales`, `payment`, and `DLQ`.
- **Apache Cassandra**: Stores sales and payment data.
- **Python**: Used for implementing the producers and consumers.


