# noinspection SpellCheckingInspection
class Games(object):
    DIRT_RALLY = {
        'name': 'Dirt Rally',
        'db_file': 'dirt_rally.db'
    }
    DIRT_4 = {
        'name': 'Dirt 4',
        'db_file': None
    }
    DIRT_SHOWDOWN = {
        'name': 'Dirt Showdown',
        'db_file': None
    }
    F1_2015 = {
        'name': 'F1 2015',
        'db_file': None
    }
    F1_2016 = {
        'name': 'F1 2016',
        'db_file': None
    }
    F1_2017 = {
        'name': 'F1 2017',
        'db_file': None
    }
    GRID_AUTOSPORT = {
        'name': 'GRID Autosport',
        'db_file': None
    }
    all_games = [
        DIRT_RALLY,
        DIRT_4,
        DIRT_SHOWDOWN,
        F1_2015,
        F1_2016,
        F1_2017,
        GRID_AUTOSPORT
    ]

    def __iter__(self):
        return iter(self.all_games)
