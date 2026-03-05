## Run Alembic Migrations

### Configuration

```bash
cp alembic.ini.example alembic.ini
```

- Update the `alembic.ini` with your database credentials (`sqlalchemy.url`)

### (Optionals) Create a new migrations

```bash
alembic revision --autogenerate -m "Add ..."
```

### Updgrade the DataBase

```bash
alembic upgrade head
```
