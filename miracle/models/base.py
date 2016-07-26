from sqlalchemy.ext.declarative import declarative_base


class BaseModel(object):
    pass

Model = declarative_base(cls=BaseModel)
