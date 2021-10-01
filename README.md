# Smart speaker with Raspberry Pi (Raspeaker)

I started this project especially to upgrade my Logitech Z906 sound system, 
but I found the solution to be quite versatile. So when I upgraded another
sound system I had lying around, I decided to abstract this project from
the underlying hardware.

So this piece of software can be used to create a Raspberry Pi based speaker,
or to upgrade an existing sound system. It is especially useful for integrating
an existing control panel (like buttons, IR, rotary encoder, ...).

The application mainly consists of more or less hardware-specific modules. Some
can be reused in arbitrary cases, while others are for a single specific device.
The idea is to provide a simple platform, that you can easily configure use YAML 
and extend using python.

## Installation

Install using: 

```
curl -sL https://raw.githubusercontent.com/dominikberse/raspeaker/master/install.sh | sh
```

## Configuration

There are configuration files available for the projects I did myself, but it 
is very unlikely that you will be able to use them as they are. However, they
will serve as a good starting point.

TODO: Documentation

## Modules

Currently available modules:
- GPIO button
- Analog buttons
- Rotary encoder
- Adafruit ADS1015
- Web API
- IR receiver

Logitech Z906
- Main unit controller
- Control panel

TODO: Documentation

## Web API

The `api` module provides a Flask webservice, which can be used to control the sound
system remotely. It can also be used to integrate the system into other services 
(like smart home).

TODO: Documentation