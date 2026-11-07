#pragma once

#include "pico/stdlib.h"
uint led_pin(void);
void led_init(void);
void led_set(bool on);
void led_toggle(void);
bool led_is_on(void);
