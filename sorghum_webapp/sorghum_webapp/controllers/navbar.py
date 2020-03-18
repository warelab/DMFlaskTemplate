import logging
app_logger = logging.getLogger("sorghumbase")

def make_menu(label, style='simple'):
    return { 'label':label, 'style':style, 'links':[] }

def add_link(menu, label, link):
    menu['links'].append({'label':label, 'link':link})

def news():
    menu = make_menu('News')
    add_link(menu, 'News', '/posts?categories=news')
    add_link(menu, 'Events', '/events')
    add_link(menu, 'Publications', '/publications')
    return menu

def community():
    menu = make_menu('Community')
    add_link(menu, 'Research Notes', '/posts?categories=researchnote')
    add_link(menu, 'People', '/people')
    add_link(menu, 'Mailing List', '/mailing_list')
    return menu

def resources():
    menu = make_menu('Resources')
    add_link(menu, 'Links', '/resource_links')
    add_link(menu, 'Tools', '/posts?categories=tools')
    add_link(menu, 'Tutorials', '/posts?categories=tutorials')
    add_link(menu, 'Projects', '/projects')
    return menu

def about():
    menu = make_menu('About')
    add_link(menu, 'Mission Statement', '/mission-statement')
    add_link(menu, 'FAQ', '/faq')
    add_link(menu, 'Contact Us', '/contact')
    return menu

def germplasms():
    ref = make_menu('Reference')
    add_link(ref, 'BTx623 - PI 564163', '/accession/btx623')
    add_link(ref, 'Rio - PI 651496', '/accession/rio')

    # sap = make_menu('SAP')
    # add_link(sap, 'RTx430 - PI 655996 ', '#')
    # add_link(sap, 'RTx436 - PI 561071 ', '#')
    # add_link(sap, 'BTx2783 - PI 656001 ', '#')
    #
    # bap = make_menu('BAP')
    # add_link(bap, 'Chinese Amber - PI 22913 ', '#')
    # add_link(bap, 'Grassl - PI 154844 ', '#')
    # add_link(bap, 'PI 229841 ', '#')
    # add_link(bap, 'PI 297155 ', '#')
    # add_link(bap, 'PI 506069 ', '#')
    # add_link(bap, 'PI 510757 ', '#')
    # add_link(bap, 'PI 655972 ', '#')
    #
    # other = make_menu('Other')
    # add_link(other, 'Leoti - PI 641825 ', '#')
    # add_link(other, 'PI 329311 ', '#')
    # add_link(other, 'PI 300119 - S. Verticiliflorum ', '#')

    association = make_menu('Association Panels')
    add_link(association, 'World Core Collection', '/population/world-core')
    add_link(association, 'Mini Core Collection', '/population/mini-core')
    add_link(association, 'SAP', '/population/sap')
    add_link(association, 'BAP', '/population/bap')
    add_link(association, 'Nigerian Diversity Panel', '/population/nigeria-div')

    TIL = make_menu('TILLING Populations')
    add_link(TIL, 'Xin EMS', '/population/xin-ems')
    add_link(TIL, 'Weil EMS', '/population/weil-ems')

    Other = make_menu('NAM populations')
    add_link(Other, 'Klein BC-NAM', '/population/klein-nam')
    add_link(Other, 'Kresovich NAM', '/population/kresovich-nam')
    add_link(Other, 'Mace BC-NAM', '/population/mace-nam')

    menu = make_menu('Germplasms','mega')
    # menu['categories'] = [ref,sap,bap,other]
    menu['categories'] = [ref, association, TIL, Other]

    return menu

def navbar_template(activemenu='NA'):
    return {'navbar': [news(), community(), germplasms(), resources(), about()],'activemenu':activemenu}
