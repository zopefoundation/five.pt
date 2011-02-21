import patches


def initialize(site):
    import chameleon.config

    if chameleon.config.EAGER_PARSING:
        import gc

        # this only deals with the page template classes provided by
        # Zope, as Chameleon's classes are aware of the eager parsing
        # flag
        from zope.pagetemplate.pagetemplatefile import PageTemplateFile
        from five.pt.pagetemplate import BaseTemplateFile

        for template in (x for x in gc.get_objects()
                         if isinstance(x, PageTemplateFile)):

            inst = BaseTemplateFile(template.filename)
            inst.parse()
