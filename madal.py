# test.py
class TestModel(models.Model):
    _name = 'test.model'

    def do_thing(self):
        self.env.cr.execute("SELECT * FROM res_partner WHERE name = '%s'" % self.name)
        x=1