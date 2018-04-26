# Consumers
Consumers are an essential part of nerodia.
Once an update event is received, it is dispatched to all
available consumers, which will then inform their respective
platforms about the received update.

In order for this to work, consumers need to implement a common API.
This document describes that API to allow users to easily implement
their own consumers.


## Basic Structure
At its core, a consumer is just a class.

* abstract base class for consumers
