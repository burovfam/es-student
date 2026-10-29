#include "pico/stdlib.h"
#include "hardware/gpio.h"

const uint LED_PIN = 25;

int main()
{
    stdio_init_all(); // Инициализация USB и UART для вывода

    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    while (1)
    {
        // Читаем символ из USB
        int c = getchar_timeout_us(100000); // Ждём 100 мс

        if (c == '1')
        {
            gpio_put(LED_PIN, 1);
            printf("LED ON\n");
        }
        else if (c == '0')
        {
            gpio_put(LED_PIN, 0);
            printf("LED OFF\n");
        }
    }
}