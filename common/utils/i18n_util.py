import gettext


def i18n_config():
    zh_trans = gettext.translation('i18n_config', localedir='locales', languages=['zh_CN'])
    zh_trans.install()
    return zh_trans.gettext
