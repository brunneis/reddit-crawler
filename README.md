# reddit-crawler
This crawler scrapes all new submissions and comments posted on Reddit in real time. A topology is defined with three [Catenae](https://github.com/catenae) modules. The extracted texts can be retrieved on the Kafka topic `new_texts`.

## Standalone mode
In order to launch the crawler in standalone mode with its own Kafka broker execute the `start-all.sh` script.
