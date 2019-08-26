from sure import expect
from pytlas.handling.localization import TranslationsStore
from pytlas.handling.skill import intent, meta, GLOBAL_HANDLERS, GLOBAL_METAS, \
    HandlersStore, MetasStore, Meta, Setting


class TestMeta:

    def test_it_should_be_instantiable(self):
        m = Meta('lights',
                 description='Some lighting skill',
                 author='Julien LEICHER',
                 homepage='https://julien.leicher.me',
                 media='https://somepic',
                 version='1.0.0')

        expect(m.name).to.equal('lights')
        expect(m.description).to.equal('Some lighting skill')
        expect(m.author).to.equal('Julien LEICHER')
        expect(m.version).to.equal('1.0.0')
        expect(m.homepage).to.equal('https://julien.leicher.me')
        expect(m.media).to.equal('https://somepic')

    def test_it_should_convert_settings_strings_to_setting_object_if_needed(self):
        m = Meta('lights', settings=['lights.default', Setting(
            'lights', 'other', int, 'A description')])

        expect(m.settings).to.have.length_of(2)
        expect(m.settings[0]).to.be.a(Setting)
        expect(m.settings[0].section).to.equal('lights')
        expect(m.settings[0].name).to.equal('default')

        expect(m.settings[1]).to.be.a(Setting)
        expect(m.settings[1].section).to.equal('lights')
        expect(m.settings[1].name).to.equal('other')
        expect(m.settings[1].type).to.equal(int)
        expect(m.settings[1].description).to.equal('A description')

    def test_it_should_provide_eq_operator(self):
        a = Meta('aname', description='a desc',
                 version='1.0.0', author='John doe')
        b = Meta('anothername', description='another desc',
                 version='1.1.1', author='Bob')
        expect(a).to_not.equal(b)

        b.name = a.name
        expect(a).to_not.equal(b)

        b.description = a.description
        expect(a).to_not.equal(b)

        b.version = a.version
        expect(a).to_not.equal(b)

        b.author = a.author
        expect(a).to.equal(b)

    def test_it_should_print_correctly(self):
        m = Meta('lights',
                 description='Some lighting skill',
                 author='Julien LEICHER',
                 homepage='https://julien.leicher.me',
                 media='https://somepic',
                 version='1.0.0',
                 settings=[Setting('lights', 'default')])

        expect(str(m)).to.equal("""lights - v1.0.0
  description: Some lighting skill
  homepage: https://julien.leicher.me
  author: Julien LEICHER
  settings: lights.default (str)
""")


class TestHandlers:

    def teardown(self):
        GLOBAL_HANDLERS.reset()

    def test_it_should_register_handlers_correctly(self):
        s = HandlersStore()

        def on_lights_on():
            pass

        s.register('lights_on', on_lights_on)

        expect(s._data).to.equal({
            'lights_on': on_lights_on,
        })

    def test_it_should_register_with_the_decorator_in_the_provided_store(self):
        s = HandlersStore()

        @intent('an_intent', store=s)
        def a_handler(r):
            return r.agent.done()

        expect(s._data).to.equal({
            'an_intent': a_handler,
        })

    def test_it_should_register_with_the_decorator_in_the_global_store(self):
        @intent('another_intent')
        def another_handler(r):
            return r.agent.done()

        expect(GLOBAL_HANDLERS._data).to.equal({
            'another_intent': another_handler,
        })

    def test_it_should_retrieve_an_handler_with_an_intent(self):
        s = HandlersStore()

        @intent('an_intent', store=s)
        def a_handler(r):
            return r.agent.done()

        @intent('another_intent', store=s)
        def another_handler(r):
            return r.agent.done()

        expect(s.get('an_intent')).to.equal(a_handler)
        expect(s.get('another_intent')).to.equal(another_handler)


class TestMetas:

    def teardown(self):
        GLOBAL_METAS.reset()

    def test_it_should_register_metas_correctly(self):
        s = MetasStore()

        def module_meta():
            pass

        s.register(module_meta, 'amodule')

        expect(s._data).to.equal({
            'amodule': module_meta,
        })

    def test_it_should_register_with_the_decorator_in_the_provided_store(self):
        s = MetasStore()

        @meta(store=s, package='amodule')
        def meta_handler():
            pass

        expect(s._data).to.equal({
            'amodule': meta_handler,
        })

    def test_it_should_register_with_the_decorator_in_the_global_store(self):
        @meta(package='amodule')
        def meta_handler():
            pass

        expect(GLOBAL_METAS._data).to.equal({
            'amodule': meta_handler,
        })

    def test_it_should_provides_all_meta(self):
        s = MetasStore()
        s.register(lambda _: {
            'name': _('my module'),
            'version': '1.0.0',
        }, package='mymodule')
        s.register(lambda _: {
            'name': _('a module'),
            'version': '1.0.0',
        }, package='amodule')

        expect(s.all('fr')).to.equal([
            Meta(name='my module', version='1.0.0'),
            Meta(name='a module', version='1.0.0'),
        ])

    def test_it_should_provides_all_meta_and_translate_them_with_a_translations_store(self):
        t = TranslationsStore({
            'mymodule': {'fr': lambda: {'my module': 'mon module'}},
            'amodule': {'fr': lambda: {'a module': 'un module'}},
        })
        s = MetasStore(translations_store=t)
        s.register(lambda _: {
            'name': _('my module'),
            'version': '1.0.0',
        }, package='mymodule')
        s.register(lambda _: {
            'name': _('a module'),
            'version': '1.0.0',
        }, package='amodule')

        expect(s.all('fr')).to.equal([
            Meta(name='mon module', version='1.0.0'),
            Meta(name='un module', version='1.0.0'),
        ])

    def test_it_should_retrieve_a_particular_package_meta(self):
        s = MetasStore()
        s.register(lambda _: {
            'name': _('my module'),
            'version': '1.0.0',
        }, package='mymodule')
        s.register(lambda _: {
            'name': _('a module'),
            'version': '1.0.0',
        }, package='amodule')

        expect(s.get('amodule', 'fr')).to.equal(
            Meta(name='a module', version='1.0.0'))
        expect(s.get('anunknownmodule', 'fr')).to.be.none

    def test_it_should_retrieve_a_particular_package_meta_and_translate_it(self):
        t = TranslationsStore({
            'mymodule': {'fr': lambda: {'my module': 'mon module'}},
            'amodule': {'fr': lambda: {'a module': 'un module'}},
        })
        s = MetasStore(translations_store=t)
        s.register(lambda _: {
            'name': _('my module'),
            'version': '1.0.0',
        }, package='mymodule')
        s.register(lambda _: {
            'name': _('a module'),
            'version': '1.0.0',
        }, package='amodule')

        expect(s.get('mymodule', 'fr')).to.equal(
            Meta(name='mon module', version='1.0.0'))
        expect(s.get('amodule', 'fr')).to.equal(
            Meta(name='un module', version='1.0.0'))
