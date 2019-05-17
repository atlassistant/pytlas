Upcoming
===

In this library
---

- [ ] Remote training of the interpreter for when you have large training data and you are deploying pytlas on small devices

Big plans
---

If you wish to contribute, here is what I have in my head for this project :)

**pytlas** is a library and as such does not provide any end user interface (except the REPL). I've done some projects such as the [server](https://github.com/atlassistant/pytlas-server) and [mobile](https://github.com/atlassistant/pytlas-mobile) to expose this library over websockets and connect to it using a mobile client but there's still many stuff to do.

The **big plan** is to provide a `pytlas-broker` which will exposes agents via MQTT to provide a better integration with other IoT systems using simple topics listed below.

This broker project will expose two entry points: `BrokerServer` and `BrokerClient`. Discovery for the MQTT server should be possible using [avahi](https://gist.github.com/marciogranzotto/20e45b83bbcca11e267708b10507c54a).

### Client to Server

- `atlas/<uid>/ping`: Creates an agent if needed
- `atlas/<uid>/parse`: Ask pytlas to parse a raw message

### Server to Client

- `atlas/<uid>/pong`: Reply to ping requests when the agent is ready
- `atlas/<uid>/ask`: Ask something to the user
- `atlas/<uid>/answer`: Answer something to the user
- `atlas/<uid>/context`: Switched to a particular context
- `atlas/<uid>/thinking`: Started processing a message
- `atlas/<uid>/done`: Stopped processing a message

Once that's done, I've got some work in progress for a pod on a RPI which always listen using [snowboy](https://snowboy.kitt.ai/), do some STT using Google Cloud Speech for now (waiting for DeepSpeech...), push the transcript to pytlas and reply back using svox pico. Sources will be available soon, I just need to refactor a little bit.