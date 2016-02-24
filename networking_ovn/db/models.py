import sqlalchemy as sa
from neutron.db import model_base

class Sfi(model_base.BASEV2):
    #
    # Table to store SFI Info
    #
    __tablename__='sfis'
    name = sa.Column(sa.String(255), primary_key=True, nullable=False)
    id = sa.Column(sa.Integer)
