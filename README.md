<img src="https://r2cdn.dstn.to/lanyard/logo.png" alt="Bracelet Logo" width="300"/>

# 🏷️ Expose your Yapin' presence to a RESTful API in less than 10 seconds

Bracelet is a service that makes it super easy to export your live Yapin' presence to an API endpoint (`api.bracelet.oriaxen.com/v1/users/:your_id`) (see below) for you to use wherever you want - for example, I use this to display what I'm listening to on Spotify on my personal website. It also acts as a globally-accessible realtime KV store which you can update from the Bracelet Yapin' bot or from the Bracelet API.

You can use Bracelet's API without deploying anything yourself - but if you want to self host it, you have the option to, though it'll require a tiny bit of configuration.

## Get started in < 10 seconds

Just [join this Yapin' server](https://www.yapin.gg/invite/bracelet) and your presence will start showing up when you `GET api.bracelet.oriaxen.com/v1/users/:your_id`. It's that easy.

## Table of Contents

- [Community Projects](#community-projects)
- [API Docs](#api-docs)
  - [Getting a user's presence data](#getting-a-user-s-presence-data)
  * [KV](#kv)
    - [Use cases](#use-cases)
    - [Limits](#limits)
    - [Getting an API Key](#getting-an-api-key)
    - [Setting a key->value pair](#setting-a-key--value-pair)
    - [Deleting a key](#deleting-a-key)
- [Quicklinks](#quicklinks)
- [Self-host with PM2](#self-host-with-pm2)
- [Showcase](#showcase)
- [Todo](#todo)

## Community Projects

The Bracelet community has worked on some pretty cool projects that allows you to extend the functionality of Bracelet. PR to add a project!

[bracelet.py](https://github.com/lecanact/bracelet.py) - Modern wrapper for the Bracelet API written in Python.\

## API Docs

#### Getting a user's presence data

`GET https://api.bracelet.oriaxen.com/v1/users/:user_id`

Example response:

```json
{
  "success": true,
  "data": {
    // Bracelet KV
    "kv": {
      "location": "Dover, DE"
    },
    "user": {
      "username": "leandre",
      "badges":[
      	"bot_dev",
      	"bug_hunter"
      ]
      "id": "USER_ID_HERE",
      "avatar_url": "https://files.yapper.website/avatars/AVATAR_HASH_HERE"
      "banner_url": "https://files.yapper.website/banners/BANNER_HASH_HERE"
    },
    "status": "online",
  }
}
```

### KV

The Bracelet KV is a a dynamic, real-time key->value store which is added to the Bracelet user API response.

#### Use cases

- Configuration values for your website
- Configuration values for Bracelet 3rd party projects
- Dynamic data for your website/profile (e.g. current location)

#### Limits

1. Keys and values can only be strings
2. Values can be 30,000 characters maximum
3. Keys must contain only letters, numbers, and underscores (a-zA-Z0-9_) and be at most 255 characters long
4. Your user can have a maximum of 512 key->value pairs linked

#### Getting an API Key

> [!CAUTION]
> If you just want to display your Yapin' presence on a website or read it through the API, you do not need an API key.
> You only need an API key to manage custom key/value data in your Bracelet KV store. Keep it private and never include it in frontend code.

DM the Yapin' bot ([`Bracelet#5676`](https://www.yapin.gg/bot/BOT_ID_HERE)) with `/apikey` or use it in the [Server](https://www.yapin.gg/invite/bracelet) to get your API key.

When making Bracelet KV API requests, set an `Authorization` header with the API key you received from the Bracelet bot as the value.

#### Setting a key->value pair

##### Yapin'

`/set key:<key> value:<value>`

##### HTTP

`PUT https://api.bracelet.oriaxen.com/v1/users/:user_id/kv/:key`
The value will be set to the body of the request. The body can be any type of data, but it will be string-encoded when set in Bracelet KV.

#### Setting multiple key->value pairs

##### Yapin'

Not yet implemented

##### HTTP

`PATCH https://api.bracelet.oriaxen.com/v1/users/:user_id/kv`
The user's KV store will be merged with the body of the request. Conflicting keys will be overwritten. The body must be keyvalue pair object with a maximum depth of 1.

#### Deleting a key

##### Yapin'

`/del key:<key>`

##### HTTP

`DELETE https://api.bracelet.oriaxen.com/v1/users/:user_id/kv/:key`

## Quicklinks

Bracelet quicklinks allow you to easily access resources from Yapin', such as profile pictures, and banners.

### User Icons

`https://api.bracelet.oriaxen.com/<id>.<file_type>`
Where `id` is the Yapin' UserID you want the icon of. `file_type` can be one of: `png`, `gif`, `webp`, `jpg`, or `jpeg`

## Self-host with PM2

Build the Docker image by cloning this repo and running:

```bash
# The latest version is already on the docker hub, you can skip this step unless you would like to run a modified version.
git clone https://github.com/our-websites/bracelet \
cd bracelet \
pm2 start
```

You'll be able to access the API using **port 5119**.

You also need to create a Yapin' bot and use its token above.

Create a bot here: https://www.yapin.gg -> Settings -> Developer

If you'd like to run Bracelet with `docker-compose`, that will be coming soon maybe? If you'd like to open a PR that adds support for docker and docker compose feel free!

Note, that you're **hosting a http server, not https**. You'll need to use a **reverse proxy** if you want to secure your API endpoint.

## Showcase

Below is a curated selection of websites using Bracelet right now, check them out! Some of them will only show an activity when they're active.
- [example.com](https://example.com)
