import random
import faker
import tools


def create_corp_entity(client, fake):
    payload = client.get("/api/persona/new")
    persona = payload.named_table("persona")
    entity = persona.rows[0]
    entity.corporate_entity = True
    entity.l_name = fake.company()

    client.put(
        f"/api/persona/{entity.id}", files={"persona": persona.as_http_post_file()}
    )

    payload = client.get(f"/api/persona/{entity.id}")
    name = payload.named_table("persona").rows[0].entity_name
    print(f"Added corp entity {name}")


def create_personal_entity(client, fake):
    payload = client.get("/api/persona/new")
    persona = payload.named_table("persona")
    entity = persona.rows[0]
    entity.corporate_entity = False
    entity.l_name = fake.last_name()
    entity.f_name = fake.first_name()
    if random.random() < 0.1:
        entity.title = fake.prefix()
    if random.random() < 0.1:
        entity.organization = fake.company()

    client.put(
        f"/api/persona/{entity.id}", files={"persona": persona.as_http_post_file()}
    )

    payload = client.get(f"/api/persona/{entity.id}")
    name = payload.named_table("persona").rows[0].entity_name
    print(f"Added personal entity {name}")


def main():
    pass


def outer(f):
    creds = {"username": "george sales", "password": "pigeon"}
    with tools.lms_std_client(creds) as client:
        fake = faker.Faker()
        for _ in range(10):
            f(client, fake)


if __name__ == "__main__":
    main()
