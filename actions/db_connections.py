import psycopg2
import sqlalchemy

from actions.db_credentials import USER, PASSWORD, SERVER, PORT, DATABASE

SQA_CONN_STR = f"postgresql://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DATABASE}"

SQA_CONN_PUB_ENGINE = sqlalchemy.create_engine(SQA_CONN_STR,
                                               connect_args={'options': '-csearch_path=public'})
SQA_CONN_PUB = SQA_CONN_PUB_ENGINE.connect()

PSY_CONN_PUB = psycopg2.connect(
    host=SERVER,
    port=PORT,
    database=DATABASE,
    user=USER,
    password=PASSWORD,
    )