import psycopg
from polling.core.security import hash_password

conn = psycopg.connect(
    host="localhost",
    dbname="voterdatabase",
    user="voterdatabase",
    password="password",
    port=5432,
)

try:
    with conn.cursor() as cursor:
        hashed = hash_password("Ndgdte653gd637")
        cursor.execute(
            """
            INSERT INTO users (
                name,
                username,
                password_hash,
                role,
                proof_reference,
                is_active,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (username) DO UPDATE
            SET password_hash = EXCLUDED.password_hash
            """,
            (
                "karunakaran",
                "karan",
                hashed,
                "admin",
                "license",
                True,
            ),
        )

        conn.commit()
        print("User inserted/updated successfully with hashed password")

except Exception as error:
    conn.rollback()
    print("Database error:", error)

finally:
    conn.close()
