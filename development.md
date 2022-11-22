# Useful commands

# Start local environment

```bash
docker-compose up --build -d && docker-compose exec main bash
```

All other commands are executing in this shell

# Render package

Simple:

```bash
./build.sh
```

Render using dev version:

```bash
DEV=1 ./build.sh
```

# Prettify

```bash
isort --profile black . && black .
```

pyflakes:

```bash
# ignore false warning
pyflakes . | grep -v inner_context
```

# Build docs

```bash
cd docs
make html
```

Background server serves docs on http://localhost:8080
