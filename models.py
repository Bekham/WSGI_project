import sqlite3



class UsersModel:
    columns = {
        'id': 'INTEGER PRIMARY KEY',
        'name': 'TEXT UNIQUE',
        'good_sub': 'TEXT',
        'admin': 'BOOL'
    }


class GoodsModel:
    columns = {
        'id': 'INTEGER UNIQUE',
        'name': 'TEXT UNIQUE',
        'description': 'TEXT',
        'image': 'TEXT',
        'discount': 'REAL',
        'cost': 'REAL',
        'visible': 'BOOL',
        'category': 'TEXT',
        'notify_users': 'TEXT'
    }


class CategorysModel:
    columns = {
        'id': 'INTEGER UNIQUE',
        'name': 'TEXT UNIQUE',
        'description': 'TEXT',
        'visible': 'BOOL',
        'category': 'TEXT',
        'goods': 'TEXT'
    }


connection = sqlite3.connect('patterns.sqlite')
cursor = connection.cursor()

class ModelFactory:
    """Регистрация моделей"""
    types = {
        'users': UsersModel,
        'goods': GoodsModel,
        'categorys': CategorysModel
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_):
        return cls.types[type_]()

    @staticmethod
    def migrate():

        for type_ in ModelFactory().types.keys():
            model = ModelFactory().create(type_)
            columns = ""
            for column_name, column_params in model.columns.items():
                columns += f"{column_name} {column_params},"
            table = f"CREATE TABLE IF NOT EXISTS {type_}({columns[:-1]})"
            cursor.execute(table)
            connection.commit()

    @staticmethod
    def get_model(name):
        return ModelFactory.types[name](tablename=name,
                                        connection=connection)