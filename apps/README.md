# CLO5 APPS
Microservices

# Usage
Setup:
```bash
cp .env.example .env
code .env # ou vim .env
docker compsoe build # optional
```

Demarrage:
```bash
docker-compose up -V # -d # detach
# complete command :
docker-compose up --renew-anon-volumes # --detach
```

Stop:
```bash
docker-compose down
# stop with removing volumes and local images
docker-compose down --volumes --remove-orphans --rmi local
```

Production
```bash
docker-compose up -d --scale web=3
```

### Logging level configuration

> To configure logging verbosity, here's how to do it in the different services:

| Service to log | Description on how to edit logging verbosity |
| --- | --- |
| `APIs` | _[From official doc](https://flask.palletsprojects.com/en/1.1.x/quickstart/#logging): The attached logger is a [standard logging Logger](https://docs.python.org/3/howto/logging.html)_.<br />Available levels configurable in `APP_LOG_LEVEL` env variable: `CRITICAL`:50, `ERROR`:40, `WARNING`:30, `INFO`:20, `DEBUG`:10 and `NOTSET`:0. Configuration is done in .env file through `APP_DEBUG` variable (`True`/`False`) and `APP_LOG_LEVEL` variable.|
| `MongoDB` | Once you started a MongoDB shell, head to the database you want to use (using `use databaseName` command) and use `db.setLogLevel()` function. [function offical documentation](https://www.mongodb.com/docs/manual/reference/method/db.setLogLevel/). |

_For convenience, use only levels betweeen 4/40 (Error) and 1/10 (Debug)._ 

## Development notes
The docker compose already does everything.

However if you don't want to run the api via docker but your machine just comment out the API part in compose and follow the instructions in the respective api folder.

For convenience, it's best to leave the db in the compose docker and launch it using the compose docker but it is possible to do it manually. You will need to manually include the potential db files, including `init-mongo.sh`

### DB:
The DB is in a linux docker container which is launched automatically with the `docker compose` command since it is part of the `docker-compose.yml` stack.

To access there's are 2 ways:
- **CLI**:

In another terminal, ideally in the same folder where the `docker compose` commands were run:
```bash
# admin/root access
docker compose exec db mongo admin -u mlsRoot -p mlsSecureP
# db user access
# same command with .env credentials
# CLI/Docker access
docker compose exec db mongo
```

- **Graphic**:
[Install MongoDB Compass](https://www.mongodb.com/products/compass).

Once compass has been installed and launched, simply copy the line displayed in the terminal into the docker compose logs:
```bash
DEBUG [db]: Mongo URI: [mongodb://cloUser:cloUserPassword@db:27017/clo]
```
Be careful to replace the host after the `@` from `db` to `localhost`. Also check the `?authSource=admin` end parameter and replace it with `?authSource=clo` or vice versa.

- **mongo-express** with docker compose:
In `docker-compose.yml`, uncomment the `db-express` block and restart the stack.

The service is available at [localhost:8081](http://localhost:8081) and the credentials are in the `.env` file.

## Useful data
### Debug VSCode Python/API
> Edit the API service definition in `docker-compose.yml`:
```yaml
    # from this
    command: app.py # prod
    # to this
    command: "-m debugpy --listen 0.0.0.0:5678 app.py" # debug
```
> Redeploy the stack, VSCode debugger is already configured, start it from the sidebar.

### APIs docs

> The documentation (OpenAPI/Swagger) is accessible in the /docs path of the apis.

| API | Port | URL |
| --- | --- | --- |
| `iamSvc` | 5051 | http://localhost:5051/docs |
| `catalogSvc` | 5052 | http://localhost:5052/docs |
| `bookingAndBillingSvc` | 5053 | http://localhost:5053/docs |
| `mailingSvc` | 5054 | http://localhost:5054/docs |

### MongoDB Documentation
> [**A cheatsheet of mongo** is available on their website](https://www.mongodb.com/developer/quickstart/cheat-sheet/) and also [**an excellent guide** for people who come from mysql](https://gist.github.com/yannvanhalewyn/dd35a847896b2ef9f688).

### Clean docker images:
```bash
docker-compose down --rmi local
# ou
docker rmi $(docker images -f "dangling=true" -q)
```

### Container with `-it` option in compose:
> Add these values to the service definition in `docker-compose.yml`:
```yaml
    stdin_open: true # docker run -i
    tty: true        # docker run -t
```

### Flask colored logs _(experimental)_
> It is possible to have colored logs for flask as we use `coloredlogs` module. All you need to do is in  `docker-compose.yml` enable TTY:
```yaml
# [...]
    command: app.py
    tty: true        # docker run -t (experimental)
    volumes:
      - ./api:/api
# [...]
```
> However [there's a bug that prevents you from viewing the logs in the terminal](https://github.com/docker/compose/issues/2231) using the `docker compose up` option, but you can use the `docker compose logs -f` command in a separate terminal.

## FAQ:
### Proxy issues:

> If you're behind a corporate proxy, be sure to export `http_proxy` and `https_proxy` it in your env so the containers can download dependencies without issues.

### `Error: error:0308010C:digital envelope routines::unsupported`:

> Use `npm run start-legacy` instead of `npm run start` or downgrade to `node:16`.

## Contributors, license and etc:
On repo main [README.md](../README.md).