# Kamal


### Installation and Setup

#### Non Docker setup
* Install ruby
    ```
    brew install ruby
    ```
    If you are on mac then https://mac.install.guide/ruby/13
* Set this in .zsh
    ```
    export GEM_HOME="$HOME/.gem"
    ```
* Install kamal
    ```
    gem install kamal
    ```
* Specify the config
    - Add the registry. In our case we will use docker hub
    - Add the builder arch
    - install buildx . If not available locally
    - Leran how secrets are maintained in kamal
    - Check if your registry is reachable

* Run kamal setup
    ```
    kamal setup
    ```
    Now this will make sure to set up the server with docker container. Note that you need root access
* Run `kamal deploy` for deploying after setup
* Sometimes due to errors kamal is bound to get deploy lock run `kamal lock release`


* Run in this order kamal
    - kamal server bootstrap  -c kamal/accessories/config/deploy.yml
    -  export $(cat .env | xargs) [To get values to in env to log in to docker deployment]
    - kamal accessory boot redis  -c kamal/accessories/config/deploy.yml
    - kamal accessory boot db  -c kamal/accessories/config/deploy.yml
    - kamal deploy -r web  -c kamal/sync-app/config/deploy.yml
    - kamal deploy -r web  -c kamal/async-app/config/deploy.yml
    # Remove
    - kamal remove -c kamal/sync-app/config/deploy.yml



Points to discuss:
* Evolution of deployment for hobby projects. (1.5)
* Async Django and what you can do with it (1.5)
* Streaming SSE and the use for notification (2)
* Introducing classic django deployment when everything was sync, Heroku , fly.io , vps , dokku, docker-swarm, dokploy.com (5)
* Introducing kamal and some basics like why was it formed why should it be use , a whole trend of going on prem. What can we learn from it and use it(5)
* Showing the config file and what can are the various options (5)
 - hosts
 - envs
 - accessories
 - kamal proxy and how it communicates with other docker pods and SSL
 - secrets and how do we store it
 - structure of how config should be
 - health checks
* Describe some django specific config needed for both sync and async apps with different subdomain same domain to work (2)
  - like CSR coookie, session cookie domain things in the env.
  - when dealing with sub domains the cookie origin should be something to take good care of
* Sample django application deployment can we show live demo ? (if there is some time ?)