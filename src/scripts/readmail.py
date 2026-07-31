# readmail.py
# Script to read email and write relevant fields to PostgreSQL quarantine database
from pathlib import Path
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_to_datetime
import psycopg

# Function for extracting body text using Python's email library
def get_plaintext_body(message):
	if message.is_multipart():
		for part in message.walk():
			if (
				part.get_content_type() == "text/plain"
				and "attachment" not in str(part.get("Content-Disposition", ""))
			):
				try:
					return part.get_content().strip()
				except Exception:
					payload = part.get_payload(decode=True)
					charset = part.get_content_charset() or "utf-8"
					return payload.decode(charset, errors="replace").strip()
	else:
		try:
			return message.get_content().strip()
		except Exception:
			payload = message.get_payload(decode=True)
			charset = message.get_content_charset() or "utf-8"
			return payload.decode(charset, errors="replace").strip()

	return ""

# Function for importing email into PostgreSQL DB
# Schema:
#		CREATE TABLE emails (
#			id SERIAL PRIMARY KEY,
#			sender TEXT NOT NULL,
#			datetime TIMESTAMPTZ,
#			text TEXT NOT NULL
#		);
def import_email(email_path, conn):
	with conn.cursor() as cur:

		for path in Path(email_dir).glob("*"):

			if not path.is_file():
				continue

			with open(path, "rb") as f:
				msg = BytesParser(policy=policy.default).parse(f)

			# Parse sender address
			sender = parseaddr(msg.get("From", ""))[1]

			# Convert to valid datetime
			date_str = msg.get("Date")
			try:
				dt = parsedate_to_datetime(date_str) if date_str else None
			except Exception:
				dt = None

			subject = (msg.get("Subject") or "").strip()
			body = get_plaintext_body(msg)

			text = f"{subject} {body}".strip()

			cur.execute("INSERT INTO emails (sender, datetime, text) VALUES (%s, %s, %s)", (sender, dt, text))

	conn.commit()


if __name__ == "__main__":

	conn = psycopg.connect(
		host="localhost",
		dbname="mydb",
		user="postgres",
		password="password",
		port=5432,
	)

	import_email_directory("emails/", conn)

	conn.close()