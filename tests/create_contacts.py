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


def add_random_contact_bits(client, fake):
    payload = client.get("/api/personas/list")
    personas = payload.main_table()

    corporate_types = ["email_addresses", "urls", "phone_numbers", "street_addresses"]
    personal_types = ["email_addresses", "phone_numbers", "street_addresses"]

    for _ in range(30):
        persona = random.choice(personas.rows)

        btlist = corporate_types if persona.corporate_entity else personal_types
        bt = random.choice(btlist)
        payload = client.get(f"/api/persona/{persona.id}/bit/new", bit_type=bt)
        bits = payload.main_table()
        row = bits.rows[0]

        row.name = "thing"
        if bt == "email_addresses":
            row.email = fake.ascii_email()
        elif bt == "phone_numbers":
            # row.number = fake.phone_number()
            row.number = "717-298-2911"
        elif bt == "urls":
            row.url = fake.uri()
            row.password = fake.password()
        elif bt == "street_addresses":
            row.address1 = fake.street_address()
            row.city = fake.city()
            row.state = fake.state()
            row.zip = fake.postcode()
            row.country = "USA"
        if random.random() < 0.1:
            row.memo = fake.text()

        client.put(
            f"/api/persona/{persona.id}/bit/{row.id}",
            files={"bit": bits.as_http_post_file()},
        )


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
