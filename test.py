# somewhere in your addons, a throwaway test change
class TestModel(models.Model):
    _name = 'test.model'

    def do_thing(self):
        self.env.cr.execute("SELECT * FROM res_partner WHERE name = '%s'" % self.name)  # bad: raw SQL, string formatting
        x=1  # bad: no space around =, unused var