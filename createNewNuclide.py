# -*- coding: utf-8  -*-
import pywikibot
import csv

site = pywikibot.Site('wikidata', 'wikidata')
repo = site.data_repository()


def get_item(item_id):
    item = pywikibot.ItemPage(repo, item_id)
    item.get()
    return item

def create_item(site, data):
    new_item = pywikibot.ItemPage(site)

    new_item.editEntity(data, summary=u'set labels, descriptions, aliases')
        
    return new_item.getID()

def getIsotopeOfQID():

    isotopeOf = {}
    with open("listIsotopeOf.csv") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            QID, longName = row
            beg = longName.find(" of ")
            name = longName[beg+4:]
            isotopeOf[name] = QID
            
    return isotopeOf

def getElementNameQID():

    elementQID = {}
    with open("listElementEn.csv") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            QID, name, Z = row
            elementQID[name] = QID
            
    return elementQID

def process_data(filename):
    isotopeOf = getIsotopeOfQID()
    elementQID = getElementNameQID()
    
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            nameEn, nameFr, elementEn, elementFr, Z, N, massExcess, massExcessUnc, massExcessEst, bindingEnergy, bindingEnergyUnc, bindingEnergyEst, atomicMass, atomicMassUnc, atomicMassEst = row
            print("Treating "+nameFr+"...")
            data = {"labels": {"en": nameEn, "fr": nameFr},
                    "descriptions": {"en": "isotope of " + elementEn, "fr": "isotope du " + elementFr}}
            new_item_id = create_item(site, data)
            item = get_item(new_item_id)

            #Adding P31
            claim = pywikibot.Claim(repo, u'P31')
            target = pywikibot.ItemPage(repo, isotopeOf[elementEn])
            claim.setTarget(target)
            item.addClaim(claim, bot=True, summary=u'Adding instance')

            #Adding P279
            claim = pywikibot.Claim(repo, u'P279')
            target = pywikibot.ItemPage(repo, elementQID[elementEn])
            claim.setTarget(target)
            item.addClaim(claim, bot=True, summary=u'Adding subclass')

            #Adding Z
            claim = pywikibot.Claim(repo, u'P1086') #Z
            wb_quant = pywikibot.WbQuantity(int(Z),error="0")
            claim.setTarget(wb_quant)
            item.addClaim(claim, bot=True, summary="Adding atomic number claim.")
    
            #Adding N
            claim = pywikibot.Claim(repo, u'P1148') #N
            wb_quant = pywikibot.WbQuantity(int(N), error="0")
            claim.setTarget(wb_quant)
            item.addClaim(claim, bot=True, summary="Adding atomic number claim.")

process_data('nuclearData2Tmp.csv')
